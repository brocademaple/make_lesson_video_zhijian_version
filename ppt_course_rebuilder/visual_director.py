"""Visual direction helpers for the dual Remotion + Hyperframes renderer."""

from __future__ import annotations

from typing import Any


REMOTION_STABLE = "remotion_stable"
HYPERFRAMES_CREATIVE = "hyperframes_creative"
HYBRID = "hybrid"

VALID_RENDER_ENGINES = {REMOTION_STABLE, HYPERFRAMES_CREATIVE, HYBRID}


def scene_role_for_scene(scene_type: str, index: int, total: int) -> str:
    st = (scene_type or "").strip()
    if index == 0 or st == "title":
        return "intro"
    if index == total - 1 or st == "summary":
        return "recap"
    if st == "agenda":
        return "transition"
    if st in {"case_dialogue", "explanation"}:
        return "concept_animation"
    return "content"


def render_engine_for_scene(scene_role: str, scene_type: str, risk_flags: list[str]) -> str:
    if risk_flags:
        return REMOTION_STABLE
    if scene_role in {"intro", "transition", "recap"}:
        return HYPERFRAMES_CREATIVE
    if scene_role == "concept_animation" or scene_type == "case_dialogue":
        return HYBRID
    return REMOTION_STABLE


def creative_brief_for_scene(
    scene: dict[str, Any],
    *,
    scene_role: str,
    render_engine: str,
    profile: dict[str, Any],
) -> dict[str, Any]:
    source_slide_ids = scene.get("source_slide_ids")
    if not isinstance(source_slide_ids, list):
        source_slide_ids = []
    evidence = scene.get("source_evidence")
    if not isinstance(evidence, list):
        evidence = []
    timing = scene.get("timing") if isinstance(scene.get("timing"), dict) else {}
    try:
        duration_sec = float(timing.get("estimated_duration_sec") or 3)
    except (TypeError, ValueError):
        duration_sec = 3.0

    intent = {
        REMOTION_STABLE: "保留原 PPT 证据与字幕节奏，避免艺术化改写高风险信息。",
        HYPERFRAMES_CREATIVE: "生成全屏创意镜头，可作为片头、转场、复盘或概念动画嵌入 Remotion 时间线。",
        HYBRID: "生成创意动效层或氛围背景，由 Remotion 继续承载 PPT 证据、口播与字幕。",
    }.get(render_engine, "生成可嵌入 Remotion 时间线的视觉片段。")

    return {
        "engine": "hyperframes" if render_engine in {HYPERFRAMES_CREATIVE, HYBRID} else "remotion",
        "scene_role": scene_role,
        "intent": intent,
        "style": str(profile.get("label") or profile.get("id") or "企业培训视频"),
        "motion_style": str(profile.get("motion_style") or ""),
        "visual_strategy": str(profile.get("visual_strategy") or ""),
        "title": str(scene.get("title") or ""),
        "onscreen_text": str(scene.get("onscreen_text") or "")[:500],
        "subtitle_text": str(scene.get("subtitle_text") or "")[:240],
        "duration_sec": max(1.0, duration_sec),
        "canvas": {"width": 1920, "height": 1080, "fps": 30},
        "source_slide_ids": [str(item) for item in source_slide_ids[:6]],
        "evidence_quotes": [
            {
                "slide_id": str(item.get("slide_id") or ""),
                "quote": str(item.get("quote") or "")[:180],
            }
            for item in evidence[:3]
            if isinstance(item, dict) and str(item.get("quote") or "").strip()
        ],
        "must_not": [
            "不要改写金额、处罚、合规边界等高风险事实",
            "不要遮挡 Remotion 后续叠加的字幕安全区",
            "不要依赖外部网络素材",
        ],
    }


def apply_visual_direction(
    scene: dict[str, Any],
    *,
    index: int,
    total: int,
    profile: dict[str, Any],
) -> dict[str, Any]:
    scene_type = str(scene.get("scene_type") or "")
    risk_flags = scene.get("risk_flags") if isinstance(scene.get("risk_flags"), list) else []
    role = str(scene.get("scene_role") or "").strip() or scene_role_for_scene(scene_type, index, total)
    engine = str(scene.get("render_engine") or "").strip()
    if engine not in VALID_RENDER_ENGINES:
        engine = render_engine_for_scene(role, scene_type, [str(item) for item in risk_flags])
    scene["scene_role"] = role
    scene["render_engine"] = engine
    scene["fallback_engine"] = REMOTION_STABLE if engine != REMOTION_STABLE else ""
    scene["creative_brief"] = creative_brief_for_scene(
        scene,
        scene_role=role,
        render_engine=engine,
        profile=profile,
    )
    return scene
