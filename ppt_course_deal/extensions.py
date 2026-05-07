from __future__ import annotations

from typing import Protocol, runtime_checkable

from ppt_course_deal.models import ContentBlock, SourceSlide


@runtime_checkable
class SlideAnalyzer(Protocol):
    """后续可替换为：LLM API、本地 Skill、多模态模型等。"""

    def analyze(self, slide: SourceSlide) -> list[ContentBlock]:
        """返回结构化内容块（可覆盖启发式分类结果）。"""
        ...


class HeuristicAnalyzer:
    """默认实现：基于关键词与规则的启发式分类。"""

    def analyze(self, slide: SourceSlide) -> list[ContentBlock]:
        from ppt_course_deal.classify import classify_slide_text

        return classify_slide_text(slide.raw_text)
