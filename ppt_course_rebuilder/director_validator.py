"""Validation helpers for DirectorManifest v2."""

from __future__ import annotations

import re
from typing import Any


def _slides_by_id(material_or_raw: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    slides = material_or_raw.get("slides")
    if not isinstance(slides, list):
        return out
    for slide in slides:
        if not isinstance(slide, dict):
            continue
        sid = str(slide.get("slide_id") or "")
        if sid:
            out[sid] = slide
    return out


def _source_text(scene: dict[str, Any], slides: dict[str, dict[str, Any]]) -> str:
    parts: list[str] = []
    ids = scene.get("source_slide_ids")
    if not isinstance(ids, list):
        return ""
    for sid in ids:
        slide = slides.get(str(sid))
        if not slide:
            continue
        text = str(slide.get("raw_text") or "")
        if text:
            parts.append(text)
    return "\n".join(parts)


def _numbers(text: str) -> set[str]:
    return set(re.findall(r"\d+(?:\.\d+)?", text or ""))


def validate_director_manifest(
    director_manifest: dict[str, Any],
    material_or_raw: dict[str, Any] | None = None,
) -> dict[str, Any]:
    material_or_raw = material_or_raw or {}
    slides = _slides_by_id(material_or_raw)
    slide_ids = set(slides)
    warnings: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    scenes = director_manifest.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        errors.append({"code": "no_scenes", "message": "导演脚本没有 scenes"})
        scenes = []

    for idx, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            errors.append({"code": "invalid_scene", "index": idx, "message": "scene 不是对象"})
            continue
        scene_id = str(scene.get("scene_id") or f"scene[{idx}]")
        source_ids = scene.get("source_slide_ids")
        if not isinstance(source_ids, list) or not source_ids:
            errors.append(
                {"code": "missing_source_slide_ids", "scene_id": scene_id, "message": "缺少 source_slide_ids"}
            )
        else:
            missing = [str(sid) for sid in source_ids if slide_ids and str(sid) not in slide_ids]
            if missing:
                warnings.append(
                    {
                        "code": "source_slide_not_found",
                        "scene_id": scene_id,
                        "missing_slide_ids": missing,
                        "message": "scene 引用的 slide 在素材中不存在",
                    }
                )
        if not str(scene.get("tts_text") or scene.get("narration") or "").strip():
            errors.append({"code": "empty_tts_text", "scene_id": scene_id, "message": "口播为空"})
        timing = scene.get("timing")
        dur = timing.get("estimated_duration_sec") if isinstance(timing, dict) else None
        if not isinstance(dur, (int, float)) or dur <= 0:
            warnings.append({"code": "invalid_duration", "scene_id": scene_id, "message": "预计时长缺失或无效"})

        source_text = _source_text(scene, slides)
        high_risk = bool(
            re.search(r"(罚款|扣除|处罚|元|金额|违约|红线|不得|禁止)", source_text)
            or "contains_penalty_or_amount" in (scene.get("risk_flags") or [])
        )
        if high_risk:
            spoken = " ".join(
                [
                    str(scene.get("tts_text") or ""),
                    str(scene.get("narration") or ""),
                    str(scene.get("subtitle_text") or ""),
                    str(scene.get("onscreen_text") or ""),
                ]
            )
            missing_numbers = sorted(_numbers(source_text) - _numbers(spoken))
            if missing_numbers:
                warnings.append(
                    {
                        "code": "risk_number_missing",
                        "scene_id": scene_id,
                        "numbers": missing_numbers,
                        "message": "高风险规则/金额页中的数字未在导演脚本中完整保留",
                    }
                )

    return {
        "ok": not errors,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }
