"""句级字幕分段（无音频对齐）。"""

from __future__ import annotations

import re
from typing import Any


_SPLIT_RE = re.compile(r"(?<=[。；;!?？])")


def split_subtitle_segments(text: str, estimated_duration_sec: float) -> list[dict[str, Any]]:
    """
    按中文句号、分号、问号、感叹号切分；按时长均匀分配 start_sec / end_sec。
    """
    t = (text or "").strip()
    if not t:
        return []

    parts: list[str] = []
    for chunk in _SPLIT_RE.split(t):
        s = chunk.strip()
        if s:
            parts.append(s)
    if not parts:
        parts = [t]

    n = len(parts)
    dur = max(float(estimated_duration_sec), 0.1)
    seg_len = dur / n
    out: list[dict[str, Any]] = []
    for i, seg_text in enumerate(parts):
        start = round(i * seg_len, 3)
        end = round((i + 1) * seg_len, 3) if i < n - 1 else round(dur, 3)
        out.append({"start_sec": start, "end_sec": end, "text": seg_text})
    return out
