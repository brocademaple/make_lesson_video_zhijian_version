"""Adapt approved DirectorManifest scenes into Remotion render props."""

from __future__ import annotations

import math
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


def director_manifest_to_props(
    task_id: str,
    director_manifest: dict[str, Any],
    *,
    fps: int = 30,
    no_audio_frames: int = 90,
) -> dict[str, Any]:
    task_root = get_data_root() / "tasks" / task_id
    slides: list[dict[str, Any]] = []
    for scene_index, scene in enumerate(director_manifest.get("scenes") or []):
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
        caption = {
            "title": str(scene.get("title") or f"第 {slide_index + 1} 页"),
            "subtitle": str(scene.get("subtitle_text") or scene.get("onscreen_text") or "")[:140],
        }
        slide_obj: dict[str, Any] = {
            "imageRelative": rel_for_props(full, repo_root()),
            "durationInFrames": frames,
            "caption": caption,
            "sceneId": str(scene.get("scene_id") or f"sc-{scene_index:04d}"),
            "layout": str((scene.get("screen_design") or {}).get("layout") or "full_slide")
            if isinstance(scene.get("screen_design"), dict)
            else "full_slide",
            "riskFlags": scene.get("risk_flags") if isinstance(scene.get("risk_flags"), list) else [],
        }
        if audio_rels:
            slide_obj["audioRelatives"] = audio_rels
            slide_obj["audioSegmentDurationInFrames"] = segment_frames
        slides.append(slide_obj)
    return {"fps": fps, "slides": slides}


def write_render_plan_from_task(
    task_id: str,
    *,
    fps: int = 30,
    no_audio_frames: int = 90,
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
        "scenes": [
            {
                "scene_id": str(scene.get("scene_id") or ""),
                "source_slide_ids": scene.get("source_slide_ids") or [],
                "layout": str((scene.get("screen_design") or {}).get("layout") or "full_slide")
                if isinstance(scene.get("screen_design"), dict)
                else "full_slide",
                "title": str(scene.get("title") or ""),
            }
            for scene in manifest.get("scenes") or []
            if isinstance(scene, dict)
        ],
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
        **plan["props_summary"],
    }
