"""无 LibreOffice 时，根据已解析的幻灯片文本生成 16:9 占位 PNG（保证前端可见缩略图与大图）。"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# 16:9
_W, _H = 1200, 675


def _load_font(size: int):
    from PIL import ImageFont

    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/Library/Fonts/Microsoft/SimHei.ttf",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "C:\\Windows\\Fonts\\msyh.ttc",
        "C:\\Windows\\Fonts\\simhei.ttf",
    ]
    for p in candidates:
        if Path(p).is_file():
            try:
                return ImageFont.truetype(p, size, index=0)
            except OSError:
                continue
    logger.warning("未找到中文字体，占位图中文可能显示为方框")
    return ImageFont.load_default()


def _wrap_lines(text: str, max_chars: int, max_lines: int) -> list[str]:
    lines: list[str] = []
    for para in text.replace("\r\n", "\n").split("\n"):
        para = para.strip()
        if not para:
            if lines and lines[-1] != "":
                lines.append("")
            continue
        while para:
            chunk = para[:max_chars]
            lines.append(chunk)
            para = para[max_chars:]
            if len(lines) >= max_lines:
                lines[-1] = lines[-1].rstrip() + "…"
                return lines
    return lines[:max_lines]


def render_slide_placeholder_png(slide: dict[str, Any]) -> bytes:
    """单页 dict 与 extract.slide_snapshot 输出字段一致。"""
    from PIL import Image, ImageDraw

    title = (slide.get("title") or "（无标题）").strip()[:120]
    blocks = slide.get("text_blocks") or []
    body = slide.get("text") or ""
    if blocks:
        body = "\n".join(blocks)
    body = (body or "（本页无正文）").strip()[:3500]

    img = Image.new("RGB", (_W, _H), (245, 247, 252))
    draw = ImageDraw.Draw(img)
    font_title = _load_font(36)
    font_body = _load_font(22)
    font_foot = _load_font(16)

    margin = 48
    y = margin
    draw.text((margin, y), title, fill=(30, 58, 138), font=font_title)
    y += 52

    body_lines = _wrap_lines(body, max_chars=44, max_lines=18)
    line_h = 30
    for line in body_lines:
        if y > _H - 80:
            draw.text((margin, y), "…", fill=(55, 65, 81), font=font_body)
            break
        draw.text((margin, y), line, fill=(31, 41, 55), font=font_body)
        y += line_h

    foot = "占位预览 · 文本排版示意（安装 LibreOffice + Poppler 后可显示真实幻灯片像素图）"
    draw.text((margin, _H - 36), foot[:80], fill=(148, 163, 184), font=font_foot)

    import io

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def write_fallback_pngs(slides: list[dict[str, Any]], out_dir: Path) -> list[Path]:
    """按 slide index 顺序写入 slide-{i}.png，返回路径列表。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for i, slide in enumerate(slides):
        data = render_slide_placeholder_png(slide)
        p = out_dir / f"slide-{i:04d}.png"
        p.write_bytes(data)
        paths.append(p)
    logger.info("已生成 %s 张文本占位预览 PNG", len(paths))
    return paths
