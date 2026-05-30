from __future__ import annotations

import pytest

from ppt_course_deal import speech_synthesis as ss
from ppt_course_deal.minimax_client import MiniMaxTTSError


def test_synthesize_speech_falls_back_to_edge_tts(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_minimax(_mm, _text):
        raise MiniMaxTTSError("MiniMax 错误：资源包已过期")

    monkeypatch.setattr(ss, "synthesize_to_mp3_bytes_traced", fail_minimax)
    monkeypatch.setattr(ss, "_run_async_edge_tts", lambda **_kwargs: b"mp3-bytes")

    result = ss.synthesize_speech(
        minimax={"api_key": "expired"},
        tts={
            "provider": "minimax",
            "fallback_enabled": True,
            "fallback_provider": "edge_tts",
            "edge_tts": {"voice": "zh-CN-XiaoxiaoNeural"},
        },
        text="你好，这是兜底语音。",
    )

    assert result.audio_bytes == b"mp3-bytes"
    assert result.provider == "edge_tts"
    assert result.fallback_used is True
    assert "资源包已过期" in result.primary_error


def test_synthesize_speech_can_use_edge_tts_directly(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {}

    def fake_edge(**kwargs):
        called.update(kwargs)
        return b"edge"

    monkeypatch.setattr(ss, "_run_async_edge_tts", fake_edge)

    result = ss.synthesize_speech(
        minimax={},
        tts={
            "provider": "edge_tts",
            "edge_tts": {
                "voice": "zh-CN-XiaoxiaoNeural",
                "rate": "5",
                "volume": "+0%",
                "pitch": "0",
            },
        },
        text="直接使用 edge tts。",
    )

    assert result.provider == "edge_tts"
    assert result.fallback_used is False
    assert called["rate"] == "+5%"
    assert called["pitch"] == "+0Hz"


def test_synthesize_speech_reports_without_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        ss,
        "synthesize_to_mp3_bytes_traced",
        lambda _mm, _text: (_ for _ in ()).throw(MiniMaxTTSError("quota expired")),
    )

    with pytest.raises(ss.SpeechSynthesisError, match="quota expired"):
        ss.synthesize_speech(
            minimax={"api_key": "expired"},
            tts={"provider": "minimax", "fallback_enabled": False},
            text="hello",
        )
