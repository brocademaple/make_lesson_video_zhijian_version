"""本机持久化：每次解析成功后的 PPT 与解析结果，供「已存任务」列表与弹窗回顾。"""

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
        if pngs:
            prev_dir.mkdir(exist_ok=True)
            for i, src in enumerate(pngs):
                if not src.is_file():
                    continue
                dest = prev_dir / f"slide-{i:04d}.png"
                shutil.copy2(src, dest)

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
        out.append(
            {
                "id": data.get("id", p.name),
                "filename": data.get("filename", "unknown.pptx"),
                "created_at": data.get("created_at", ""),
                "slide_count": int(data.get("slide_count", 0)),
                "preview_count": int(data.get("preview_count", 0)),
                "images_available": bool(data.get("images_available")),
            }
        )
    out.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    return out


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
    p = tasks_dir() / task_id / "previews" / f"slide-{slide_index:04d}.png"
    if p.is_file():
        return p
    return None
