"""Normalize Deal outputs into a course-level material contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ppt_course_rebuilder.manifest_reader import read_json, write_json
from ppt_course_rebuilder.material_tagger import (
    infer_layout,
    material_role,
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
            asset_refs.append(generated_asset)
            all_assets.append(generated_asset)

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
                "recommended_layout": infer_layout(tags),
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
