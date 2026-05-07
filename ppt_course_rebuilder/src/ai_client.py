"""OpenAI-compatible Chat Completions + JSON 解析与重试。"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional

from openai import OpenAI

logger = logging.getLogger(__name__)


class AIClient:
    def __init__(
        self,
        api_key: Optional[str],
        base_url: str,
        model: str,
    ) -> None:
        self._model = model
        self._client: Optional[OpenAI] = None
        if api_key:
            self._client = OpenAI(api_key=api_key, base_url=base_url)

    @property
    def available(self) -> bool:
        return self._client is not None

    def call_json(self, prompt: str, schema_hint: str = "") -> Any:
        """调用模型并解析 JSON（对象或数组）。失败自动重试一次。"""
        if not self._client:
            raise RuntimeError("未配置 AI_API_KEY，无法调用 AI")

        full_prompt = prompt.strip()
        if schema_hint:
            full_prompt += "\n\n【输出格式提示】\n" + schema_hint.strip()

        last_err: Optional[Exception] = None
        for attempt in range(2):
            try:
                resp = self._client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {
                            "role": "system",
                            "content": "你只输出合法 JSON，不要 markdown 代码块，不要额外解释。",
                        },
                        {"role": "user", "content": full_prompt},
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"},
                )
                raw = resp.choices[0].message.content or ""
                logger.debug("AI 原始响应: %s", raw[:4000])
                return self._parse_json_payload(raw)
            except Exception as e:
                last_err = e
                logger.warning("AI 调用/解析失败 (第 %s 次): %s", attempt + 1, e)

        assert last_err is not None
        raise last_err

    def _parse_json_payload(self, raw: str) -> Any:
        text = raw.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        data = json.loads(text)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "slides" in data:
            return data["slides"]
        return data
