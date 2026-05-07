"""逐字稿与生成音频的磁盘存储（按会话 task_id 或临时 session_id）。"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any
from uuid import UUID

from ppt_course_deal.task_storage import get_data_root, load_task

logger = logging.getLogger(__name__)


def _validate_id(kind: str, id_str: str | None) -> bool:
    if not id_str or not str(id_str).strip():
        return False
    s = str(id_str).strip()
    if kind == "task":
        try:
            UUID(s)
            return True
        except ValueError:
            return False
    if kind == "session":
        try:
            UUID(s)
            return True
        except ValueError:
            return False
    return False


def workspace_root(kind: str, key: str) -> Path:
    root = get_data_root() / "audio_workspace" / kind / key
    root.mkdir(parents=True, exist_ok=True)
    return root


def meta_path(kind: str, key: str) -> Path:
    return workspace_root(kind, key) / "meta.json"


def slide_audio_path(kind: str, key: str, slide_index: int, ext: str) -> Path:
    safe_ext = re.sub(r"[^a-z0-9]", "", ext.lower()) or "mp3"
    return workspace_root(kind, key) / f"slide-{slide_index:04d}.{safe_ext}"


def load_meta(kind: str, key: str) -> dict[str, Any]:
    p = meta_path(kind, key)
    if not p.is_file():
        return {"transcripts": [], "audio_format": "mp3"}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        logger.warning("音频工作台 meta 损坏 %s", p)
        return {"transcripts": [], "audio_format": "mp3"}


def save_meta(kind: str, key: str, transcripts: list[str], slide_count: int) -> None:
    if slide_count < 0:
        slide_count = 0
    t = list(transcripts)[:slide_count]
    while len(t) < slide_count:
        t.append("")
    meta = load_meta(kind, key)
    meta["transcripts"] = t
    p = meta_path(kind, key)
    p.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def slide_count_for_task(task_id: str) -> int | None:
    data = load_task(task_id)
    if not data:
        return None
    return int(data.get("slide_count") or len(data.get("slides") or []))


def record_generated(kind: str, key: str, slide_index: int, filename: str) -> None:
    meta = load_meta(kind, key)
    gen = meta.get("generated_files") or {}
    gen[str(slide_index)] = filename
    meta["generated_files"] = gen
    meta_path(kind, key).write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
