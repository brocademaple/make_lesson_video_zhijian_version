"""Adapt approved DirectorManifest scenes into Remotion render props."""

from __future__ import annotations

import math
from collections import Counter
from pathlib import Path
from typing import Any

from ppt_course_deal.audio_workspace_store import load_meta, resolve_workspace_audio_path
from ppt_course_deal.remotion_input_props import (
    create_render_task,
    rel_for_props,
    render_command_for_task,
    render_task_paths,
    repo_root,
    safe_render_task_name,
    summarize_props,
)
from ppt_course_deal.task_storage import get_data_root
from ppt_course_rebuilder.manifest_reader import read_json, write_json


def _slide_index_from_id(slide_id: str) -> int:
    try:
        return int(str(slide_id).rsplit("-", 1)[-1])
    except (TypeError, ValueError):
        return 0


def _duration_frames(scene: dict[str, Any], fps: int, fallback: int) -> int:
    timing = scene.get("timing")
    sec = timing.get("estimated_duration_sec") if isinstance(timing, dict) else None
    if isinstance(sec, (int, float)) and sec > 0:
        return max(1, math.ceil(float(sec) * fps))
    return fallback


def _clean_text(value: Any, *, limit: int = 180) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def _screen_layout(scene: dict[str, Any]) -> str:
    screen_design = scene.get("screen_design")
    if isinstance(screen_design, dict):
        layout = str(screen_design.get("layout") or "").strip()
        if layout:
            return layout
    return "full_slide"


def _subtitle_segments(scene: dict[str, Any]) -> list[dict[str, Any]]:
    subtitle = scene.get("subtitle")
    segments = subtitle.get("segments") if isinstance(subtitle, dict) else None
    if isinstance(segments, list) and segments:
        out = []
        for item in segments:
            if not isinstance(item, dict):
                continue
            text = _clean_text(item.get("text"), limit=120)
            if text:
                out.append(
                    {
                        "start_sec": item.get("start_sec", item.get("start")),
                        "end_sec": item.get("end_sec", item.get("end")),
                        "text": text,
                    }
                )
        if out:
            return out
    fallback = _clean_text(scene.get("subtitle_text") or scene.get("tts_text"), limit=120)
    return [{"start_sec": 0, "text": fallback}] if fallback else []


def _overlay(scene: dict[str, Any], key: str, fallback: Any) -> Any:
    overlays = scene.get("render_overlays")
    if isinstance(overlays, dict) and key in overlays:
        return overlays.get(key)
    return fallback


def _callouts(scene: dict[str, Any]) -> list[dict[str, str]]:
    raw = _overlay(scene, "callouts", [])
    if isinstance(raw, list):
        out: list[dict[str, str]] = []
        for item in raw[:4]:
            if isinstance(item, dict):
                label = _clean_text(item.get("label") or item.get("text"), limit=42)
                kind = _clean_text(item.get("kind") or "key_point", limit=24)
            else:
                label = _clean_text(item, limit=42)
                kind = "key_point"
            if label:
                out.append({"label": label, "kind": kind})
        if out:
            return out
    onscreen = _clean_text(scene.get("onscreen_text"), limit=160)
    if not onscreen:
        return []
    return [{"label": part[:42], "kind": "key_point"} for part in onscreen.split("。") if part][:3]


def _evidence_panel(scene: dict[str, Any]) -> dict[str, Any]:
    panel = _overlay(scene, "evidence_panel", {})
    if not isinstance(panel, dict):
        panel = {}
    quotes = panel.get("quotes")
    if not isinstance(quotes, list):
        quotes = scene.get("source_evidence") if isinstance(scene.get("source_evidence"), list) else []
    clean_quotes: list[dict[str, str]] = []
    for item in quotes[:3]:
        if not isinstance(item, dict):
            continue
        quote = _clean_text(item.get("quote"), limit=120)
        if quote:
            clean_quotes.append(
                {
                    "slide_id": str(item.get("slide_id") or ""),
                    "quote": quote,
                }
            )
    return {"title": str(panel.get("title") or "原文证据") if clean_quotes else "", "quotes": clean_quotes}


def _risk_badge(scene: dict[str, Any]) -> dict[str, Any]:
    badge = _overlay(scene, "risk_badge", {})
    if not isinstance(badge, dict):
        badge = {}
    items = badge.get("items")
    if not isinstance(items, list):
        items = scene.get("risk_items") if isinstance(scene.get("risk_items"), list) else []
    clean_items: list[dict[str, Any]] = []
    for item in items[:4]:
        if not isinstance(item, dict):
            continue
        clean_items.append(
            {
                "risk_type": str(item.get("risk_type") or ""),
                "quote": _clean_text(item.get("quote"), limit=90),
                "numbers": item.get("numbers") if isinstance(item.get("numbers"), list) else [],
                "slide_id": str(item.get("slide_id") or ""),
            }
        )
    return {
        "show": bool(clean_items or scene.get("risk_flags")),
        "label": str(badge.get("label") or "需核对原文"),
        "items": clean_items,
    }


