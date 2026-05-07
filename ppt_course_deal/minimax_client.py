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
        "model": mm.get("model") or "speech-2.8-hd",
        "text": text,
        "stream": bool(mm.get("stream", False)),
        "voice_setting": voice_setting,
        "audio_setting": {
            "sample_rate": int(mm.get("sample_rate", 32000)),
            "bitrate": int(mm.get("bitrate", 128000)),
            "format": fmt,
            "channel": 1,
        },
    }
    lb = mm.get("language_boost")
    if lb:
        payload["language_boost"] = lb
    of = mm.get("output_format") or "hex"
    payload["output_format"] = of
    return payload


def synthesize_to_mp3_bytes(mm: dict[str, Any], text: str) -> bytes:
    """非流式；返回 mp3/pcm/flac 原始字节（由 audio_setting.format 决定）。"""
    key = (mm.get("api_key") or "").strip()
    if not key:
        raise MiniMaxTTSError("未配置 MiniMax API Key")

    text = (text or "").strip()
    if not text:
        raise MiniMaxTTSError("合成文本为空")
    if len(text) > 10000:
        raise MiniMaxTTSError("单次合成文本过长（上限 10000 字符）")

    base = (mm.get("api_base") or "https://api.minimax.io").rstrip("/")
    path = "/v1/t2a_v2"
    gid = (mm.get("group_id") or "").strip()
    if gid:
        path = path + "?GroupId=" + urllib.parse.quote(gid, safe="")

    url = base + path
    payload = _build_payload(mm, text)

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
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8", errors="replace")
        except Exception:
            detail = str(e)
        logger.warning("MiniMax HTTP %s: %s", e.code, detail[:500])
        raise MiniMaxTTSError(f"MiniMax 请求失败（HTTP {e.code}）") from e
    except urllib.error.URLError as e:
        raise MiniMaxTTSError(f"网络错误：{e.reason}") from e

    try:
        data = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise MiniMaxTTSError("MiniMax 返回非 JSON") from e

    base_resp = data.get("base_resp") or {}
    code = base_resp.get("status_code")
    if code != 0:
        msg = base_resp.get("status_msg") or "unknown"
        raise MiniMaxTTSError(f"MiniMax 错误：{msg}（code={code}）")

    inner = data.get("data") or {}
    audio_field = inner.get("audio")
    if not audio_field:
        raise MiniMaxTTSError("响应中无音频数据")

    if isinstance(audio_field, str) and audio_field.startswith("http"):
        try:
            with urllib.request.urlopen(audio_field, timeout=120) as au:
                return au.read()
        except urllib.error.URLError as e:
            raise MiniMaxTTSError(f"下载音频 URL 失败：{e}") from e

    if not isinstance(audio_field, str):
        raise MiniMaxTTSError("音频字段格式异常")

    try:
        return binascii.unhexlify(audio_field.strip())
    except binascii.Error as e:
        raise MiniMaxTTSError("音频 hex 解码失败") from e
