"""导演入口：raw_material_manifest → director_manifest。"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Optional

from ppt_course_rebuilder.asset_tagger import tag_assets
from ppt_course_rebuilder.manifest_reader import read_json, write_json
from ppt_course_rebuilder.models import utc_now_iso
from ppt_course_rebuilder.narration import build_narration
from ppt_course_rebuilder.scene_planner import infer_scene_type, scene_title_for_type
from ppt_course_rebuilder.subtitle import split_subtitle_segments


def _sha16(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8"))
        h.update(b"|")
    return h.hexdigest()[:16]


def _estimate_duration(raw_text: str, tts_text: str) -> float:
    base = len((tts_text or raw_text or "")) / 8.0
    return float(max(8.0, min(180.0, base + 6.0)))


def _risk_flags(scene_type: str, raw_text: str) -> list[str]:
    flags: list[str] = []
    if scene_type in ("rule_explanation", "rule_card"):
        flags.append("compliance_sensitive")
    if re.search(r"(罚款|扣除|处罚|元)", raw_text or ""):
        flags.append("contains_penalty_or_amount")
    return flags


def rebuild_course_from_raw_manifest(
    raw_manifest_path: str,
    output_path: str,
    options: Optional[dict] = None,
) -> dict[str, Any]:
    """
    读取 raw_material_manifest.json，生成 director_manifest.json。
    返回 director_manifest dict。
    """
    _ = options
    raw = read_json(raw_manifest_path)

    assets_dicts = tag_assets(raw)
    assets = assets_dicts

    slides = raw.get("slides") or []
    task_id = str(raw.get("task_id") or "")
    filename_hint = Path(str(raw.get("source_pptx") or "课程")).stem

    scenes_out: list[dict[str, Any]] = []
    for slide in slides:
        slide_id = str(slide.get("slide_id") or "")
        idx = int(slide.get("slide_index") or 0)
        raw_text = str(slide.get("raw_text") or "").strip()
        title_hint = ""
        if raw_text:
            title_hint = raw_text.split("\n", 1)[0][:80]

        scene_type = infer_scene_type(raw_text, idx, title_hint=title_hint)
        card_title, learning_goal = scene_title_for_type(
            scene_type, title_hint or f"第 {idx + 1} 页", raw_text
        )

        narr = build_narration(raw_text, scene_type)
        tts_text = narr["tts_text"]
        subtitle_text = narr["subtitle_text"]
        dur = _estimate_duration(raw_text, tts_text)
        segments = split_subtitle_segments(subtitle_text, dur)

        content_hash = _sha16(task_id, slide_id, scene_type, tts_text)
        asset_hash = _sha16(slide_id, str(slide.get("full_page_png") or ""))
        audio_hash = _sha16("", "")  # 尚无音频文件
        scene_id = f"sc-{idx:04d}-{scene_type}"
        render_cache_key = _sha16(task_id, scene_id, content_hash, asset_hash)

        screen_design = {
            "layout": "full_slide" if scene_type != "case_dialogue" else "split_panel",
            "visual_strategy": (
                "overlay_highlights"
                if scene_type in ("rule_explanation", "rule_card")
                else "standard_kinetic_type"
            ),
            "emphasis": [scene_type],
        }

        scene = {
            "scene_id": scene_id,
            "scene_type": scene_type,
            "source_slide_ids": [slide_id] if slide_id else [f"slide-{idx:04d}"],
            "learning_goal": learning_goal,
            "title": card_title,
            "onscreen_text": raw_text[:2000] if raw_text else "",
            "narration": narr["narration"],
            "tts_text": tts_text,
            "subtitle_text": subtitle_text,
            "content": {
                "title": card_title,
                "onscreen_text": raw_text[:2000] if raw_text else "",
                "bullets": [],
            },
            "subtitle": {"segments": segments},
            "timing": {"estimated_duration_sec": dur},
            "screen_design": screen_design,
            "visual_generation": {
                "mode": "heuristic_v1",
                "notes": "未接真实生图 API；后续可替换为 structured prompts。",
            },
            "review_status": "pending",
            "reject_reason": None,
            "risk_flags": _risk_flags(scene_type, raw_text),
            "version": "1",
            "content_hash": content_hash,
            "asset_hash": asset_hash,
            "audio_hash": audio_hash,
            "render_cache_key": render_cache_key,
        }
        scenes_out.append(scene)

    pending = sum(
        1 for s in scenes_out if s.get("review_status") == "pending"
    )
    dm = {
        "task_id": task_id,
        "course": {
            "title": filename_hint or "课程",
            "audience": "内部培训",
            "goal": "完成本节关键知识点与执行口径的讲解",
            "version": "1",
        },
        "assets": assets,
        "scenes": scenes_out,
        "review": {
            "pending_count": pending,
            "approved_count": 0,
            "rejected_count": 0,
            "notes": "",
        },
        "generated_at": utc_now_iso(),
    }

    out_p = Path(output_path)
    write_json(out_p, dm)
    return dm