def _transition(scene: dict[str, Any], index: int) -> dict[str, str]:
    transition = _overlay(scene, "transition", {})
    if not isinstance(transition, dict):
        transition = {}
    transition_type = str(transition.get("type") or ("chapter" if index == 0 else "cut"))
    return {
        "type": transition_type,
        "label": _clean_text(transition.get("label") or scene.get("title"), limit=48),
    }


def _render_profile(scene: dict[str, Any], manifest_profile: dict[str, Any]) -> dict[str, Any]:
    overlays = scene.get("render_overlays")
    raw = overlays.get("render_profile") if isinstance(overlays, dict) else None
    if isinstance(raw, dict) and raw.get("id"):
        return raw
    return {
        "id": str(manifest_profile.get("id") or ""),
        "label": str(manifest_profile.get("label") or ""),
        "motion_style": str(manifest_profile.get("motion_style") or ""),
        "visual_strategy": str(manifest_profile.get("visual_strategy") or ""),
        "remotion": manifest_profile.get("remotion") if isinstance(manifest_profile.get("remotion"), dict) else {},
    }


def _shape_relatives(task_root: Path, slide_index: int, root: Path) -> list[str]:
    shapes_dir = task_root / "previews" / f"slide-{slide_index:04d}" / "shapes"
    if not shapes_dir.is_dir():
        return []
    return [rel_for_props(p, root) for p in sorted(shapes_dir.glob("shape-*.png"))[:6]]


def _layout_counts(slides: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(str(slide.get("layout") or "full_slide") for slide in slides))


def _audio_for_slide(task_id: str, slide_index: int, *, fps: int) -> tuple[list[str], list[int]]:
    meta = load_meta("task", task_id)
    durations = meta.get("segment_duration_sec")
    if not isinstance(durations, dict):
        durations = {}
    audio_rels: list[str] = []
    segment_frames: list[int] = []
    j = 0
    root = repo_root()
    while True:
        ap = resolve_workspace_audio_path("task", task_id, slide_index, j, "mp3")
        if ap is None or not ap.is_file():
            break
        audio_rels.append(rel_for_props(ap, root))
        raw_sec = durations.get(f"{slide_index}-{j}")
        if isinstance(raw_sec, (int, float)) and raw_sec > 0:
            segment_frames.append(max(1, math.ceil(float(raw_sec) * fps)))
        j += 1
        if j > 500:
            break
    return audio_rels, segment_frames


def _scene_plan_entries(
    director_manifest: dict[str, Any],
    *,
    props_slides: list[dict[str, Any]] | None = None,
    max_scenes: int | None = None,
) -> list[dict[str, Any]]:
    raw_scenes = director_manifest.get("scenes") or []
    if max_scenes is not None:
        raw_scenes = raw_scenes[:max_scenes]
    entries: list[dict[str, Any]] = []
    for idx, scene in enumerate(raw_scenes):
        if not isinstance(scene, dict):
            continue
        prop_slide = props_slides[idx] if props_slides and idx < len(props_slides) else {}
        entries.append(
            {
                "scene_id": str(scene.get("scene_id") or ""),
                "source_slide_ids": scene.get("source_slide_ids") or [],
                "layout": str(prop_slide.get("layout") or _screen_layout(scene)),
                "title": str(scene.get("title") or ""),
                "durationInFrames": prop_slide.get("durationInFrames", 0),
                "audio_segment_count": len(prop_slide.get("audioRelatives") or []),
                "callouts": prop_slide.get("callouts") or [],
                "evidence_panel": prop_slide.get("evidencePanel") or {},
                "risk_badge": prop_slide.get("riskBadge") or {},
                "risk_flags": prop_slide.get("riskFlags") or [],
                "transition": prop_slide.get("transition") or {},
                "render_profile": prop_slide.get("renderProfile") or {},
            }
        )
    return entries


