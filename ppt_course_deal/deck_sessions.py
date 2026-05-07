"""浏览器上传演示文稿后的预览会话（磁盘 PNG + session id）。"""

from __future__ import annotations

import shutil
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from uuid import uuid4

MAX_SESSIONS = 30

_lock = Lock()
_sessions: OrderedDict[str, DeckSession] = OrderedDict()


@dataclass(frozen=True)
class DeckSession:
    session_id: str
    root_dir: Path
    png_paths: tuple[Path, ...]


def create_session(root_dir: Path, png_paths: list[Path]) -> str:
    sid = str(uuid4())
    sess = DeckSession(sid, root_dir.resolve(), tuple(png_paths))
    with _lock:
        _sessions[sid] = sess
        _sessions.move_to_end(sid)
        while len(_sessions) > MAX_SESSIONS:
            _, old = _sessions.popitem(last=False)
            shutil.rmtree(old.root_dir, ignore_errors=True)
    return sid


def get_session(session_id: str) -> DeckSession | None:
    with _lock:
        s = _sessions.get(session_id)
        if s is not None:
            _sessions.move_to_end(session_id)
        return s
