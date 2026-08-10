"""Video intent profiles shared by the web UI, director and Remotion adapter."""

from __future__ import annotations

from typing import Any


DEFAULT_VIDEO_PROFILE_ID = "knowledge"


VIDEO_PROFILES: dict[str, dict[str, Any]] = {
    "knowledge": {
        "id": "knowledge",
        "label": "知识讲解",
        "short_label": "知识",
        "goal": "把观点、案例和方法拆成有节奏的镜头，帮助观众快速理解一个主题。",
        "audience": "AIGC 创作者、知识分享者、研究和产品观察者",
        "tone": "清楚、有观点、节奏稳",
        "duration_hint": "3-8 分钟",
        "layout_bias": ["full_slide", "split_panel", "summary"],
        "visual_strategy": "structured_explainer_with_visual_moments",
        "motion_style": "guided_steps",
        "remotion": {
            "theme": "knowledge",
            "shot_motion": "gentle_pan",
            "overlay_density": "medium",
            "evidence_mode": "supporting",
        },
    },
    "retrospective": {
        "id": "retrospective",
        "label": "作品复盘",
        "short_label": "复盘",
        "goal": "把过程、判断和结果串成有起承转合的复盘视频。",
        "audience": "个人创作者、项目作者、团队复盘观众",
        "tone": "真诚、具体、有方法沉淀",
        "duration_hint": "4-10 分钟",
        "layout_bias": ["full_slide", "split_panel", "summary"],
        "visual_strategy": "timeline_with_decision_moments",
        "motion_style": "slow_push",
        "remotion": {
            "theme": "retrospective",
            "shot_motion": "gentle_pan",
            "overlay_density": "medium",
            "evidence_mode": "supporting",
        },
    },
    "product": {
        "id": "product",
        "label": "产品体验",
        "short_label": "产品",
        "goal": "把产品界面、功能路径和体验判断剪成清楚流畅的演示视频。",
        "audience": "AIGC 创作者、产品观察者、工具使用者",
        "tone": "清晰、轻快、强调体验细节",
        "duration_hint": "2-5 分钟",
        "layout_bias": ["split_panel", "case_dialogue", "summary"],
        "visual_strategy": "screen_demo_with_zoom_and_callouts",
        "motion_style": "spotlight",
        "remotion": {
            "theme": "product",
            "shot_motion": "spotlight_reveal",
            "overlay_density": "medium",
            "evidence_mode": "light",
        },
    },
    "workflow": {
        "id": "workflow",
        "label": "流程教学",
        "short_label": "流程",
        "goal": "把操作步骤、关键界面和注意事项拆成可跟随的教程镜头。",
        "audience": "工具用户、创作者、团队协作者",
        "tone": "直接、动作导向、少铺垫",
        "duration_hint": "3-6 分钟",
        "layout_bias": ["split_panel", "full_slide", "summary"],
        "visual_strategy": "step_by_step_visual_guide",
        "motion_style": "process_slide",
        "remotion": {
            "theme": "workflow",
            "shot_motion": "horizontal_track",
            "overlay_density": "medium",
            "evidence_mode": "light",
        },
    },
    "freeform": {
        "id": "freeform",
        "label": "自由创作",
        "short_label": "创作",
        "goal": "围绕一个主题自由组合素材、镜头语言和旁白结构。",
        "audience": "个人创作者",
        "tone": "灵活、有表达感",
        "duration_hint": "1-8 分钟",
        "layout_bias": ["full_slide", "split_panel", "case_dialogue", "summary"],
        "visual_strategy": "mixed_media_visual_essay",
        "motion_style": "slow_push",
        "remotion": {
            "theme": "freeform",
            "shot_motion": "slow_push",
            "overlay_density": "medium",
            "evidence_mode": "supporting",
        },
    },
}

LEGACY_PROFILE_ALIASES = {
    "quality": "knowledge",
    "training": "workflow",
    "onboarding": "workflow",
    "sop": "workflow",
    "sales": "product",
}


def normalize_video_profile_id(value: Any) -> str:
    profile_id = str(value or "").strip().lower()
    profile_id = LEGACY_PROFILE_ALIASES.get(profile_id, profile_id)
    return profile_id if profile_id in VIDEO_PROFILES else DEFAULT_VIDEO_PROFILE_ID


def video_profile(value: Any) -> dict[str, Any]:
    return dict(VIDEO_PROFILES[normalize_video_profile_id(value)])
