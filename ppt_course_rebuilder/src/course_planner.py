"""将 SlideAnalysis 列表规划为 List[CourseSlide]。"""

from __future__ import annotations

import json
import logging
from typing import List

from ai_client import AIClient
from models import CourseSlide, SlideAnalysis

logger = logging.getLogger(__name__)

PLANNER_SCHEMA_HINT = """输出 JSON 对象，必须包含键 \"slides\"，值为 CourseSlide 数组。
每个 CourseSlide 含：slide_id, source_slide_indexes, type, title, subtitle, main_text,
bullets, dialogue, quiz, explanation, narration, visual_suggestion, duration_seconds,
image_prompt, image_url, asset_urls（后三项可为 null/[]）。"""


def build_planner_prompt(analyses: List[SlideAnalysis]) -> str:
    payload = [a.model_dump() for a in analyses]
    slide_analysis_json = json.dumps(payload, ensure_ascii=False, indent=2)
    return f"""你是一名课程产品设计专家，需要把一组原始 PPT 页面分析结果，重构成一组适合录制视频课程的新 PPT 页面。

目标：
把文字密集型规则 PPT 转换成课程型 PPT。

课程型 PPT 要求：
- 页面更少字；
- 更适合视频讲解；
- 有规则卡；
- 有案例页；
- 有互动判断题；
- 有总结页；
- 每页对应 10–30 秒口播；
- 页面之间有清晰课程节奏。

业务准确性优先：
- 不得编造规则或改变处罚标准；
- 不得虚构案例；
- 每一页必须保留 source_slide_indexes 便于人工审核；
- 允许改写表述与过渡语，但必须与原文规则含义一致。

原始页面分析结果：
{slide_analysis_json}

请输出严格 JSON，格式为：{{ "slides": [ ... CourseSlide ... ] }}

页面类型 type 取值：
title, agenda, transition, rule_card, case_dialogue, quiz, explanation, summary

严格要求：
1. 根对象含 slides 数组；
2. 不要 markdown；
3. 新 PPT 页数可多于或少于原页；
4. 每页 title 简短；
5. bullets 最多 3 条；
6. narration 自然，适合 AI 配音；
7. visual_suggestion 具体；
8. 内容过长则拆页；
9. 每 4–6 页节奏中插入案例或互动（在合理位置）；
10. 原文有 quiz_candidates 时优先出现 quiz / explanation。

红线问题培训场景：若出现红线、致命/严重/普通问题、处罚、判断题等，请优先映射为 rule_card、case_dialogue、quiz、explanation、summary。
"""


def plan_course(client: AIClient, analyses: List[SlideAnalysis]) -> List[CourseSlide]:
    if not analyses:
        return []
    prompt = build_planner_prompt(analyses)
    data = client.call_json(prompt, PLANNER_SCHEMA_HINT)
    if isinstance(data, dict) and "slides" in data:
        data = data["slides"]
    if not isinstance(data, list):
        raise ValueError("规划结果应为数组或包含 slides 的对象")
    slides: List[CourseSlide] = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        item.setdefault("slide_id", f"S{i+1:03d}")
        slides.append(CourseSlide.model_validate(item))
    return slides


def plan_course_fallback(analyses: List[SlideAnalysis]) -> List[CourseSlide]:
    """AI 不可用或失败时：每页压缩为一张 rule_card（保守、可人工再审）。"""
    slides: List[CourseSlide] = []
    for i, a in enumerate(analyses):
        bullets = (a.rules or a.key_points or [])[:3]
        if not bullets and a.core_topic:
            bullets = [a.core_topic[:60]]
        slides.append(
            CourseSlide(
                slide_id=f"S{i+1:03d}",
                source_slide_indexes=[a.slide_index],
                type="rule_card",
                title=(a.core_topic[:36] + "…") if len(a.core_topic) > 36 else (a.core_topic or "规则要点"),
                subtitle=a.original_title,
                main_text=a.reason[:120] if a.reason else None,
                bullets=bullets,
                narration=(
                    f"这一页聚焦{a.core_topic or '本节规则'}。"
                    "请大家对照原文，牢记限制条件与触发情形。"
                ),
                visual_suggestion="深蓝标题 + 浅色卡片 + 盾牌图标；要点不超过三条。",
                duration_seconds=22,
            )
        )
    logger.warning("已使用本地兜底课程规划（未调用 AI 或调用失败）")
    return slides
