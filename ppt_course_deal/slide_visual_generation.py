"""工作台「生成全新 PPT 画面」：使用与口播稿优化相同的 transcript_rewrite API，调用 OpenAI 兼容文生图。"""

from __future__ import annotations

import base64
import json
import logging
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_IMAGE_MODEL = "gpt-image-2"
DEFAULT_SIZE = "1792x1024"
MAX_PROMPT_CHARS = 4000


def resolve_images_generations_url(api_base: str) -> str:
    """与 ``resolve_chat_completions_url`` 同理，指向 ``…/v1/images/generations``。"""
    base = (api_base or "").strip().rstrip("/")
    if not base:
        return ""
    lower = base.lower()
    if lower.endswith("/images/generations"):
        return base
    if lower.endswith("/v1"):
        return f"{base}/images/generations"
    return f"{base}/v1/images/generations"


def build_slide_visual_prompt(slide: dict[str, Any]) -> str:
    """由解析页 meta 拼默认提示词（中文教学幻灯片配图）。"""
    title = (slide.get("title") or "").strip()
    text = (slide.get("text") or "").strip().replace("\r\n", "\n")
    if len(text) > 1200:
        text = text[:1200] + "…"
    parts = [
        "生成一张 16:9 横版教学课件配图，风格清晰专业、适合中文在线课程，配色稳重，避免低俗或与课件无关的装饰。",
        "画面中可适当包含简洁图示或排版感，但不要生成密密麻麻的小字正文。",
    ]
    if title:
        parts.append(f"本页主题标题：{title}")
    if text:
        parts.append(f"内容要点摘录（供理解语境）：\n{text}")
    raw = "\n".join(parts)
    if len(raw) > MAX_PROMPT_CHARS:
        return raw[: MAX_PROMPT_CHARS - 1] + "…"
    return raw


def _post_json(url: str, headers: dict[str, str], body: dict[str, Any], timeout: int = 180) -> dict[str, Any]:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        err_body = ""
        try:
            err_body = e.read().decode("utf-8", errors="replace")[:2000]
        except Exception:
            pass
        raise ValueError(f"文生图 HTTP {e.code}: {err_body or e.reason}") from e
    except urllib.error.URLError as e:
        raise ValueError(f"文生图网络错误：{e.reason}") from e

    try:
        parsed: Any = json.loads(raw)
    except json.JSONDecodeError as e:
        preview = raw.replace("\n", " ")[:200]
        raise ValueError(f"文生图返回非 JSON（前 200 字符）：{preview}") from e
    if not isinstance(parsed, dict):
        raise ValueError("文生图响应格式异常")
    return parsed


def _extract_image_bytes(response: dict[str, Any]) -> tuple[bytes, str]:
    """返回 (png_bytes, mime_hint)。优先 url，其次 b64_json。"""
    data = response.get("data")
    if not isinstance(data, list) or not data:
        raise ValueError("文生图响应无 data 数组")
    first = data[0]
    if not isinstance(first, dict):
        raise ValueError("文生图 data[0] 格式异常")
    url = first.get("url")
    if isinstance(url, str) and url.startswith("http"):
        req = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.read(), "image/png"
        except urllib.error.URLError as e:
            raise ValueError(f"下载生成图失败：{e.reason}") from e
    b64 = first.get("b64_json")
    if isinstance(b64, str) and b64.strip():
        try:
            return base64.b64decode(b64), "image/png"
        except Exception as e:
            raise ValueError("解码 b64_json 失败") from e
    raise ValueError("文生图响应中无可用 url 或 b64_json")


def generate_slide_visual_png(
    *,
    api_base: str,
    api_key: str,
    model: str,
    prompt: str,
    size: str = DEFAULT_SIZE,
) -> bytes:
    """调用 OpenAI 兼容 images/generations，返回 PNG/JPEG 字节。"""
    url = resolve_images_generations_url(api_base)
    if not url:
        raise ValueError("未配置 API Base")
    key = (api_key or "").strip()
    if key.lower().startswith("bearer "):
        key = key[7:].strip()
    if not key:
        raise ValueError("未配置口播稿优化 API Key，无法文生图")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
    }
    body: dict[str, Any] = {
        "model": model or DEFAULT_IMAGE_MODEL,
        "prompt": prompt,
        "n": 1,
    }
    if size:
        body["size"] = size

    parsed = _post_json(url, headers, body)
    png, _ = _extract_image_bytes(parsed)
    if not png:
        raise ValueError("文生图得到空文件")
    return png


def save_generated_visual(
    task_dir: Path,
    slide_index: int,
    png_bytes: bytes,
    *,
    model_slug: str = "gpt-image-2",
) -> Path:
    """写入 ``generated_visuals/slide-NNNN/<timestamp>-<model>.png``。"""
    out_dir = task_dir / "generated_visuals" / f"slide-{slide_index:04d}"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_model = "".join(c if c.isalnum() or c in "-_" else "-" for c in model_slug)[:80]
    path = out_dir / f"{ts}-{safe_model}.png"
    path.write_bytes(png_bytes)
    logger.info("已保存文生图 %s (%s bytes)", path, len(png_bytes))
    return path


def latest_generated_visual_path(task_dir: Path, slide_index: int) -> Path | None:
    d = task_dir / "generated_visuals" / f"slide-{slide_index:04d}"
    if not d.is_dir():
        return None
    pngs = sorted(d.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    return pngs[0] if pngs else None


def generated_visual_coverage(task_dir: Path, slide_count: int) -> dict[str, Any]:
    """逐页检查是否存在 AI 生成 PNG；用于工作台分段切换与完成度。"""
    with_idx: list[int] = []
    for i in range(max(0, slide_count)):
        p = latest_generated_visual_path(task_dir, i)
        if p is not None and p.is_file():
            with_idx.append(i)
    return {
        "slide_count": slide_count,
        "slides_with_generated": with_idx,
        "all_slides_complete": slide_count > 0 and len(with_idx) == slide_count,
    }
