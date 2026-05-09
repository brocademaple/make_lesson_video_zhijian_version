"""Unit tests for transcript_rewrite.llm URL resolution and response parsing."""

import json

import pytest

from ppt_course_deal.transcript_rewrite import (
    normalize_minimax_rewrite_hints,
    parse_chat_completions_response_body,
    resolve_chat_completions_url,
    split_rewrite_output,
)


@pytest.mark.parametrize(
    ("api_base", "expected"),
    [
        ("https://api.openai.com", "https://api.openai.com/v1/chat/completions"),
        ("https://api.openai.com/", "https://api.openai.com/v1/chat/completions"),
        ("https://api.openai.com/v1", "https://api.openai.com/v1/chat/completions"),
        (
            "https://ops-ai-gateway.example.tv",
            "https://ops-ai-gateway.example.tv/v1/chat/completions",
        ),
        (
            "https://example.com/openai/v1",
            "https://example.com/openai/v1/chat/completions",
        ),
        (
            "https://api.openai.com/v1/chat/completions",
            "https://api.openai.com/v1/chat/completions",
        ),
    ],
)
def test_resolve_chat_completions_url(api_base: str, expected: str) -> None:
    assert resolve_chat_completions_url(api_base) == expected


def test_parse_plain_json() -> None:
    raw = json.dumps({"choices": [{"message": {"content": "ok"}}]})
    data = parse_chat_completions_response_body(raw)
    assert data["choices"][0]["message"]["content"] == "ok"


def test_parse_sse_first_line() -> None:
    inner = {"choices": [{"message": {"content": "hi"}}]}
    raw = "data: " + json.dumps(inner) + "\n\n"
    data = parse_chat_completions_response_body(raw)
    assert data["choices"][0]["message"]["content"] == "hi"


def test_parse_bom_prefix() -> None:
    raw = "\ufeff" + json.dumps({"choices": [{"message": {"content": "x"}}]})
    data = parse_chat_completions_response_body(raw)
    assert data["choices"][0]["message"]["content"] == "x"


def test_split_rewrite_output_strips_json_fence() -> None:
    raw = (
        "大家好，接下来我们看概念。\n\n---\n\n"
        '```json\n{"speed": 0.95, "emotion": "calm"}\n```\n'
    )
    text, hints = split_rewrite_output(raw)
    assert "概念" in text
    assert "```" not in text
    assert hints == {"speed": 0.95, "emotion": "calm"}


def test_split_rewrite_output_backward_compat_plain_text() -> None:
    text, hints = split_rewrite_output("仅有正文没有 JSON")
    assert text == "仅有正文没有 JSON"
    assert hints is None


def test_split_rewrite_output_strips_empty_json_block() -> None:
    """空 JSON 块应剥除，不污染口播正文（如连通性探测的短输出）。"""
    raw = "好\n\n---\n\n```json\n{}\n```\n"
    text, hints = split_rewrite_output(raw)
    assert hints is None
    assert text.strip() == "好"


def test_normalize_minimax_rewrite_hints_emotion() -> None:
    payload, notes, warns = normalize_minimax_rewrite_hints(
        {"speed": 1.05, "emotion": "CALM", "delivery_notes": "说明"}
    )
    assert payload["emotion"] == "calm"
    assert payload["speed"] == 1.05
    assert notes == "说明"
    assert not warns


def test_normalize_minimax_rewrite_hints_bad_emotion_warns() -> None:
    payload, _notes, warns = normalize_minimax_rewrite_hints({"emotion": "angry"})
    assert "emotion" not in payload
    assert any("angry" in w for w in warns)
