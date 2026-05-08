"""MiniMax T2A HTTP 调用（与官方 OpenAPI 对齐）。"""

from __future__ import annotations

import binascii
import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)


class MiniMaxTTSError(RuntimeError):
    pass


def normalize_minimax_api_key(raw: str | None) -> str:
    """去掉首尾空白；若用户误把「Bearer …」整段粘贴进密钥框，剥掉前缀以免请求头变成 Bearer Bearer。"""
    s = (raw or "").strip()
    lower = s.lower()
    if lower.startswith("bearer "):
        s = s[7:].strip()
    return s


def _build_payload(mm: dict[str, Any], text: str) -> dict[str, Any]:
    voice_setting: dict[str, Any] = {
        "voice_id": mm.get("voice_id") or "Chinese (Mandarin)_Lyrical_Voice",
        "speed": float(mm.get("speed", 1)),
        "vol": float(mm.get("vol", 1)),
        "pitch": int(mm.get("pitch", 0)),
    }
    emotion = mm.get("emotion")
    if emotion:
        voice_setting["emotion"] = emotion

    fmt = (mm.get("audio_format") or "mp3").lower()
    payload: dict[str, Any] = {
        "model": mm.get("model") or "speech-2.8-turbo",
        "text": text,
        "stream": bool(mm.get("stream", False)),
        "voice_setting": voice_setting,
        "audio_setting": {
            "sample_rate": int(mm.get("sample_rate", 32000)),
            "bitrate": int(mm.get("bitrate", 128000)),
            "format": fmt,
            # channel=1：单声道，体积小于立体声；与「外部 API 配置」中的码率等一同生效
            "channel": 1,
        },
    }
    lb = mm.get("language_boost")
    if lb:
        payload["language_boost"] = lb
    of = mm.get("output_format") or "hex"
    payload["output_format"] = of
    pd = mm.get("pronunciation_dict")
    if isinstance(pd, dict) and pd:
        payload["pronunciation_dict"] = pd
    if "subtitle_enable" in mm:
        payload["subtitle_enable"] = bool(mm["subtitle_enable"])
    return payload


def _payload_for_trace(payload: dict[str, Any]) -> dict[str, Any]:
    """归档用：缩短 text，避免 JSON 过大。"""
    p = dict(payload)
    t = p.get("text")
    if isinstance(t, str) and len(t) > 160:
        p["text"] = t[:160] + "…"
    return p


def synthesize_to_mp3_bytes_traced(
    mm: dict[str, Any], text: str
) -> tuple[bytes, dict[str, Any]]:
    """非流式合成；返回音频字节与可追溯摘要（无密钥明文）。"""
    key = normalize_minimax_api_key(mm.get("api_key"))
    if not key:
        raise MiniMaxTTSError("未配置 MiniMax API Key")

    text = (text or "").strip()
    if not text:
        raise MiniMaxTTSError("合成文本为空")
    if len(text) > 10000:
        raise MiniMaxTTSError("单次合成文本过长（上限 10000 字符）")

    base = (mm.get("api_base") or "https://api.minimaxi.com").rstrip("/")
    path = "/v1/t2a_v2"
    gid = (mm.get("group_id") or "").strip()
    if gid:
        path = path + "?GroupId=" + urllib.parse.quote(gid, safe="")

    url = base + path
    payload = _build_payload(mm, text)

    trace: dict[str, Any] = {
        "request": {
            "url": url,
            "payload": _payload_for_trace(payload),
            "authorization_suffix": key[-4:] if len(key) >= 4 else None,
        },
        "t2a_http": {},
        "audio": {},
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read()
            trace["t2a_http"]["status"] = getattr(resp, "status", 200)
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8", errors="replace")
        except Exception:
            detail = str(e)
        logger.warning("MiniMax HTTP %s: %s", e.code, detail[:500])
        hint = detail.strip()[:400]
        msg = f"MiniMax 请求失败（HTTP {e.code}）"
        if hint:
            msg += f"：{hint}"
        trace["t2a_http"]["error_http_status"] = e.code
        trace["t2a_http"]["error_body_excerpt"] = hint
        raise MiniMaxTTSError(msg) from e
    except urllib.error.URLError as e:
        raise MiniMaxTTSError(f"网络错误：{e.reason}") from e

    try:
        data = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise MiniMaxTTSError("MiniMax 返回非 JSON") from e

    base_resp = data.get("base_resp") or {}
    trace["t2a_http"]["base_resp"] = base_resp
    code = base_resp.get("status_code")
    if code != 0:
        msg = base_resp.get("status_msg") or "unknown"
        raise MiniMaxTTSError(f"MiniMax 错误：{msg}（code={code}）")

    inner = data.get("data") or {}
    audio_field = inner.get("audio")
    if not audio_field:
        raise MiniMaxTTSError("响应中无音频数据")

    if isinstance(audio_field, str) and audio_field.startswith("http"):
        trace["audio"]["delivery"] = "url"
        trace["audio"]["url_prefix"] = (
            audio_field[:120] + "…" if len(audio_field) > 120 else audio_field
        )
        try:
            with urllib.request.urlopen(audio_field, timeout=120) as au:
                audio_bytes = au.read()
        except urllib.error.URLError as e:
            raise MiniMaxTTSError(f"下载音频 URL 失败：{e}") from e
        trace["audio"]["final_bytes"] = len(audio_bytes)
        return audio_bytes, trace

    if not isinstance(audio_field, str):
        raise MiniMaxTTSError("音频字段格式异常")

    trace["audio"]["delivery"] = "hex"
    trace["audio"]["hex_char_len"] = len(audio_field)
    try:
        audio_bytes = binascii.unhexlify(audio_field.strip())
    except binascii.Error as e:
        raise MiniMaxTTSError("音频 hex 解码失败") from e
    trace["audio"]["final_bytes"] = len(audio_bytes)
    return audio_bytes, trace


def synthesize_to_mp3_bytes(mm: dict[str, Any], text: str) -> bytes:
    """非流式；返回 mp3/pcm/flac 原始字节（由 audio_setting.format 决定）。

    请求体含 ``audio_setting.channel=1``（单声道），便于控制文件大小。
    """
    audio, _ = synthesize_to_mp3_bytes_traced(mm, text)
    return audio
