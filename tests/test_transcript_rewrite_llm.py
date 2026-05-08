"""Unit tests for transcript_rewrite.llm URL resolution and response parsing."""

import json

import pytest

from ppt_course_deal.transcript_rewrite import (
    parse_chat_completions_response_body,
    resolve_chat_completions_url,
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
