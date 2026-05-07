"""从 CourseSlide 列表生成 PPTX。"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from pptx import Presentation

from models import CourseSlide
from template_engine import render_course_slide, render_error_slide

logger = logging.getLogger(__name__)


def write_page_scripts(slides: List[CourseSlide], path: Path) -> None:
    lines: List[str] = ["# 逐页讲稿", ""]
    for s in slides:
        lines.append(f"## {s.slide_id}｜{s.title}")
        lines.append(f"预计时长：{s.duration_seconds} 秒")
        lines.append("")
        lines.append("口播：")
        lines.append(s.narration or "（待补充口播）")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("已写入讲稿 %s", path)


def build_presentation(
    slides: List[CourseSlide],
    out_pptx: Path,
    assets_dir: Path,
) -> List[str]:
    """生成 PPTX；返回错误信息列表（每页失败记录一条，并插入 fallback 页）。"""
    out_pptx.parent.mkdir(parents=True, exist_ok=True)
    errors: List[str] = []
    prs = Presentation()

    for cs in slides:
        try:
            render_course_slide(prs, cs, assets_dir)
        except Exception as e:
            msg = f"{cs.slide_id}: {e}"
            logger.exception("渲染失败 %s", cs.slide_id)
            errors.append(msg)
            try:
                render_error_slide(prs, cs.slide_id, str(e))
            except Exception as e2:
                errors.append(f"fallback 失败 {cs.slide_id}: {e2}")

    prs.save(str(out_pptx))
    logger.info("已保存 %s", out_pptx)
    return errors
