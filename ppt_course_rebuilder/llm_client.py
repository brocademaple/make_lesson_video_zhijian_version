"""OpenAI-compatible LLM client used by the director pipeline."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from ppt_course_rebuilder import config

logger = logging.getLogger(__name__)


def _normalize_base_url(raw: str) -> str:
    url = (raw or "").rstrip("/")
    if not url:
        return "https://dashscope.aliyuncs.com/compatible-mode/v1"
    if url.endswith("/v1"):
        return url
    return f"{url}/v1"


def configured_model() -> str:
    cfg = _load_director_llm_settings()
    if cfg and cfg.get("enabled") and str(cfg.get("api_key") or "").strip():
        model = str(cfg.get("model") or "").strip()
        if model:
            return model
    return config.ai_model()


def _load_director_llm_settings() -> dict[str, Any] | None:
    try:
        from ppt_course_deal.external_settings import (
            get_director_llm_for_server_call,
        )

        cfg = get_director_llm_for_server_call()
    except Exception:
        return None
    return cfg if isinstance(cfg, dict) else None


class DirectorLLMClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        director_cfg = _load_director_llm_settings()
        if api_key is None and director_cfg and director_cfg.get("enabled"):
            api_key = str(director_cfg.get("api_key") or "")
        if base_url is None and director_cfg and director_cfg.get("enabled"):
            base_url = str(director_cfg.get("api_base") or "")
        if model is None and director_cfg and director_cfg.get("enabled"):
            model = str(director_cfg.get("model") or "")

        key = (api_key if api_key is not None else config.ai_api_key()) or ""
        self.model = model or config.ai_model()
        self.base_url = _normalize_base_url(base_url or config.ai_base_url())
        self._client: Any | None = None
        if key.strip():
            from openai import OpenAI

            self._client = OpenAI(api_key=key.strip(), base_url=self.base_url)

    @property
    def available(self) -> bool:
        return self._client is not None

    def call_json(
        self,
        *,
        system: str,
        user: str,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        if self._client is None:
            raise RuntimeError("未配置 AI_API_KEY，无法调用 rebuilder LLM")

        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content or ""
        logger.debug("rebuilder LLM raw response: %s", raw[:4000])
        return _parse_json_object(raw)


def _parse_json_object(raw: str) -> dict[str, Any]:
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("LLM 输出必须是 JSON object")
    return data
