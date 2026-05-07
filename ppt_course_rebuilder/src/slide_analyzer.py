"""单页结构化分析（调用 AI）。"""

from __future__ import annotations

import logging
from typing import List

from ai_client import AIClient
from models import RawSlide, SlideAnalysis

logger = logging.getLogger(__name__)


def fallback_analysis(rs: RawSlide) -> SlideAnalysis:
    """AI 失败时的兜底分析（不编造规则，仅做密度与保留建议）。"""
    dense: str = "low"
    al = len(rs.all_text or "")
    if al > 1200:
        dense = "very_high"
    elif al > 600:
        dense = "high"
    elif al > 200:
        dense = "medium"
    return SlideAnalysis(
        slide_index=rs.slide_index,
        original_title=rs.title_text,
        page_type="rule_dense" if al > 400 else "unknown",
        content_density=dense,
        core_topic=(rs.title_text or "本节要点")[:120],
        key_points=[],
        rules=[],
        cases=[],
        penalties=[],
        quiz_candidates=[],
        should_keep=True,
        operation="split" if dense in ("high", "very_high") else "keep",
        reason="本地兜底：AI 不可用或解析失败；请人工复核。",
    )

ANALYSIS_SCHEMA_HINT = """输出一个 JSON 对象，字段：
slide_index, original_title, page_type, content_density, core_topic,
key_points, rules, cases, penalties, quiz_candidates, should_keep, operation, reason"""


def build_analysis_prompt(rs: RawSlide) -> str:
    title = rs.title_text or "（无标题）"
    return f"""你是一名培训课程设计专家，正在把一份文字密集型业务培训 PPT 改造成适合录制视频课程的新 PPT。

请分析下面这一页原始 PPT，并输出严格 JSON。

你需要判断：
1. 这一页的核心主题是什么；
2. 这一页是否文字过多；
3. 这一页包含哪些规则点；
4. 是否包含案例；
5. 是否包含处罚规则；
6. 是否适合直接保留；
7. 应该如何处理：保留、拆分、合并、改写、删除；
8. 是否可以生成互动题。

原始页信息：
页码：{rs.slide_index}
标题：{title}
全文：
{rs.all_text}

请输出 JSON，格式如下：
{{
  "slide_index": {rs.slide_index},
  "original_title": "...",
  "page_type": "rule_dense",
  "content_density": "very_high",
  "core_topic": "...",
  "key_points": ["...", "..."],
  "rules": ["...", "..."],
  "cases": ["...", "..."],
  "penalties": ["...", "..."],
  "quiz_candidates": ["...", "..."],
  "should_keep": true,
  "operation": "split",
  "reason": "..."
}}

要求：
- 不要输出 markdown；
- 不要输出解释；
- 只输出 JSON；
- 不得虚构原文没有的信息；
- 如果信息不明确，用空数组；
- 规则表达要忠于原文；
- 不要改变业务含义。

page_type 取值：cover, agenda, rule_dense, rule_card, case, quiz, summary, transition, unknown
content_density 取值：low, medium, high, very_high
operation 取值：keep, split, merge, rewrite, delete
"""


def analyze_slide(client: AIClient, rs: RawSlide) -> SlideAnalysis:
    prompt = build_analysis_prompt(rs)
    data = client.call_json(prompt, ANALYSIS_SCHEMA_HINT)
    if not isinstance(data, dict):
        raise ValueError("分析结果应为 JSON 对象")
    data.setdefault("slide_index", rs.slide_index)
    return SlideAnalysis.model_validate(data)


def analyze_all(client: AIClient, slides: List[RawSlide]) -> List[SlideAnalysis]:
    out: List[SlideAnalysis] = []
    for rs in slides:
        logger.info("分析第 %s 页…", rs.slide_index)
        try:
            if not client.available:
                raise RuntimeError("AI 未配置")
            out.append(analyze_slide(client, rs))
        except Exception as e:
            logger.warning("第 %s 页 AI 分析失败，使用兜底：%s", rs.slide_index, e)
            out.append(fallback_analysis(rs))
    return out
