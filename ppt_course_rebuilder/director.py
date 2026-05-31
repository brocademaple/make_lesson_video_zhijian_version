"""导演入口：raw_material_manifest → director_manifest。"""

from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import Any, Optional

from ppt_course_rebuilder.asset_tagger import tag_assets
from ppt_course_rebuilder.director_validator import validate_director_manifest
from ppt_course_rebuilder.llm_client import DirectorLLMClient, configured_model
from ppt_course_rebuilder.llm_director import plan_director_manifest_with_llm
from ppt_course_rebuilder.manifest_reader import read_json, write_json
from ppt_course_rebuilder.models import utc_now_iso
from ppt_course_rebuilder.narration import build_narration
from ppt_course_rebuilder.scene_planner import infer_scene_type, scene_title_for_type
from ppt_course_rebuilder.subtitle import split_subtitle_segments

logger = logging.getLogger(__name__)


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


def _slide_lookup(slides: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for slide in slides:
        idx = int(slide.get("slide_index") or 0)
        sid = str(slide.get("slide_id") or f"slide-{idx:04d}")
        out[sid] = slide
    return out


def _load_course_material(raw_manifest_path: str) -> dict[str, Any]:
    path = Path(raw_manifest_path).with_name("course_material.json")
    if not path.is_file():
        return {}
    try:
        data = read_json(path)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _material_slide_lookup(material: dict[str, Any]) -> dict[str, dict[str, Any]]:
    slides = material.get("slides")
    if not isinstance(slides, list):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for slide in slides:
        if not isinstance(slide, dict):
            continue
        sid = str(slide.get("slide_id") or "")
        if sid:
            out[sid] = slide
    return out


def _source_text_for_ids(
    source_slide_ids: list[str],
    slide_by_id: dict[str, dict[str, Any]],
) -> str:
    parts: list[str] = []
    for sid in source_slide_ids:
        slide = slide_by_id.get(sid)
        if slide:
            txt = str(slide.get("raw_text") or "").strip()
            if txt:
                parts.append(txt)
    return "\n\n".join(parts)


def _source_evidence(source_slide_ids: list[str], slide_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for sid in source_slide_ids:
        slide = slide_by_id.get(sid)
        if not slide:
            continue
        text = " ".join(str(slide.get("raw_text") or "").split())
        if text:
            evidence.append({"slide_id": sid, "quote": text[:240]})
    return evidence


def _material_evidence(source_slide_ids: list[str], material_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for sid in source_slide_ids:
        material = material_by_id.get(sid)
        if not material:
            continue
        for quote in material.get("evidence_texts") or []:
            text = str(quote or "").strip()
            if text:
                evidence.append({"slide_id": sid, "quote": text[:240], "source": "course_material"})
    return evidence


def _risk_items_for_ids(source_slide_ids: list[str], material_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for sid in source_slide_ids:
        material = material_by_id.get(sid)
        if not material:
            continue
        for item in material.get("risk_items") or []:
            if isinstance(item, dict):
                out.append({"slide_id": sid, **item})
    return out[:8]


def _layout_from_material(
    source_slide_ids: list[str],
    material_by_id: dict[str, dict[str, Any]],
    fallback: str,
) -> str:
    for sid in source_slide_ids:
        material = material_by_id.get(sid)
        if not material:
            continue
        layout = str(material.get("recommended_scene_layout") or material.get("recommended_layout") or "").strip()
        if layout:
            return layout
    return fallback


def _overlay_payload(
    *,
    title: str,
    onscreen_text: str,
    screen_design: dict[str, Any],
    source_evidence: list[dict[str, Any]],
    risk_items: list[dict[str, Any]],
    scene_type: str,
) -> dict[str, Any]:
    emphasis = _coerce_string_list(screen_design.get("emphasis"), limit=5)
    callouts = []
    for text in emphasis:
        callouts.append({"label": text, "kind": "emphasis"})
    if not callouts and onscreen_text:
        for part in re.split(r"[。；;\n]", onscreen_text):
            s = " ".join(part.split())
            if s:
                callouts.append({"label": s[:36], "kind": "key_point"})
            if len(callouts) >= 3:
                break
    evidence_quotes = [
        {
            "slide_id": str(item.get("slide_id") or ""),
            "quote": str(item.get("quote") or "")[:180],
        }
        for item in source_evidence[:3]
        if isinstance(item, dict) and str(item.get("quote") or "").strip()
    ]
    return {
        "callouts": callouts[:4],
        "highlights": emphasis[:5],
        "evidence_panel": {
            "title": "原文证据" if evidence_quotes else "",
            "quotes": evidence_quotes,
        },
        "risk_badge": {
            "show": bool(risk_items),
            "label": "需核对原文" if risk_items else "",
            "items": risk_items[:4],
        },
        "transition": {
            "type": "chapter" if scene_type in ("title", "agenda", "summary") else "cut",
            "label": title,
        },
    }


def _coerce_string_list(value: Any, *, limit: int = 8) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        s = str(item or "").strip()
        if s:
            out.append(s)
        if len(out) >= limit:
            break
    return out


def _llm_scene_to_manifest_scene(
    item: dict[str, Any],
    *,
    idx: int,
    task_id: str,
    slide_by_id: dict[str, dict[str, Any]],
    material_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    source_slide_ids = _coerce_string_list(item.get("source_slide_ids"), limit=12)
    if not source_slide_ids:
        fallback_sid = f"slide-{idx:04d}"
        source_slide_ids = [fallback_sid]
    raw_text = _source_text_for_ids(source_slide_ids, slide_by_id)
    scene_type = str(item.get("scene_type") or "explanation")
    title = str(item.get("title") or "").strip() or scene_title_for_type(
        scene_type, "要点讲解", raw_text
    )[0]
    learning_goal = str(item.get("learning_goal") or "").strip() or "掌握本镜头的关键要点。"

    narr = build_narration(raw_text, scene_type)
    tts_text = str(item.get("tts_text") or "").strip() or narr["tts_text"]
    subtitle_text = str(item.get("subtitle_text") or "").strip() or narr["subtitle_text"]
    onscreen_text = str(item.get("onscreen_text") or "").strip() or raw_text[:500]
    dur = _estimate_duration(raw_text, tts_text)
    segments = split_subtitle_segments(subtitle_text, dur)

    screen_design = item.get("screen_design")
    if not isinstance(screen_design, dict):
        screen_design = {}
    screen_design = {
        "layout": _layout_from_material(
            source_slide_ids,
            material_by_id,
            str(screen_design.get("layout") or "full_slide"),
        ),
        "visual_strategy": str(
            screen_design.get("visual_strategy")
            or "use_full_slide_with_caption_and_subtitle"
        ),
        "emphasis": _coerce_string_list(screen_design.get("emphasis"), limit=6)
        or [scene_type],
    }

    scene_id = f"sc-{idx:04d}-{scene_type}"
    content_hash = _sha16(task_id, scene_id, tts_text, onscreen_text)
    asset_hash = _sha16("|".join(source_slide_ids))
    audio_hash = _sha16("", "")
    render_cache_key = _sha16(task_id, scene_id, content_hash, asset_hash)
    risk_flags = _risk_flags(scene_type, raw_text)
    risk_flags.extend(_coerce_string_list(item.get("risk_flags"), limit=8))
    risk_flags = list(dict.fromkeys(risk_flags))
    source_evidence = _material_evidence(source_slide_ids, material_by_id) or _source_evidence(source_slide_ids, slide_by_id)
    scene_risk_items = _risk_items_for_ids(source_slide_ids, material_by_id)
    render_overlays = _overlay_payload(
        title=title,
        onscreen_text=onscreen_text,
        screen_design=screen_design,
        source_evidence=source_evidence,
        risk_items=scene_risk_items,
        scene_type=scene_type,
    )

    return {
        "scene_id": scene_id,
        "scene_type": scene_type,
        "source_slide_ids": source_slide_ids,
        "learning_goal": learning_goal,
        "title": title,
        "onscreen_text": onscreen_text[:2000],
        "narration": str(item.get("narration") or narr["narration"]),
        "tts_text": tts_text,
        "subtitle_text": subtitle_text,
        "content": {
            "title": title,
            "onscreen_text": onscreen_text[:2000],
            "bullets": _coerce_string_list(item.get("bullets"), limit=3),
        },
        "subtitle": {"segments": segments},
        "timing": {"estimated_duration_sec": dur},
        "screen_design": screen_design,
        "render_intent": {
            "style": "enterprise_training",
            "layout": screen_design["layout"],
            "use_source_slide_as_evidence": True,
        },
        "source_evidence": source_evidence,
        "risk_items": scene_risk_items,
        "render_overlays": render_overlays,
        "visual_generation": {
            "mode": "llm_director_v0",
            "notes": "LLM 生成课程导演脚本；真实生图与高级模板后续接入。",
        },
        "review_status": "pending",
        "reject_reason": None,
        "risk_flags": risk_flags,
        "version": "1",
        "content_hash": content_hash,
        "asset_hash": asset_hash,
        "audio_hash": audio_hash,
        "render_cache_key": render_cache_key,
    }


def _build_heuristic_scenes(
    *,
    slides: list[dict[str, Any]],
    task_id: str,
    material: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    scenes_out: list[dict[str, Any]] = []
    slide_by_id = _slide_lookup(slides)
    material_by_id = _material_slide_lookup(material or {})
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
        audio_hash = _sha16("", "")
        scene_id = f"sc-{idx:04d}-{scene_type}"
        render_cache_key = _sha16(task_id, scene_id, content_hash, asset_hash)

        screen_design = {
            "layout": _layout_from_material(
                [slide_id] if slide_id else [f"slide-{idx:04d}"],
                material_by_id,
                "full_slide" if scene_type != "case_dialogue" else "split_panel",
            ),
            "visual_strategy": (
                "overlay_highlights"
                if scene_type in ("rule_explanation", "rule_card")
                else "standard_kinetic_type"
            ),
            "emphasis": [scene_type],
        }
        source_ids = [slide_id] if slide_id else [f"slide-{idx:04d}"]
        source_evidence = _material_evidence(source_ids, material_by_id) or _source_evidence(source_ids, slide_by_id)
        scene_risk_items = _risk_items_for_ids(source_ids, material_by_id)
        render_overlays = _overlay_payload(
            title=card_title,
            onscreen_text=raw_text[:2000] if raw_text else "",
            screen_design=screen_design,
            source_evidence=source_evidence,
            risk_items=scene_risk_items,
            scene_type=scene_type,
        )

        scene = {
            "scene_id": scene_id,
            "scene_type": scene_type,
            "source_slide_ids": source_ids,
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
            "render_intent": {
                "style": "enterprise_training",
                "layout": screen_design["layout"],
                "use_source_slide_as_evidence": True,
            },
            "source_evidence": source_evidence,
            "risk_items": scene_risk_items,
            "render_overlays": render_overlays,
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
    return scenes_out


def rebuild_course_from_raw_manifest(
    raw_manifest_path: str,
    output_path: str,
    options: Optional[dict] = None,
) -> dict[str, Any]:
    """
    读取 raw_material_manifest.json，生成 director_manifest.json。
    返回 director_manifest dict。
    """
    opts = options or {}
    raw = read_json(raw_manifest_path)

    assets_dicts = tag_assets(raw)
    assets = assets_dicts

    slides = raw.get("slides") or []
    task_id = str(raw.get("task_id") or "")
    filename_hint = Path(str(raw.get("source_pptx") or "课程")).stem
    material = _load_course_material(raw_manifest_path)
    material_by_id = _material_slide_lookup(material)

    planning_mode = "heuristic_v1"
    llm_error = ""
    llm_data: dict[str, Any] | None = None
    use_llm = bool(opts.get("use_llm", True))
    if use_llm:
        try:
            client = opts.get("llm_client")
            if client is None:
                client = DirectorLLMClient()
            if not getattr(client, "available", False):
                raise RuntimeError("未配置可用 LLM client")
            max_slides = int(opts.get("llm_max_slides") or max(1, len(slides)))
            llm_data = plan_director_manifest_with_llm(
                raw,
                client=client,
                max_slides=max_slides,
            )
            slide_by_id = _slide_lookup(slides)
            scenes_out = [
                _llm_scene_to_manifest_scene(
                    item,
                    idx=i,
                    task_id=task_id,
                    slide_by_id=slide_by_id,
                    material_by_id=material_by_id,
                )
                for i, item in enumerate(llm_data.get("scenes") or [])
                if isinstance(item, dict)
            ]
            if not scenes_out:
                raise ValueError("LLM 未生成有效 scenes")
            planning_mode = "llm_director_v0"
        except Exception as e:
            llm_error = str(e)
            logger.warning("LLM 导演规划失败，回退启发式：%s", e)
            scenes_out = _build_heuristic_scenes(slides=slides, task_id=task_id, material=material)
    else:
        scenes_out = _build_heuristic_scenes(slides=slides, task_id=task_id, material=material)

    pending = sum(
        1 for s in scenes_out if s.get("review_status") == "pending"
    )
    course_from_llm = (llm_data or {}).get("course") if isinstance(llm_data, dict) else None
    if not isinstance(course_from_llm, dict):
        course_from_llm = {}
    course_outline = (llm_data or {}).get("course_outline") if isinstance(llm_data, dict) else None
    if not isinstance(course_outline, list):
        course_outline = [
            {
                "order": i + 1,
                "title": str(scene.get("title") or f"镜头 {i + 1}"),
                "source_scene_id": str(scene.get("scene_id") or ""),
            }
            for i, scene in enumerate(scenes_out)
        ]
    chapters = (llm_data or {}).get("chapters") if isinstance(llm_data, dict) else None
    if not isinstance(chapters, list):
        chapters = [
            {
                "chapter_id": "ch-0001",
                "title": str(course_from_llm.get("title") or filename_hint or "课程"),
                "scene_ids": [str(s.get("scene_id") or "") for s in scenes_out],
            }
        ]

    dm = {
        "task_id": task_id,
        "course": {
            "title": str(course_from_llm.get("title") or filename_hint or "课程"),
            "audience": str(course_from_llm.get("audience") or "内部培训"),
            "goal": str(
                course_from_llm.get("goal") or "完成本节关键知识点与执行口径的讲解"
            ),
            "version": "1",
        },
        "assets": assets,
        "course_outline": course_outline,
        "chapters": chapters,
        "render_intent": {
            "style": "enterprise_internal_training",
            "visual_policy": "source_slide_first_with_light_callouts",
            "layouts_supported": [
                "full_slide",
                "rule_card",
                "split_panel",
                "case_dialogue",
                "summary",
            ],
        },
        "scenes": scenes_out,
        "review": {
            "pending_count": pending,
            "approved_count": 0,
            "rejected_count": 0,
            "notes": "",
        },
        "generation": {
            "planning_mode": planning_mode,
            "llm_model": configured_model() if planning_mode.startswith("llm") else "",
            "llm_error": llm_error,
            "material_source": "course_material.json" if material else "",
        },
        "generated_at": utc_now_iso(),
    }
    dm["quality_checks"] = validate_director_manifest(dm, raw)

    out_p = Path(output_path)
    write_json(out_p, dm)
    return dm
