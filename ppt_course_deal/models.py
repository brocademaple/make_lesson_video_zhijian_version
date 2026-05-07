from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class BlockKind(str, Enum):
    """内容块类型（启发式分类 + 人工扩展）。"""

    RULE = "rule"  # 规则 / 要点 / 条款
    CASE = "case"  # 案例 / 场景
    PENALTY = "penalty"  # 处罚 / 后果
    INTERACTION = "interaction"  # 互动 / 练习 / 测验
    SUMMARY = "summary"  # 总结 / 小结
    NARRATION = "narration"  # 讲解叙述（默认兜底）
    TITLE = "title"  # 标题性语句（页级）


class ContentBlock(BaseModel):
    """单段结构化内容。"""

    kind: BlockKind
    text: str = Field(..., description="原始文本，保留换行与编号")


class SourceSlide(BaseModel):
    """输入文件中的一页。"""

    index: int = Field(..., ge=0, description="从 0 开始的幻灯片序号")
    title: str = ""
    raw_text: str = ""
    blocks: list[ContentBlock] = Field(default_factory=list)


class CourseSlidePlan(BaseModel):
    """输出侧一页的规划（可由一页输入拆成多页输出）。"""

    source_slide_index: int
    segment_label: Optional[str] = None  # 如「续 1/2」
    slide_title: str
    sections: dict[str, str] = Field(
        default_factory=dict,
        description="区块标题 -> 正文，键为 rule/case/penalty/interaction/summary/narration",
    )
    notes: Optional[str] = None  # 讲者备注（可接 TTS）


class TransformResult(BaseModel):
    """流水线输出摘要。"""

    source_path: str
    output_path: str
    source_slide_count: int
    output_slide_count: int
    slides: list[CourseSlidePlan] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)
