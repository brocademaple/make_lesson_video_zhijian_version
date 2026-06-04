"""Video intent profiles shared by the web UI, director and Remotion adapter."""

from __future__ import annotations

from typing import Any


DEFAULT_VIDEO_PROFILE_ID = "quality"


VIDEO_PROFILES: dict[str, dict[str, Any]] = {
    "quality": {
        "id": "quality",
        "label": "规则质检片",
        "short_label": "质检",
        "goal": "把制度、处罚、金额、边界条件讲清楚，帮助学员快速识别风险点。",
        "audience": "质检、合规、新入职运营人员",
        "tone": "准确、克制、保留证据来源",
        "duration_hint": "3-5 分钟",
        "layout_bias": ["rule_card", "split_panel", "case_dialogue", "summary"],
        "visual_strategy": "source_slide_evidence_with_risk_callouts",
        "motion_style": "audit_focus",
        "remotion": {
            "theme": "audit",
            "shot_motion": "slow_push",
            "overlay_density": "high",
            "evidence_mode": "required",
        },
    },
    "onboarding": {
        "id": "onboarding",
        "label": "新人速训片",
        "short_label": "新人",
        "goal": "把陌生术语、关键流程和易错点讲成能跟上的入门课程。",
        "audience": "新人、转岗人员、实习培训对象",
        "tone": "清楚、友好、节奏稳",
        "duration_hint": "5-8 分钟",
        "layout_bias": ["full_slide", "split_panel", "summary"],
        "visual_strategy": "guided_walkthrough_with_terms",
        "motion_style": "guided_steps",
        "remotion": {
            "theme": "coach",
            "shot_motion": "gentle_pan",
            "overlay_density": "medium",
            "evidence_mode": "supporting",
        },
    },
    "sop": {
        "id": "sop",
        "label": "SOP 操作片",
        "short_label": "SOP",
        "goal": "把流程步骤拆成动作序列，突出先后顺序、检查点和交付物。",
        "audience": "一线执行人员、流程负责人",
        "tone": "直接、动作导向、少铺垫",
        "duration_hint": "4-6 分钟",
        "layout_bias": ["split_panel", "full_slide", "summary"],
        "visual_strategy": "step_by_step_action_board",
        "motion_style": "process_slide",
        "remotion": {
            "theme": "process",
            "shot_motion": "horizontal_track",
            "overlay_density": "medium",
            "evidence_mode": "light",
        },
    },
    "sales": {
        "id": "sales",
        "label": "销售赋能片",
        "short_label": "赋能",
        "goal": "把卖点、异议处理和案例亮点剪成可复用的销售讲解素材。",
        "audience": "销售、客户成功、区域培训负责人",
        "tone": "聚焦价值、强调案例和话术",
        "duration_hint": "3-6 分钟",
        "layout_bias": ["case_dialogue", "split_panel", "summary"],
        "visual_strategy": "case_value_highlight_reel",
        "motion_style": "spotlight",
        "remotion": {
            "theme": "spotlight",
            "shot_motion": "spotlight_reveal",
            "overlay_density": "medium",
            "evidence_mode": "supporting",
        },
    },
}


def normalize_video_profile_id(value: Any) -> str:
    profile_id = str(value or "").strip().lower()
    return profile_id if profile_id in VIDEO_PROFILES else DEFAULT_VIDEO_PROFILE_ID


def video_profile(value: Any) -> dict[str, Any]:
    return dict(VIDEO_PROFILES[normalize_video_profile_id(value)])