def director_manifest_to_props(
    task_id: str,
    director_manifest: dict[str, Any],
    *,
    fps: int = 30,
    no_audio_frames: int = 90,
    max_scenes: int | None = None,
) -> dict[str, Any]:
    task_root = get_data_root() / "tasks" / task_id
    slides: list[dict[str, Any]] = []
    raw_scenes = director_manifest.get("scenes") or []
    if max_scenes is not None:
        raw_scenes = raw_scenes[:max_scenes]
    root = repo_root()
    total_scenes = sum(1 for scene in raw_scenes if isinstance(scene, dict))
    manifest_intent = director_manifest.get("render_intent")
    manifest_profile = {}
    if isinstance(manifest_intent, dict) and isinstance(manifest_intent.get("profile"), dict):
        manifest_profile = manifest_intent["profile"]
    for scene_index, scene in enumerate(raw_scenes):
        if not isinstance(scene, dict):
            continue
        source_ids = scene.get("source_slide_ids")
        source_id = str(source_ids[0]) if isinstance(source_ids, list) and source_ids else f"slide-{scene_index:04d}"
        slide_index = _slide_index_from_id(source_id)
        full = task_root / "previews" / f"slide-{slide_index:04d}" / "full.png"
        if not full.is_file():
            raise ValueError(f"缺少整页预览：{full}")

        audio_rels, segment_frames = _audio_for_slide(task_id, slide_index, fps=fps)
        frames = sum(segment_frames) if segment_frames else _duration_frames(scene, fps, no_audio_frames)
        layout = _screen_layout(scene)
        caption = {
            "title": str(scene.get("title") or f"第 {slide_index + 1} 页"),
            "subtitle": str(scene.get("subtitle_text") or scene.get("onscreen_text") or "")[:140],
        }
        slide_obj: dict[str, Any] = {
            "imageRelative": rel_for_props(full, root),
            "shapeRelatives": _shape_relatives(task_root, slide_index, root),
            "durationInFrames": frames,
            "caption": caption,
            "sceneId": str(scene.get("scene_id") or f"sc-{scene_index:04d}"),
            "layout": layout,
            "onscreenText": _clean_text(scene.get("onscreen_text"), limit=360),
            "subtitleSegments": _subtitle_segments(scene),
            "callouts": _callouts(scene),
            "highlights": _overlay(scene, "highlights", []),
            "evidencePanel": _evidence_panel(scene),
            "riskBadge": _risk_badge(scene),
            "riskFlags": scene.get("risk_flags") if isinstance(scene.get("risk_flags"), list) else [],
            "transition": _transition(scene, scene_index),
            "renderProfile": _render_profile(scene, manifest_profile),
            "progress": {"index": scene_index + 1, "total": total_scenes},
            "sourceEvidence": scene.get("source_evidence") if isinstance(scene.get("source_evidence"), list) else [],
            "sourceSlideIds": source_ids if isinstance(source_ids, list) else [source_id],
        }
        if audio_rels:
            slide_obj["audioRelatives"] = audio_rels
            slide_obj["audioSegmentDurationInFrames"] = segment_frames
        slides.append(slide_obj)
    return {"fps": fps, "videoProfile": manifest_profile, "slides": slides}


def write_render_plan_from_task(
    task_id: str,
    *,
    fps: int = 30,
    no_audio_frames: int = 90,
    max_scenes: int | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    task_root = get_data_root() / "tasks" / task_id
    approved = task_root / "approved_director_manifest.json"
    director = task_root / "director_manifest.json"
    source_path = approved if approved.is_file() else director
    if not source_path.is_file():
        fallback = create_render_task(
            task_id,
            fps=fps,
            max_slides=max_scenes,
            no_audio_frames=no_audio_frames,
            root=root,
        )
        return {"source": "fallback_deal_props", "render_plan_path": "", **fallback}

    manifest = read_json(source_path)
    props = director_manifest_to_props(
        task_id,
        manifest,
        fps=fps,
        no_audio_frames=no_audio_frames,
        max_scenes=max_scenes,
    )
    paths = render_task_paths(task_id, root=root)
    paths["output_video"].parent.mkdir(parents=True, exist_ok=True)
    write_json(paths["input_props"], props)
    plan = {
        "schema_version": "render_plan.v1",
        "task_id": task_id,
        "source": "approved_director_manifest" if source_path == approved else "director_manifest",
        "source_manifest_path": str(source_path),
        "task_name": safe_render_task_name(task_id),
        "input_props_path": str(paths["input_props"]),
        "output_video_path": str(paths["output_video"]),
        "render_command": render_command_for_task(task_id, root=root),
        "props_summary": summarize_props(props),
        "video_profile": props.get("videoProfile") or {},
        "scene_count": len(props.get("slides") or []),
        "layout_counts": _layout_counts(props.get("slides") or []),
        "risk_scene_count": sum(1 for slide in props.get("slides") or [] if (slide.get("riskBadge") or {}).get("show")),
        "scenes": _scene_plan_entries(manifest, props_slides=props.get("slides") or [], max_scenes=max_scenes),
    }
    render_plan_path = paths["task_dir"] / "render_plan.json"
    write_json(render_plan_path, plan)
    return {
        "source": plan["source"],
        "render_plan_path": str(render_plan_path),
        "task_name": plan["task_name"],
        "task_dir": str(paths["task_dir"]),
        "input_props_path": str(paths["input_props"]),
        "output_video_path": str(paths["output_video"]),
        "render_command": plan["render_command"],
        "scene_count": plan["scene_count"],
        "layout_counts": plan["layout_counts"],
        "risk_scene_count": plan["risk_scene_count"],
        **plan["props_summary"],
    }
