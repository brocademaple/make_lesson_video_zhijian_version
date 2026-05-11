"""素材启发式标签。"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore[misc, assignment]


_LOGO_ICON_RES = re.compile(r"(logo|icon)", re.I)


def _large_shape_hint(path_str: str) -> str:
    """大尺寸 shape → screenshot / decoration。"""
    if Image is None:
        return "decoration"
    try:
        with Image.open(path_str) as im:
            w, h = im.size
        if w >= 900 or h >= 700:
            return "screenshot"
        return "decoration"
    except Exception:
        return "decoration"


def tag_assets(raw_manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """对 full page 与 shapes 生成 asset 列表。"""
    task_root = (raw_manifest.get("task_root") or "").strip()
    slides = raw_manifest.get("slides") or []
    out: list[dict[str, Any]] = []
    aid = 0

    for slide in slides:
        slide_id = str(slide.get("slide_id") or "")
        full_png = slide.get("full_page_png")
        if full_png:
            rel = str(full_png).replace("\\", "/")
            lp = rel.lower()
            at = "full_slide"
            tags: list[str] = ["slide", "full_page"]
            if "logo" in lp:
                at = "logo"
                tags.append("brand")
            elif "icon" in lp:
                at = "icon"
            out.append(
                {
                    "asset_id": f"asset-{aid:04d}",
                    "source": "full_page_png",
                    "source_slide_id": slide_id,
                    "path": rel,
                    "asset_type": at,
                    "semantic_tags": tags,
                    "transparent": False,
                    "quality_status": "usable",
                    "usage_suggestion": "整页底板或镜头切换",
                    "review_status": "pending",
                }
            )
            aid += 1

        for sh in slide.get("shapes") or []:
            if isinstance(sh, dict):
                p = str(sh.get("image_path") or "").replace("\\", "/")
            else:
                p = ""
            if not p:
                continue
            lp = p.lower()
            if "logo" in lp or _LOGO_ICON_RES.search(p):
                at = "logo" if "logo" in lp else "icon"
            elif any(x in lp for x in ("screenshot", "screen", "capture")):
                at = "screenshot"
            else:
                abs_path = Path(task_root) / p if task_root else Path(p)
                at = _large_shape_hint(str(abs_path)) if abs_path.is_file() else "unknown"

            out.append(
                {
                    "asset_id": f"asset-{aid:04d}",
                    "source": "shape",
                    "source_slide_id": slide_id,
                    "path": p,
                    "asset_type": at,
                    "semantic_tags": ["shape", at],
                    "transparent": str(p).lower().endswith(".png"),
                    "quality_status": "unknown",
                    "usage_suggestion": "",
                    "review_status": "pending",
                }
            )
            aid += 1

    return out
