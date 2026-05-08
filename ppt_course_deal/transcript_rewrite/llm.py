"""口播稿优化：OpenAI 兼容 Chat Completions 调用。"""

from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)


def resolve_chat_completions_url(api_base: str) -> str:
    """Turn UI「API Base」into a POST URL for OpenAI-compatible chat completions.

    Accepts host roots (… /v1 appended), bases already ending in /v1, or a full
    …/v1/chat/completions URL so users are not forced to guess path segments.
    """
    base = (api_base or "").strip().rstrip("/")
    if not base:
        return ""
    lower = base.lower()
    if lower.endswith("/chat/completions"):
        return base
    if lower.endswith("/v1"):
        return f"{base}/chat/completions"
    return f"{base}/v1/chat/completions"


def _try_parse_sse_json_line_payload(text: str) -> dict[str, Any] | None:
    """Some gateways mis-send ``stream: true`` bodies as SSE ``data: {...}``."""
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        payload = line[5:].strip()
        if payload == "[DONE]":
            continue
        try:
            parsed: Any = json.loads(payload)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue
    return None


def parse_chat_completions_response_body(raw: str) -> dict[str, Any]:
    """Parse a Chat Completions HTTP body (plain JSON or first SSE JSON chunk)."""
    text = (raw or "").lstrip("\ufeff").strip()
    if not text:
        raise ValueError("口播稿优化返回空响应")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        sse = _try_parse_sse_json_line_payload(text)
        if sse is not None:
            return sse
        preview = text.replace("\n", " ")[:160]
        raise ValueError(f"口播稿优化返回非 JSON（前 160 字符）：{preview}") from e
    if not isinstance(data, dict):
        raise ValueError("口播稿优化响应格式异常（顶层不是 JSON 对象）")
    return data


def normalize_rewrite_api_key(raw: str | None) -> str:
    s = (raw or "").strip()
    if s.lower().startswith("bearer "):
        s = s[7:].strip()
    return s


def _strip_code_fence(s: str) -> str:
    t = (s or "").strip()
    m = re.match(r"^```(?:\w*)?\s*([\s\S]*?)```\s*$", t)
    if m:
        return m.group(1).strip()
    return t


def chat_rewrite(
    *,
    api_base: str,
    api_key: str,
    model: str,
    system: str,
    user: str,
    timeout_sec: float = 120.0,
) -> str:
    base = (api_base or "").strip()
    if not base:
        raise ValueError("未配置口播稿优化 API Base")
    url = resolve_chat_completions_url(base)
    if not url:
        raise ValueError("未配置口播稿优化 API Base")
    key = normalize_rewrite_api_key(api_key)
    if not key:
        raise ValueError("未配置口播稿优化 API Key")
    payload: dict[str, Any] = {
        "model": (model or "").strip() or "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.35,
        "stream": False,
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:800]
        logger.warning("口播稿优化 LLM HTTP %s: %s", e.code, detail)
        raise ValueError(f"口播稿优化请求失败（HTTP {e.code}）") from e
    except urllib.error.URLError as e:
        raise ValueError(f"网络错误：{e.reason}") from e

    data = parse_chat_completions_response_body(raw)

    if isinstance(data, dict) and data.get("error"):
        err = data["error"]
        msg = err.get("message") if isinstance(err, dict) else str(err)
        raise ValueError(f"口播稿优化 API 错误：{msg}")

    choices = data.get("choices") if isinstance(data, dict) else None
    if not choices or not isinstance(choices, list):
        raise ValueError("口播稿优化响应缺少 choices")
    first = choices[0]
    msg = first.get("message") if isinstance(first, dict) else None
    content = ""
    if isinstance(msg, dict):
        content = msg.get("content") or ""
    if not isinstance(content, str):
        content = str(content)
    content = _strip_code_fence(content).strip()
    if not content:
        raise ValueError("模型返回空文本")
    return content
