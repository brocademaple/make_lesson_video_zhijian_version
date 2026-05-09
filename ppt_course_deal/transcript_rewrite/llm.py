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


# 与 Web「音频生成参数」及 FastAPI _apply_minimax_generation_overrides 中情绪下拉一致
_MINIMAX_HINT_EMOTIONS = frozenset(
    {"happy", "calm", "fluent", "whisper", "sad"},
)
# 可写入本机 minimax_overrides 的键（与 app._AUDIO_GEN_OVERRIDE_KEYS 中合成相关子集）
_MINIMAX_HINT_PAYLOAD_KEYS = frozenset(
    {
        "model",
        "voice_id",
        "language_boost",
        "speed",
        "vol",
        "pitch",
        "emotion",
    }
)

_JSON_FENCE_RE = re.compile(
    r"```\s*json\s*([\s\S]*?)```",
    re.IGNORECASE,
)


def _is_minimax_hints_dict(d: dict[str, Any]) -> bool:
    """识别口播优化末尾的「合成参数建议」JSON（与纯技术 JSON 区分）。"""
    if not d:
        return False
    keys = frozenset(d.keys())
    if keys & _MINIMAX_HINT_PAYLOAD_KEYS:
        return True
    if d.get("delivery_notes") is not None or d.get("rationale") is not None:
        return True
    if d.get("notes") is not None:
        return True
    return False


def split_rewrite_output(raw: str) -> tuple[str, dict[str, Any] | None]:
    """从模型完整输出中拆出口播正文与可选的 MiniMax 参数建议 JSON 块。

    支持：正文后接 `` ```json ... ``` ``（取**最后**一个可解析为对象且
    含合成建议字段的块）。去掉该块后，再删去 trailing ``---`` 分隔行。
    若无法识别 JSON 块，整段视为正文（兼容旧版仅输出口播稿）。
    """
    text = (raw or "").strip()
    if not text:
        return "", None
    hints: dict[str, Any] | None = None
    last_match: re.Match[str] | None = None
    for m in _JSON_FENCE_RE.finditer(text):
        inner = m.group(1).strip()
        if not inner.startswith("{"):
            continue
        try:
            parsed: Any = json.loads(inner)
        except json.JSONDecodeError:
            continue
        if not isinstance(parsed, dict):
            continue
        # 空对象常见于探测请求；仍须剥掉代码块以免残留在「改写稿」正文里。
        if parsed == {}:
            hints = None
            last_match = m
            continue
        if not _is_minimax_hints_dict(parsed):
            continue
        hints = parsed
        last_match = m
    if last_match is not None:
        text = text[: last_match.start()] + text[last_match.end() :]
    text = text.strip()
    text = re.sub(r"\n?---\s*$", "", text)
    return text.strip(), hints


def normalize_minimax_rewrite_hints(
    raw: dict[str, Any] | None,
) -> tuple[dict[str, Any], str | None, list[str]]:
    """将模型 JSON 规范为可合并进 T2A / 前端的字段；返回 (payload, 说明文案, 警告)。"""
    warnings: list[str] = []
    if not raw:
        return {}, None, warnings
    note = raw.get("delivery_notes")
    if note is None:
        note = raw.get("rationale")
    if note is None:
        note = raw.get("notes")
    note_s: str | None
    if note is None or isinstance(note, (dict, list)):
        note_s = None
    else:
        s = str(note).strip()
        note_s = s[:2000] if s else None

    out: dict[str, Any] = {}
    for k in _MINIMAX_HINT_PAYLOAD_KEYS:
        if k not in raw or raw[k] is None:
            continue
        v = raw[k]
        if k == "emotion":
            if isinstance(v, str) and not v.strip():
                continue
            em = str(v).strip().lower()
            if em in _MINIMAX_HINT_EMOTIONS:
                out["emotion"] = em
            else:
                warnings.append(
                    f"已忽略无法识别的情绪建议 emotion={v!r}（允许：{', '.join(sorted(_MINIMAX_HINT_EMOTIONS))}）"
                )
            continue
        if k in ("speed", "vol"):
            try:
                out[k] = float(v)
            except (TypeError, ValueError):
                warnings.append(f"已忽略无法解析的 {k}：{v!r}")
        elif k == "pitch":
            try:
                out[k] = int(v)
            except (TypeError, ValueError):
                warnings.append(f"已忽略无法解析的 pitch：{v!r}")
        elif k in ("model", "voice_id", "language_boost"):
            s = str(v).strip()
            if s:
                out[k] = s
    return out, note_s, warnings


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
