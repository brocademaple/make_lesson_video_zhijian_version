"""Speech synthesis provider dispatch for the audio workspace."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from ppt_course_deal.minimax_client import (
    MiniMaxTTSError,
    synthesize_to_mp3_bytes_traced,
)


class SpeechSynthesisError(RuntimeError):
    pass


@dataclass
class SpeechSynthesisResult:
    audio_bytes: bytes
    audio_format: str = "mp3"
    provider: str = "unknown"
    fallback_used: bool = False
    primary_error: str = ""
    trace: dict[str, Any] = field(default_factory=dict)


def synthesize_speech(
    *,
    minimax: dict[str, Any],
    tts: dict[str, Any],
    text: str,
) -> SpeechSynthesisResult:
    provider = str(tts.get("provider") or "minimax").strip().lower()
    fallback_enabled = bool(tts.get("fallback_enabled", True))
    fallback_provider = str(tts.get("fallback_provider") or "edge_tts").strip().lower()

    if provider == "edge_tts":
        return _synthesize_edge_result(tts, text, fallback_used=False)
    if provider not in ("minimax", "edge_tts"):
        raise SpeechSynthesisError(f"不支持的 TTS provider：{provider}")

    try:
        audio_bytes, trace = synthesize_to_mp3_bytes_traced(minimax, text)
        fmt = str(minimax.get("audio_format") or "mp3").lower()
        if fmt not in ("mp3", "pcm", "flac"):
            fmt = "mp3"
        return SpeechSynthesisResult(
            audio_bytes=audio_bytes,
            audio_format=fmt,
            provider="minimax",
            trace={"minimax": trace},
        )
    except MiniMaxTTSError as e:
        primary_error = str(e)
        if not fallback_enabled or fallback_provider != "edge_tts":
            raise SpeechSynthesisError(primary_error) from e
        edge = _synthesize_edge_result(tts, text, fallback_used=True)
        edge.primary_error = primary_error
        edge.trace.setdefault("fallback_from", "minimax")
        return edge


def _synthesize_edge_result(
    tts: dict[str, Any], text: str, *, fallback_used: bool
) -> SpeechSynthesisResult:
    edge_cfg = tts.get("edge_tts") if isinstance(tts.get("edge_tts"), dict) else {}
    voice = str(edge_cfg.get("voice") or "zh-CN-XiaoxiaoNeural")
    rate = _edge_percent(edge_cfg.get("rate"), default="+0%")
    volume = _edge_percent(edge_cfg.get("volume"), default="+0%")
    pitch = _edge_pitch(edge_cfg.get("pitch"), default="+0Hz")
    try:
        audio = _run_async_edge_tts(
            text=(text or "").strip(),
            voice=voice,
            rate=rate,
            volume=volume,
            pitch=pitch,
        )
    except Exception as e:
        raise SpeechSynthesisError(f"edge-tts 合成失败：{e}") from e
    return SpeechSynthesisResult(
        audio_bytes=audio,
        audio_format="mp3",
        provider="edge_tts",
        fallback_used=fallback_used,
        trace={
            "edge_tts": {
                "voice": voice,
                "rate": rate,
                "volume": volume,
                "pitch": pitch,
                "audio_bytes": len(audio),
            }
        },
    )


def _edge_percent(value: Any, *, default: str) -> str:
    s = str(value if value is not None else default).strip()
    if not s:
        return default
    if s.endswith("%") and (s[0] in "+-" or s[0].isdigit()):
        return s
    try:
        n = float(s)
    except ValueError:
        return default
    if -100 <= n <= 100:
        return f"{n:+.0f}%"
    return default


def _edge_pitch(value: Any, *, default: str) -> str:
    s = str(value if value is not None else default).strip()
    if not s:
        return default
    if s.endswith("Hz") and (s[0] in "+-" or s[0].isdigit()):
        return s
    try:
        n = float(s)
    except ValueError:
        return default
    if -100 <= n <= 100:
        return f"{n:+.0f}Hz"
    return default


async def _edge_tts_bytes(
    *,
    text: str,
    voice: str,
    rate: str,
    volume: str,
    pitch: str,
) -> bytes:
    if not text:
        raise SpeechSynthesisError("合成文本为空")
    try:
        import edge_tts
    except ModuleNotFoundError as e:
        raise SpeechSynthesisError("缺少 edge-tts 依赖，请执行 pip install -e .") from e

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        volume=volume,
        pitch=pitch,
    )
    chunks: list[bytes] = []
    async for chunk in communicate.stream():
        if chunk.get("type") == "audio" and chunk.get("data"):
            chunks.append(bytes(chunk["data"]))
    if not chunks:
        raise SpeechSynthesisError("edge-tts 未返回音频数据")
    return b"".join(chunks)


def _run_async_edge_tts(
    *,
    text: str,
    voice: str,
    rate: str,
    volume: str,
    pitch: str,
) -> bytes:
    return asyncio.run(
        _edge_tts_bytes(
            text=text,
            voice=voice,
            rate=rate,
            volume=volume,
            pitch=pitch,
        )
    )
