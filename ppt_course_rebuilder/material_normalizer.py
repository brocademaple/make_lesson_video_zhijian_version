"""Normalize Deal outputs into a course-level material contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ppt_course_rebuilder.manifest_reader import read_json, write_json
from ppt_course_rebuilder.material_tagger import (
    asset_role,
    evidence_texts,
    infer_layout,
    material_role,
    risk_items,
    tag_asset,
    tag_slide_text,
    teaching_purpose,
)
from ppt_course_rebuilder.models import utc_now_iso


def _read_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _task_audio_meta(task_root: Path, task_id: str) -> dict[str, Any]:
    data_root = task_root.parent.parent
    return _read_json_if_exists(data_root / "audio_workspace" / "task" / task_id / "meta.json")


def _latest_generated_visual(task_root: Path, slide_index: int) -> str:
    root = task_root / "generated_visuals" / f"slide-{slide_index:04d}"
    if not root.is_dir():
        return ""
    candidates = [p for p in root.glob("*.png") if p.is_file()]
    if not candidates:
        return ""
    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    return str(latest)


def _audio_segments_for_slide(
    audio_meta: dict[str, Any],
    *,
    slide_index: int,
) -> list[dict[str, Any]]:
    generated = audio_meta.get("generated_files")
    durations = audio_meta.get("segment_duration_sec")
    transcripts = audio_meta.get("transcript_segments")
    if not isinstance(generated, dict):
        generated = {}
    if not isinstance(durations, dict):
        durations = {}
    if not isinstance(transcripts, list):
        transcripts = []

    out: list[dict[str, Any]] = []
    slide_transcripts = transcripts[slide_index] if slide_index < len(transcripts) else []
    if not isinstance(slide_transcripts, list):
        slide_transcripts = []
    for segment_index, text in enumerate(slide_transcripts):
        key = f"{slide_index}-{segment_index}"
        rel = generated.get(key)
        sec = durations.get(key)
        out.append(
            {
                "slide_index": slide_index,
                "segment_index": segment_index,
                "text": str(text or ""),
                "audio_relative": str(rel or ""),
                "duration_sec": float(sec) if isinstance(sec, (int, float)) else None,
            }
        )
    return out


def build_course_material(
    raw_manifest_path: str | Path,
    output_path: str | Path | None = None,
    *,
    use_llm: bool = False,
    llm_client: Any | None = None,
    llm_max_slides: int = 40,
) -> dict[str, Any]:
    raw = read_json(raw_manifest_path)
    task_id = str(raw.get("task_id") or "")
    task_root = Path(str(raw.get("task_root") or Path(raw_manifest_path).parent))
    task_meta = _read_json_if_exists(task_root / "meta.json")
    audio_meta = _task_audio_meta(task_root, task_id) if task_id else {}
    slides = raw.get("slides") if isinstance(raw.get("slides"), list) else []
    slide_count = len(slides)

    normalized_slides: list[dict[str, Any]] = []
    all_assets: list[dict[str, Any]] = []
    for fallback_index, slide in enumerate(slides):
        if not isinstance(slide, dict):
            continue
        slide_index = int(slide.get("slide_index") or fallback_index)
        slide_id = str(slide.get("slide_id") or f"slide-{slide_index:04d}")
        raw_text = str(slide.get("raw_text") or "")
        tags = tag_slide_text(raw_text, slide_index=slide_index, slide_count=slide_count)
        shapes = slide.get("shapes") if isinstance(slide.get("shapes"), list) else []
        asset_refs: list[dict[str, Any]] = []

        full_page_png = str(slide.get("full_page_png") or "")
        if full_page_png:
            full_asset = {
                "asset_id": f"{slide_id}:full",
                "source_slide_id": slide_id,
                "path": full_page_png,
                "asset_type": "full_slide_png",
                "semantic_tags": ["full_slide", *tags],
            }
            full_asset["asset_role"] = asset_role(full_asset)
            asset_refs.append(full_asset)
            all_assets.append(full_asset)

        for i, shape in enumerate(shapes):
            if not isinstance(shape, dict):
                continue
            asset = {
                "asset_id": str(shape.get("shape_id") or f"{slide_id}:shape:{i}"),
                "source_slide_id": slide_id,
                "path": str(shape.get("image_path") or ""),
                "asset_type": "shape_png",
                "ocr_text": str(shape.get("ocr_text") or ""),
                "semantic_tags": tag_asset(shape),
            }
            asset["asset_role"] = asset_role(asset)
            asset_refs.append(asset)
            all_assets.append(asset)

        generated_visual = _latest_generated_visual(task_root, slide_index)
        if generated_visual:
            generated_asset = {
                "asset_id": f"{slide_id}:generated_visual",
                "source_slide_id": slide_id,
                "path": generated_visual,
                "asset_type": "generated_visual_png",
                "semantic_tags": ["generated_visual"],
            }
            generated_asset["asset_role"] = "ai_generated_visual"
            asset_refs.append(generated_asset)
            all_assets.append(generated_asset)

        slide_risk_items = risk_items(raw_text)
        slide_evidence = evidence_texts(raw_text)
        asset_roles = sorted(
            {
                str(asset.get("asset_role") or "supporting_asset")
                for asset in asset_refs
                if isinstance(asset, dict)
            }
        )
        recommended_layout = infer_layout(tags)

        normalized_slides.append(
            {
                "slide_id": slide_id,
                "slide_index": slide_index,
                "title": _slide_title(task_meta, slide_index, raw_text),
                "raw_text": raw_text,
                "speaker_notes": str(slide.get("speaker_notes") or ""),
                "full_page_png": full_page_png,
                "material_tags": tags,
                "material_role": material_role(tags),
                "teaching_purpose": teaching_purpose(tags),
                "asset_roles": asset_roles,
                "risk_items": slide_risk_items,
                "evidence_texts": slide_evidence,
                "recommended_scene_layout": recommended_layout,
                "recommended_layout": recommended_layout,
                "assets": asset_refs,
                "audio_segments": _audio_segments_for_slide(
                    audio_meta,
                    slide_index=slide_index,
                ),
            }
        )

    material = {
        "schema_version": "course_material.v1",
        "task_id": task_id,
        "source_pptx": str(raw.get("source_pptx") or ""),
        "task_root": str(task_root),
        "course": {
            "title": str(task_meta.get("filename") or Path(str(raw.get("source_pptx") or "课程")).stem),
            "audience": "内部培训",
            "goal": "将 PPT 素材整理为可审核、可渲染的培训视频导演脚本。",
        },
        "slides": normalized_slides,
        "assets": all_assets,
        "audio": {
            "has_workspace": bool(audio_meta),
            "generated_segment_count": len(audio_meta.get("generated_files") or {})
            if isinstance(audio_meta.get("generated_files"), dict)
            else 0,
        },
        "generated_at": utc_now_iso(),
    }
    if use_llm:
        material = _maybe_enrich_with_llm(
            material,
            client=llm_client,
            max_slides=llm_max_slides,
        )
    if output_path is not None:
        write_json(output_path, material)
    return material


def _slide_title(task_meta: dict[str, Any], slide_index: int, raw_text: str) -> str:
    slides = task_meta.get("slides")
    if isinstance(slides, list) and slide_index < len(slides):
        slide = slides[slide_index]
        if isinstance(slide, dict):
            title = str(slide.get("title") or "").strip()
            if title:
                return title
    first_line = str(raw_text or "").strip().splitlines()
    return first_line[0][:80] if first_line else f"第 {slide_index + 1} 页"


def _maybe_enrich_with_llm(
    material: dict[str, Any],
    *,
    client: Any | None = None,
    max_slides: int = 40,
) -> dict[str, Any]:
    """Optional Director LLM enhancement; failure keeps deterministic tags."""

    try:
        from ppt_course_rebuilder.llm_client import DirectorLLMClient, configured_model

        llm = client or DirectorLLMClient()
        if not getattr(llm, "available", False):
            material["llm_enhancement"] = {
                "status": "skipped",
                "reason": "director_llm_not_configured",
            }
            return material
        slides = material.get("slides") if isinstance(material.get("slides"), list) else []
        compact = [
            {
                "slide_id": slide.get("slide_id"),
                "title": slide.get("title"),
                "raw_text": str(slide.get("raw_text") or "")[:1000],
                "material_tags": slide.get("material_tags") or [],
                "asset_roles": slide.get("asset_roles") or [],
                "risk_items": slide.get("risk_items") or [],
            }
            for slide in slides[:max_slides]
            if isinstance(slide, dict)
        ]
        system = (
            "你是企业培训视频的素材理解导演。只输出 JSON object。"
            "不要编造原文没有的规则、金额或处罚。"
        )
        user = (
            "请为每页 PPT 素材补充更准确的 material_role、teaching_purpose、"
            "recommended_scene_layout、asset_roles、evidence_texts。"
            "输出格式：{\"slides\":[{\"slide_id\":\"...\",\"material_role\":\"...\","
            "\"teaching_purpose\":\"...\",\"recommended_scene_layout\":\"full_slide|rule_card|split_panel|case_dialogue|summary\","
            "\"asset_roles\":[\"...\"],\"evidence_texts\":[\"...\"]}]}。\n"
            + json.dumps({"slides": compact}, ensure_ascii=False)
        )
        data = llm.call_json(system=system, user=user, temperature=0.1)
        enriched = data.get("slides")
        if not isinstance(enriched, list):
            raise ValueError("LLM material 输出缺少 slides")
        by_id = {
            str(item.get("slide_id") or ""): item
            for item in enriched
            if isinstance(item, dict)
        }
        for slide in slides:
            if not isinstance(slide, dict):
                continue
            item = by_id.get(str(slide.get("slide_id") or ""))
            if not item:
                continue
            for key in ("material_role", "teaching_purpose", "recommended_scene_layout"):
                val = str(item.get(key) or "").strip()
                if val:
                    slide[key] = val
                    if key == "recommended_scene_layout":
                        slide["recommended_layout"] = val
            for key in ("asset_roles", "evidence_texts"):
                val = item.get(key)
                if isinstance(val, list) and val:
                    slide[key] = [str(x).strip() for x in val if str(x).strip()][:8]
        material["llm_enhancement"] = {
            "status": "applied",
            "model": configured_model(),
            "slide_count": len(by_id),
        }
    except Exception as exc:
        material["llm_enhancement"] = {
            "status": "fallback_rules",
            "reason": str(exc),
        }
    return material
