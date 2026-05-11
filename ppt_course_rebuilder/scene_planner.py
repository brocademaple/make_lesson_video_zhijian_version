"""幻灯片 → scene_type 启发式规划。"""

from __future__ import annotations

import re
from typing import Tuple


_AGENDA = re.compile(r"(目录|章节|Part|部分|议程)")
_RULE_STRONG = re.compile(r"(红线|致命|严重|处罚|扣除|罚款|绩效|解除劳动)")
_RULE_WORD = re.compile(r"(规则|条款|禁止|违规)")
_CASE = re.compile(r"(案例|对话|用户|销售|异议|情景)")


def infer_scene_type(raw_text: str, slide_index: int, title_hint: str = "") -> str:
    """
    返回 scene_type：title | agenda | rule_explanation | rule_card | case_dialogue | explanation
    """
    text = f"{title_hint}\n{raw_text}".strip()

    if slide_index == 0 and len(raw_text or "") < 120:
        # 首页倾向标题型（启发式）
        return "title"

    if _AGENDA.search(text):
        return "agenda"

    if _RULE_STRONG.search(text):
        if _RULE_STRONG.search(raw_text or "") and len(raw_text or "") > 100:
            return "rule_explanation"
        return "rule_card"

    if _RULE_WORD.search(text) and len(raw_text or "") < 200:
        return "rule_card"

    if _CASE.search(text):
        return "case_dialogue"

    return "explanation"


def scene_title_for_type(scene_type: str, slide_title: str, raw_excerpt: str) -> Tuple[str, str]:
    """(卡片标题, learning_goal)"""
    excerpt = (raw_excerpt or "").strip().replace("\n", " ")[:80]
    st = scene_type
    if st == "title":
        return (
            slide_title or "课程开篇",
            "建立本节主题与听众预期。",
        )
    if st == "agenda":
        return ("结构与目录", "帮助听众理解课程组织结构。")
    if st in ("rule_explanation", "rule_card"):
        return (
            slide_title or "规则要点",
            "准确理解规则边界、等级与后果。",
        )
    if st == "case_dialogue":
        return (
            slide_title or "案例与对话",
            "通过情境掌握口径与应对方式。",
        )
    return (
        slide_title or (excerpt + "…") if excerpt else "要点讲解",
        "掌握本页关键概念与可执行结论。",
    )
