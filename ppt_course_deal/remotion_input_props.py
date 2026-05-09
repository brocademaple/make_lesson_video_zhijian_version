"""根据已存任务预览图 + 音频工作台生成 Remotion `input-props.json`。"""

from __future__ import annotations

import json
import math
import shutil
from pathlib import Path
from typing import Any

from ppt_course_deal.audio_workspace_store import (
    load_meta,
    resolve_workspace_audio_path,
    slide_count_for_task,
)
from ppt_course_deal.task_audio_bundle import task_bundle_audio_dir
from ppt_course_deal.task_storage import get_data_root


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def rel_for_props(abs_path: Path, remotion_workspace_root: Path) -> str:
    """Remotion 的 props 路径：相对 REMOTION_WORKSPACE_ROOT（通常为仓库根）。"""
    resolved = abs_path.resolve()
    root = remotion_workspace_root.resolve()
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError:
        return str(resolved)


def probe_duration_sec(path: Path) -> float:
    from tinytag import TinyTag

    tag = TinyTag.get(str(path))
    d = tag.duration
    if d is None or float(d) <= 0:
        raise ValueError(f"无法读取音频时长：{path}")
    return float(d)


def build_props(
    task_id: str,
    *,
    fps: int,
    max_slides: int | None,
    no_audio_frames: int,
    remotion_workspace_root: Path | None,
    bundle_audio: bool = False,
) -> dict[str, Any]:
    """
    构造 CourseDeckComposition 可用的 props。
    每页 durationInFrames：有分段 mp3 时为各段 ceil(秒×fps) 之和；否则为 no_audio_frames。
    """
    data_root = get_data_root()
    task_root = data_root / "tasks" / task_id
    preview_root = task_root / "previews"
    if not preview_root.is_dir():
        raise ValueError(f"未找到预览目录：{preview_root}")

    sc = slide_count_for_task(task_id)
    if sc is None or sc < 1:
        raise ValueError(f"无法解析任务页数：{task_id}")
    n = min(sc, max_slides) if max_slides is not None else sc

    root = remotion_workspace_root or repo_root()
    meta = load_meta("task", task_id)
    raw_dur = meta.get("segment_duration_sec") or {}
    if not isinstance(raw_dur, dict):
        raw_dur = {}

    slides: list[dict[str, Any]] = []
    for i in range(n):
        full = preview_root / f"slide-{i:04d}" / "full.png"
        if not full.is_file():
            raise ValueError(f"缺少整页预览：{full}")

        shapes_dir = preview_root / f"slide-{i:04d}" / "shapes"
        shape_rels: list[str] = []
        if shapes_dir.is_dir():
            for p in sorted(shapes_dir.glob("shape-*.png")):
                shape_rels.append(rel_for_props(p, root))

        audio_rels: list[str] = []
        segment_frames: list[int] = []
        j = 0
        while True:
            ap = resolve_workspace_audio_path("task", task_id, i, j, "mp3")
            if ap is None or not ap.is_file():
                break
            sk = f"{i}-{j}"
            sec = raw_dur.get(sk)
            if isinstance(sec, bool):
                sec = None
            if isinstance(sec, (int, float)) and float(sec) > 0:
                dur_sec = float(sec)
            else:
                dur_sec = probe_duration_sec(ap)
            frames = max(1, math.ceil(dur_sec * fps))
            if bundle_audio:
                dest_dir = task_bundle_audio_dir(task_id, i)
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_mp3 = dest_dir / ap.name
                shutil.copy2(ap, dest_mp3)
                audio_rels.append(rel_for_props(dest_mp3, root))
            else:
                audio_rels.append(rel_for_props(ap, root))
            segment_frames.append(frames)
            j += 1
            if j > 500:
                break

        image_rel = rel_for_props(full, root)
        slide_obj: dict[str, Any] = {
            "imageRelative": image_rel,
            "durationInFrames": no_audio_frames,
        }
        if shape_rels:
            slide_obj["shapeRelatives"] = shape_rels

        if audio_rels:
            slide_total = sum(segment_frames)
            slide_obj["durationInFrames"] = slide_total
            slide_obj["audioRelatives"] = audio_rels
            slide_obj["audioSegmentDurationInFrames"] = segment_frames
        else:
            slide_obj["durationInFrames"] = no_audio_frames

        slides.append(slide_obj)

    return {"fps": fps, "slides": slides}


def write_props_file(
    task_id: str,
    output: Path,
    *,
    fps: int = 30,
    max_slides: int | None = None,
    no_audio_frames: int = 90,
    remotion_workspace_root: Path | None = None,
    bundle_audio: bool = False,
) -> None:
    props = build_props(
        task_id,
        fps=fps,
        max_slides=max_slides,
        no_audio_frames=no_audio_frames,
        remotion_workspace_root=remotion_workspace_root,
        bundle_audio=bundle_audio,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(props, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
