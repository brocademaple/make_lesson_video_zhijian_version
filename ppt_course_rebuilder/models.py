"""Pydantic 模型：原始素材清单与导演脚本。"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


class RawShape(BaseModel):
    shape_id: str = ""
    image_path: str = ""
    bbox: Optional[dict[str, Any]] = None
    ocr_text: Optional[str] = None
    source_type: Optional[str] = None


class RawSlide(BaseModel):
    slide_id: str = ""
    slide_index: int = 0
    full_page_png: Optional[str] = None
    raw_text: str = ""
    speaker_notes: Optional[str] = None
    shapes: list[RawShape] = Field(default_factory=list)


class RawMaterialManifest(BaseModel):
    task_id: str = ""
    source_pptx: str = ""
    task_root: str = ""
    slides: list[RawSlide] = Field(default_factory=list)


class CourseInfo(BaseModel):
    title: str = ""
    audience: str = ""
    goal: str = ""
    version: str = "1"


class AssetSpec(BaseModel):
    asset_id: str = ""
    source: str = "slide"
    source_slide_id: str = ""
    path: str = ""
    asset_type: str = "unknown"
    semantic_tags: list[str] = Field(default_factory=list)
    transparent: bool = False
    quality_status: str = "unknown"
    usage_suggestion: str = ""
    review_status: str = "pending"


class SceneSubtitle(BaseModel):
    segments: list[dict[str, Any]] = Field(default_factory=list)


class SceneTiming(BaseModel):
    estimated_duration_sec: float = 15.0


class SceneScreenDesign(BaseModel):
    layout: str = "full_slide"
    visual_strategy: str = ""
    emphasis: list[str] = Field(default_factory=list)


class SceneContent(BaseModel):
    title: str = ""
    onscreen_text: str = ""
    bullets: list[str] = Field(default_factory=list)


class SceneSpec(BaseModel):
    scene_id: str = ""
    scene_type: str = "explanation"
    source_slide_ids: list[str] = Field(default_factory=list)
    learning_goal: str = ""
    title: str = ""
    onscreen_text: str = ""
    narration: str = ""
    tts_text: str = ""
    subtitle_text: str = ""
    content: Optional[SceneContent] = None
    subtitle: SceneSubtitle = Field(default_factory=SceneSubtitle)
    timing: SceneTiming = Field(default_factory=SceneTiming)
    screen_design: SceneScreenDesign = Field(default_factory=SceneScreenDesign)
    visual_generation: Optional[dict[str, Any]] = None
    review_status: str = "pending"
    reject_reason: Optional[str] = None
    risk_flags: list[str] = Field(default_factory=list)
    version: str = "1"
    content_hash: str = ""
    asset_hash: str = ""
    audio_hash: str = ""
    render_cache_key: str = ""


class SceneReview(BaseModel):
    pending_count: int = 0
    approved_count: int = 0
    rejected_count: int = 0
    notes: str = ""


class DirectorManifest(BaseModel):
    task_id: str = ""
    course: CourseInfo = Field(default_factory=CourseInfo)
    assets: list[AssetSpec] = Field(default_factory=list)
    scenes: list[SceneSpec] = Field(default_factory=list)
    review: SceneReview = Field(default_factory=SceneReview)
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
