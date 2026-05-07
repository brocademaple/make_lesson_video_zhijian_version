"""Pydantic schema：原始页、分析结果、课程页。"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator

# --- Raw slide ---


class RawSlide(BaseModel):
    slide_index: int
    title_text: Optional[str] = None
    all_text: str
    text_blocks: list[str] = Field(default_factory=list)
    image_count: int = 0
    table_count: int = 0
    notes: Optional[str] = None
    layout_info: Optional[str] = None


SlidePageType = Literal[
    "cover",
    "agenda",
    "rule_dense",
    "rule_card",
    "case",
    "quiz",
    "summary",
    "transition",
    "unknown",
]

ContentDensity = Literal["low", "medium", "high", "very_high"]

AnalysisOperation = Literal["keep", "split", "merge", "rewrite", "delete"]


class SlideAnalysis(BaseModel):
    slide_index: int
    original_title: Optional[str] = None
    page_type: SlidePageType = "unknown"
    content_density: ContentDensity = "medium"
    core_topic: str = ""
    key_points: list[str] = Field(default_factory=list)
    rules: list[str] = Field(default_factory=list)
    cases: list[str] = Field(default_factory=list)
    penalties: list[str] = Field(default_factory=list)
    quiz_candidates: list[str] = Field(default_factory=list)
    should_keep: bool = True
    operation: AnalysisOperation = "keep"
    reason: str = ""

    @field_validator("page_type", mode="before")
    @classmethod
    def _v_page(cls, v: object) -> str:
        allowed = {
            "cover",
            "agenda",
            "rule_dense",
            "rule_card",
            "case",
            "quiz",
            "summary",
            "transition",
            "unknown",
        }
        s = str(v) if v is not None else "unknown"
        return s if s in allowed else "unknown"

    @field_validator("content_density", mode="before")
    @classmethod
    def _v_density(cls, v: object) -> str:
        allowed = {"low", "medium", "high", "very_high"}
        s = str(v) if v is not None else "medium"
        return s if s in allowed else "medium"

    @field_validator("operation", mode="before")
    @classmethod
    def _v_op(cls, v: object) -> str:
        allowed = {"keep", "split", "merge", "rewrite", "delete"}
        s = str(v) if v is not None else "keep"
        return s if s in allowed else "keep"


CourseSlideType = Literal[
    "title",
    "agenda",
    "transition",
    "rule_card",
    "case_dialogue",
    "quiz",
    "explanation",
    "summary",
]


class CourseSlide(BaseModel):
    slide_id: str
    source_slide_indexes: list[int] = Field(default_factory=list)
    type: CourseSlideType
    title: str
    subtitle: Optional[str] = None
    main_text: Optional[str] = None
    bullets: list[str] = Field(default_factory=list)
    dialogue: list[dict[str, Any]] = Field(default_factory=list)
    quiz: Optional[dict[str, Any]] = None
    explanation: Optional[str] = None
    narration: str = ""
    visual_suggestion: str = ""
    duration_seconds: int = 15
    # 图床 / 生图扩展预留
    image_prompt: Optional[str] = None
    image_url: Optional[str] = None
    asset_urls: list[str] = Field(default_factory=list)

    @field_validator("type", mode="before")
    @classmethod
    def _v_cs_type(cls, v: object) -> str:
        allowed = {
            "title",
            "agenda",
            "transition",
            "rule_card",
            "case_dialogue",
            "quiz",
            "explanation",
            "summary",
        }
        s = str(v) if v is not None else "rule_card"
        return s if s in allowed else "rule_card"


class RunSummary(BaseModel):
    mode: str
    ok: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    output_paths: dict[str, str] = Field(default_factory=dict)
