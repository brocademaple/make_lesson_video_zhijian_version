"""本机持久化：每次解析成功后的素材与解析结果，供「项目库」列表与弹窗回顾。"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)

MAX_STORED_TASKS = 200


def _validate_task_id(task_id: str) -> bool:
    try:
        UUID(task_id)
        return True
    except ValueError:
        return False


def get_data_root() -> Path:
    """数据根目录：优先环境变量，否则为仓库根下 `ppt_course_data/`（与包内代码并列，便于在资源管理器中查看）。"""
    import os

    env = os.environ.get("PPT_COURSE_DATA")
    if env:
        return Path(env).expanduser().resolve()
    repo_root = Path(__file__).resolve().parent.parent
    return (repo_root / "ppt_course_data").resolve()


def tasks_dir() -> Path:
    d = get_data_root() / "tasks"
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_task_from_parse(
    raw: bytes,
    filename: str,
    slides: list[dict[str, Any]],
    pngs: list[Path] | None,
    preview_source: str,
    images_error: str | None,
    images_available: bool,
    preview_count: int,
    video_profile: dict[str, Any] | None = None,
) -> str | None:
    """
    将本次解析结果写入磁盘；返回 task_id，失败时返回 None（不影响主流程）。
    """
    if not slides:
        return None
    task_id = str(uuid4())
    base = tasks_dir() / task_id
    try:
        base.mkdir(parents=True, exist_ok=False)
        (base / "source.pptx").write_bytes(raw)
        prev_dir = base / "previews"
        png_list: list[Path] = list(pngs) if pngs else []
        if png_list:
            prev_dir.mkdir(exist_ok=True)
            for i, src in enumerate(png_list):
                if not src.is_file():
                    continue
                dest = prev_dir / f"slide-{i:04d}.png"
                shutil.copy2(src, dest)

        shape_manifest: list[dict[str, Any]] = []
        try:
            from ppt_course_deal.shape_image_export import populate_slide_preview_folders

            prev_dir.mkdir(exist_ok=True)
            shape_manifest = populate_slide_preview_folders(
                base / "source.pptx",
                prev_dir,
                len(slides),
                png_list if png_list else None,
            )
        except Exception:
            logger.exception("按页目录导出 full.png / shapes 失败，已跳过")

        created = datetime.now(timezone.utc).isoformat()
        meta: dict[str, Any] = {
            "id": task_id,
            "filename": filename or "uploaded.pptx",
            "created_at": created,
            "slide_count": len(slides),
            "slides": slides,
            "preview_source": preview_source,
            "images_error": images_error,
            "images_available": images_available,
            "preview_count": preview_count,
            "shape_image_manifest": shape_manifest,
            "video_profile": video_profile or {},
        }
        (base / "meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        _trim_old_tasks()
        logger.info("已持久化解析任务 %s (%s)", task_id, meta["filename"])
        return task_id
    except Exception:
        logger.exception("持久化任务失败，已忽略")
        shutil.rmtree(base, ignore_errors=True)
        return None


def _trim_old_tasks() -> None:
    """任务数超过上限时删除最旧目录。"""
    root = tasks_dir()
    dirs: list[tuple[float, Path]] = []
    for p in root.iterdir():
        if not p.is_dir() or not _validate_task_id(p.name):
            continue
        meta = p / "meta.json"
        if not meta.is_file():
            continue
        try:
            mtime = meta.stat().st_mtime
        except OSError:
            continue
        dirs.append((mtime, p))
    dirs.sort(key=lambda x: x[0])
    while len(dirs) > MAX_STORED_TASKS:
        _, oldest = dirs.pop(0)
        shutil.rmtree(oldest, ignore_errors=True)
        logger.info("已删除最旧任务目录 %s（超出存储上限）", oldest.name)


def list_task_summaries() -> list[dict[str, Any]]:
    """轻量列表（不含 slides 全文）。"""
    out: list[dict[str, Any]] = []
    root = tasks_dir()
    for p in root.iterdir():
        if not p.is_dir() or not _validate_task_id(p.name):
            continue
        meta_path = p / "meta.json"
        if not meta_path.is_file():
            continue
        try:
            data = json.loads(meta_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        task_id = str(data.get("id", p.name))
        profile = data.get("video_profile") if isinstance(data.get("video_profile"), dict) else {}
        out.append(
            {
                "id": task_id,
                "filename": data.get("filename", "unknown.pptx"),
                "created_at": data.get("created_at", ""),
                "slide_count": int(data.get("slide_count", 0)),
                "preview_count": int(data.get("preview_count", 0)),
                "images_available": bool(data.get("images_available")),
                "video_profile": profile,
                "source_type": _summary_source_type(data, p),
                "project_kind": _summary_project_kind(data, profile),
                "has_director_manifest": (p / "director_manifest.json").is_file(),
                "has_render_plan": _summary_has_render_plan(task_id),
                "has_output_video": _summary_has_output_video(task_id),
            }
        )
    out.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    return out


def _summary_source_type(data: dict[str, Any], task_root: Path) -> str:
    raw = str(data.get("source_type") or "").strip().lower()
    if raw in {"pptx", "pdf", "demo"}:
        return raw
    filename = str(data.get("filename") or data.get("source_filename") or "").lower()
    if filename.endswith(".pdf") or (task_root / "source.pdf").is_file():
        return "pdf"
    if filename.endswith(".pptx") or (task_root / "source.pptx").is_file():
        if isinstance(data.get("demo"), dict):
            return "demo"
        return "pptx"
    return "unknown"


def _summary_project_kind(data: dict[str, Any], profile: dict[str, Any]) -> str:
    kind = str(profile.get("id") or "").strip().lower()
    aliases = {
        "sales": "product",
        "onboarding": "training",
    }
    if kind:
        return aliases.get(kind, kind)
    name = str(data.get("filename") or "").lower()
    if "质检" in name or "redline" in name or "quality" in name:
        return "quality"
    if "design" in name or "workshop" in name:
        return "creative"
    if "onboarding" in name or "新人" in name:
        return "training"
    return "general"


def _summary_has_render_plan(task_id: str) -> bool:
    try:
        from ppt_course_deal.remotion_input_props import render_task_dir

        return (render_task_dir(task_id) / "render_plan.json").is_file()
    except Exception:
        return False


def _summary_has_output_video(task_id: str) -> bool:
    try:
        from ppt_course_deal.remotion_input_props import render_task_paths

        return render_task_paths(task_id)["output_video"].is_file()
    except Exception:
        return False


def load_task(task_id: str) -> dict[str, Any] | None:
    if not _validate_task_id(task_id):
        return None
    meta_path = tasks_dir() / task_id / "meta.json"
    if not meta_path.is_file():
        return None
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def delete_task(task_id: str) -> bool:
    if not _validate_task_id(task_id):
        return False
    path = tasks_dir() / task_id
    if not path.is_dir():
        return False
    shutil.rmtree(path, ignore_errors=True)
    return True


def update_task_display_name(task_id: str, display_name: str) -> bool:
    """更新 meta.json 中的展示名称（仅改显示文案，不移动磁盘上的 source.pptx）。"""
    if not _validate_task_id(task_id):
        return False
    name = (display_name or "").strip()
    if not name or len(name) > 200:
        return False
    meta_path = tasks_dir() / task_id / "meta.json"
    if not meta_path.is_file():
        return False
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    data["filename"] = name
    try:
        meta_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        return False
    logger.info("已重命名任务展示名 %s → %s", task_id, name[:80])
    return True


def preview_png_path(task_id: str, slide_index: int) -> Path | None:
    if slide_index < 0 or not _validate_task_id(task_id):
        return None
    root = tasks_dir() / task_id / "previews"
    nested = root / f"slide-{slide_index:04d}" / "full.png"
    if nested.is_file():
        return nested
    flat = root / f"slide-{slide_index:04d}.png"
    if flat.is_file():
        return flat
    return None


def slide_shape_file_path(task_id: str, slide_index: int, shape_index: int) -> Path | None:
    """``previews/slide-NNNN/shapes/shape-XXXX.ext`` 按文件名排序后的第 ``shape_index`` 个文件。"""
    if slide_index < 0 or shape_index < 0 or not _validate_task_id(task_id):
        return None
    from ppt_course_deal.shape_image_export import list_slide_shape_files

    root = tasks_dir() / task_id / "previews"
    files = list_slide_shape_files(root, slide_index)
    if shape_index >= len(files):
        return None
    return files[shape_index]
