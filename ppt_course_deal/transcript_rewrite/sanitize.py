"""根据 MiniMax T2A 文档白名单清理改写稿中的插入语与停顿标记。"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

_DEAL_ROOT = Path(__file__).resolve().parent.parent


@lru_cache
def _load_allowlist() -> dict[str, Any]:
    path = _DEAL_ROOT / "minimax_t2a_allowlist.json"
    raw = path.read_text(encoding="utf-8")
    return json.loads(raw)


def allowed_interjection_tags() -> frozenset[str]:
    data = _load_allowlist()
    tags = data.get("interjection_tags") or []
    return frozenset(str(x) for x in tags)


def pause_bounds() -> tuple[float, float]:
    data = _load_allowlist()
    pm = data.get("pause_marker") or {}
    lo = float(pm.get("min_sec", 0.01))
    hi = float(pm.get("max_sec", 99.99))
    return (lo, hi)


_INTERJECTION_RE = re.compile(r"\(([^)]+)\)")
_PAUSE_RE = re.compile(r"<#([\d.]+)#>")


def sanitize_for_minimax_t2a(text: str) -> tuple[str, list[str]]:
    """
    移除不在白名单内的 (tag) 插入语；移除不符合范围的 <#x#> 停顿。
    返回 (清理后文本, 警告文案列表)。
    """
    warnings: list[str] = []
    allowed = allowed_interjection_tags()
    lo, hi = pause_bounds()

    def sub_paren(m: re.Match[str]) -> str:
        inner = (m.group(1) or "").strip()
        if inner in allowed:
            return m.group(0)
        warnings.append(f"已移除非文档允许的插入语标记：({inner})")
        return ""

    out = _INTERJECTION_RE.sub(sub_paren, text or "")

    def sub_pause(m: re.Match[str]) -> str:
        raw_s = m.group(1) or ""
        try:
            v = float(raw_s)
        except ValueError:
            warnings.append(f"已移除非法停顿标记：{m.group(0)}")
            return ""
        if lo <= v <= hi:
            return m.group(0)
        warnings.append(f"已移除超范围的停顿标记：{m.group(0)}（允许 {lo}–{hi} 秒）")
        return ""

    out = _PAUSE_RE.sub(sub_pause, out)
    return out, warnings
