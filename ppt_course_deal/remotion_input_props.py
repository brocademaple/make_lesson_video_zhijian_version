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


DEFAULT_RENDER_TASK_NAME_PREFIX = "task-"


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


def _load_task_meta(task_root: Path) -> dict[str, Any]:
    meta_path = task_root / "meta.json"
    if not meta_path.is_file():
        return {}
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _clean_one_line(value: Any, *, limit: int) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def _caption_for_slide(task_meta: dict[str, Any], slide_index: int) -> dict[str, str] | None:
    slides = task_meta.get("slides")
    if not isinstance(slides, list) or slide_index >= len(slides):
        return None
    slide = slides[slide_index]
    if not isinstance(slide, dict):
        return None

    title = _clean_one_line(slide.get("title") or f"第 {slide_index + 1} 页", limit=60)
    text_blocks = slide.get("text_blocks")
    subtitle_source = ""
    if isinstance(text_blocks, list):
        for block in text_blocks:
            candidate = _clean_one_line(block, limit=120)
            if candidate and candidate != title:
                subtitle_source = candidate
                break
    if not subtitle_source:
        subtitle_source = _clean_one_line(slide.get("text"), limit=120)
        if subtitle_source == title:
            subtitle_source = ""

    if not title and not subtitle_source:
        return None
    caption: dict[str, str] = {"title": title or f"第 {slide_index + 1} 页"}
    if subtitle_source:
        caption["subtitle"] = subtitle_source
    return caption


def safe_render_task_name(task_id: str) -> str:
    text = "".join(ch if ch.isalnum() or ch in "-_." else "-" for ch in task_id.strip())
    text = text.strip(".-_")
    if not text:
        text = "unknown-task"
    if not text.startswith(DEFAULT_RENDER_TASK_NAME_PREFIX):
        text = f"{DEFAULT_RENDER_TASK_NAME_PREFIX}{text}"
    return text


def renderer_root() -> Path:
    return repo_root() / "ppt_course_renderer"


def render_task_dir(task_id: str, *, root: Path | None = None) -> Path:
    base = root or renderer_root()
    return base / "render_tasks" / safe_render_task_name(task_id)


def render_task_paths(task_id: str, *, root: Path | None = None) -> dict[str, Path]:
    task_dir = render_task_dir(task_id, root=root)
    return {
        "task_dir": task_dir,
        "input_props": task_dir / "input-props.json",
        "output_video": task_dir / "out" / "video.mp4",
    }


def summarize_props(props: dict[str, Any]) -> dict[str, Any]:
    slides = props.get("slides") or []
    if not isinstance(slides, list):
        slides = []
    total_frames = 0
    audio_slide_count = 0
    missing_audio_slide_indexes: list[int] = []
    for idx, slide in enumerate(slides):
        if not isinstance(slide, dict):
            missing_audio_slide_indexes.append(idx)
            continue
        frames = slide.get("durationInFrames")
        if isinstance(frames, bool):
            frames = 0
        if isinstance(frames, (int, float)):
            total_frames += int(frames)
        audio_rels = slide.get("audioRelatives") or slide.get("audioRelative")
        if audio_rels:
            audio_slide_count += 1
        else:
            missing_audio_slide_indexes.append(idx)
    fps = props.get("fps")
    if isinstance(fps, bool) or not isinstance(fps, (int, float)) or fps <= 0:
        fps = 30
    return {
        "slide_count": len(slides),
        "total_frames": total_frames,
        "duration_sec": round(total_frames / float(fps), 3) if total_frames else 0,
        "audio_slide_count": audio_slide_count,
        "missing_audio_slide_indexes": missing_audio_slide_indexes,
    }


def render_command_for_task(task_id: str, *, root: Path | None = None) -> str:
    base = root or renderer_root()
    task_name = safe_render_task_name(task_id)
    input_rel = Path("render_tasks") / task_name / "input-props.json"
    output_rel = Path("render_tasks") / task_name / "out" / "video.mp4"
    return (
        f"cd {base} && "
        f"npx remotion render src/index.ts MyVideoTest1 {output_rel.as_posix()} "
        f"--props {input_rel.as_posix()}"
    )


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
    task_meta = _load_task_meta(task_root)
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
        caption = _caption_for_slide(task_meta, i)
        if caption:
            slide_obj["caption"] = caption
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
) -> dict[str, Any]:
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
    return props


def create_render_task(
    task_id: str,
    *,
    fps: int = 30,
    max_slides: int | None = None,
    no_audio_frames: int = 90,
    remotion_workspace_root: Path | None = None,
    bundle_audio: bool = False,
    root: Path | None = None,
) -> dict[str, Any]:
    paths = render_task_paths(task_id, root=root)
    paths["output_video"].parent.mkdir(parents=True, exist_ok=True)
    props = write_props_file(
        task_id,
        paths["input_props"],
        fps=fps,
        max_slides=max_slides,
        no_audio_frames=no_audio_frames,
        remotion_workspace_root=remotion_workspace_root or repo_root(),
        bundle_audio=bundle_audio,
    )
    summary = summarize_props(props)
    return {
        "task_name": safe_render_task_name(task_id),
        "task_dir": str(paths["task_dir"]),
        "input_props_path": str(paths["input_props"]),
        "output_video_path": str(paths["output_video"]),
        "render_command": render_command_for_task(task_id, root=root),
        **summary,
    }


def render_task_status(task_id: str, *, root: Path | None = None) -> dict[str, Any]:
    paths = render_task_paths(task_id, root=root)
    input_exists = paths["input_props"].is_file()
    output_exists = paths["output_video"].is_file()
    output_size_bytes = paths["output_video"].stat().st_size if output_exists else 0
    summary: dict[str, Any] = {}
    if input_exists:
        try:
            props = json.loads(paths["input_props"].read_text(encoding="utf-8"))
            if isinstance(props, dict):
                summary = summarize_props(props)
        except (OSError, json.JSONDecodeError):
            summary = {"input_props_error": "input-props.json 无法读取或不是合法 JSON"}
    return {
        "task_name": safe_render_task_name(task_id),
        "task_dir": str(paths["task_dir"]),
        "input_props_path": str(paths["input_props"]),
        "input_props_exists": input_exists,
        "output_video_path": str(paths["output_video"]),
        "output_video_exists": output_exists,
        "output_video_size_bytes": output_size_bytes,
        "render_command": render_command_for_task(task_id, root=root),
        **summary,
    }
