"""基于任务目录生成 raw_material_manifest.json。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from ppt_course_deal.shape_image_export import list_slide_shape_files
from ppt_course_deal.task_storage import get_data_root, load_task, tasks_dir


def _task_root_for_manifest(task_id: str) -> Path:
    return tasks_dir() / task_id


def build_raw_material_manifest(task_id: str) -> dict[str, Any]:
    """
    基于已有 task 目录生成 raw_material_manifest.json。
    写入 ppt_course_data/tasks/<task_id>/raw_material_manifest.json 并返回 dict。
    """
    meta = load_task(task_id)
    if meta is None:
        raise FileNotFoundError(f"任务不存在或无效 task_id: {task_id}")

    base = _task_root_for_manifest(task_id)
    previews = base / "previews"

    slides_meta: list[dict[str, Any]] = list(meta.get("slides") or [])
    slides_out: list[dict[str, Any]] = []

    for i, sm in enumerate(slides_meta):
        sid = f"slide-{i:04d}"
        raw_lines: list[str] = []
        if isinstance(sm.get("text_blocks"), list):
            raw_lines.extend(str(x) for x in sm["text_blocks"] if x)
        elif sm.get("text"):
            raw_lines.append(str(sm["text"]))
        raw_text = "\n\n".join(raw_lines) if raw_lines else str(sm.get("text") or "")

        speaker_notes = sm.get("notes")
        if speaker_notes is not None:
            speaker_notes = str(speaker_notes)

        full_png_rel: Optional[str] = None
        nested = previews / sid / "full.png"
        flat = previews / f"{sid}.png"
        if nested.is_file():
            full_png_rel = f"previews/{sid}/full.png"
        elif flat.is_file():
            full_png_rel = f"previews/{sid}.png"

        shapes_out: list[dict[str, Any]] = []
        try:
            shape_files = list_slide_shape_files(previews, i)
            for j, p in enumerate(shape_files):
                rel = str(p.relative_to(base)).replace("\\", "/")
                shapes_out.append(
                    {
                        "shape_id": f"{sid}-shape-{j:04d}",
                        "image_path": rel,
                        "bbox": None,
                        "ocr_text": None,
                        "source_type": "picture_shape",
                    }
                )
        except Exception:
            pass

        slides_out.append(
            {
                "slide_id": sid,
                "slide_index": i,
                "full_page_png": full_png_rel,
                "raw_text": raw_text,
                "speaker_notes": speaker_notes,
                "shapes": shapes_out,
            }
        )

    task_root_str = str(base.resolve())
    manifest = {
        "task_id": task_id,
        "source_pptx": "source.pptx",
        "task_root": task_root_str,
        "video_profile": meta.get("video_profile") if isinstance(meta.get("video_profile"), dict) else {},
        "slides": slides_out,
        "data_root": str(get_data_root().resolve()),
    }

    out_path = base / "raw_material_manifest.json"
    out_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest
