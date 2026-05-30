"""Rule-first material tagging for the director pipeline."""

from __future__ import annotations

import re
from typing import Any


def _has(pattern: str, text: str) -> bool:
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def tag_slide_text(text: str, *, slide_index: int = 0, slide_count: int = 0) -> list[str]:
    body = " ".join(str(text or "").split())
    tags: list[str] = []
    if slide_index == 0:
        tags.append("cover_candidate")
    if slide_count and slide_index >= slide_count - 1:
        tags.append("summary_candidate")
    if _has(r"(目录|大纲|agenda|contents|章节)", body):
        tags.append("agenda")
    if _has(r"(规则|制度|标准|要求|必须|禁止|不得|应当|流程|规范)", body):
        tags.append("rule")
    if _has(r"(案例|例如|比如|场景|客户|员工|学员|问题)", body):
        tags.append("case")
    if _has(r"(处罚|罚款|扣除|赔偿|金额|元|违约|风险|红线)", body):
        tags.append("risk_or_penalty")
    if _has(r"(总结|回顾|要点|小结|结论|下一步)", body):
        tags.append("summary")
    if re.search(r"\d", body):
        tags.append("contains_numbers")
    if not tags:
        tags.append("content")
    return list(dict.fromkeys(tags))


def infer_layout(tags: list[str]) -> str:
    tagset = set(tags)
    if "case" in tagset:
        return "case_dialogue"
    if "risk_or_penalty" in tagset or "rule" in tagset:
        return "rule_card"
    if "agenda" in tagset or "summary" in tagset:
        return "summary"
    return "full_slide"


def tag_asset(asset: dict[str, Any]) -> list[str]:
    path = str(asset.get("path") or asset.get("image_path") or "").lower()
    text = str(asset.get("ocr_text") or asset.get("raw_text") or "")
    tags: list[str] = []
    if "full.png" in path:
        tags.append("full_slide")
    if _has(r"(logo|品牌|商标)", path + " " + text):
        tags.append("logo")
    if _has(r"(截图|页面|系统|界面|按钮)", text):
        tags.append("screenshot")
    if _has(r"(装饰|背景|线条|图标)", text):
        tags.append("decorative")
    tags.extend(tag_slide_text(text, slide_index=0, slide_count=0))
    return list(dict.fromkeys(tags))
