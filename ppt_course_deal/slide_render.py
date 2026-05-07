"""将 PPTX 逐页渲染为 PNG（依赖本机 LibreOffice + poppler pdftoppm）。"""

from __future__ import annotations

import logging
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def find_soffice() -> Optional[str]:
    for name in ("soffice", "libreoffice"):
        p = shutil.which(name)
        if p:
            return p
    if sys.platform == "darwin":
        mac = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")
        if mac.is_file():
            return str(mac)
    if sys.platform == "win32":
        win = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")
        if win.is_file():
            return str(win)
    return None


def find_pdftoppm() -> Optional[str]:
    w = shutil.which("pdftoppm")
    if w:
        return w
    # IDE / launchd 启动的服务常不带 Homebrew 的 PATH，直接探测常见安装位置
    if sys.platform == "darwin":
        for p in (
            Path("/opt/homebrew/bin/pdftoppm"),
            Path("/usr/local/bin/pdftoppm"),
        ):
            if p.is_file():
                return str(p)
    if sys.platform == "win32":
        win_poppler = Path(r"C:\poppler\Library\bin\pdftoppm.exe")
        if win_poppler.is_file():
            return str(win_poppler)
    return None


def describe_preview_render_env() -> dict:
    """供 /api/health 与前端提示：整页 PNG 预览所需的系统依赖是否就绪。"""
    soffice = find_soffice()
    ppm = find_pdftoppm()
    ready = bool(soffice and ppm)
    parts: list[str] = []
    if not soffice:
        parts.append(
            "LibreOffice（macOS：`brew install --cask libreoffice`；"
            "安装后需能访问 /Applications/LibreOffice.app 内 soffice）"
        )
    if not ppm:
        parts.append("Poppler（macOS：`brew install poppler`，提供 pdftoppm）")
    hint = ""
    if parts:
        hint = "整页像素预览仍缺：" + "；".join(parts) + "。安装后请重启 Web 服务。"
    return {
        "ready": ready,
        "libreoffice": bool(soffice),
        "pdftoppm": bool(ppm),
        "libreoffice_path": soffice,
        "pdftoppm_path": ppm,
        "install_hint_zh": hint or None,
    }


def _natural_png_sort(paths: list[Path]) -> list[Path]:
    def key(p: Path) -> tuple[int, str]:
        m = re.search(r"(\d+)", p.stem)
        return (int(m.group(1)) if m else 0, p.name)

    return sorted(paths, key=key)


def render_pptx_to_pngs(pptx_path: Path, work_dir: Path) -> tuple[list[Path], Optional[str]]:
    """
    PPTX → PDF（LibreOffice）→ 每页 PNG（pdftoppm）。
    返回 (按页排序的 png 路径列表, 错误说明)；成功时错误为 None。
    """
    pptx_path = pptx_path.resolve()
    work_dir = work_dir.resolve()
    work_dir.mkdir(parents=True, exist_ok=True)

    soffice = find_soffice()
    if not soffice:
        return [], (
            "未检测到 LibreOffice：请安装后重试（macOS 可用 "
            "`brew install --cask libreoffice`，并确保命令行可调用 soffice）。"
        )

    try:
        subprocess.run(
            [
                soffice,
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(work_dir),
                str(pptx_path),
            ],
            check=True,
            capture_output=True,
            timeout=600,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        logger.warning("LibreOffice 转 PDF 失败: %s", e.stderr or e)
        return [], "LibreOffice 将 PPT 转为 PDF 失败，请检查文件是否损坏。"
    except FileNotFoundError:
        return [], "无法执行 LibreOffice，请检查安装路径。"

    pdfs = sorted(work_dir.glob("*.pdf"))
    if not pdfs:
        return [], "未生成 PDF 中间文件。"

    pdf_path = pdfs[0]
    png_dir = work_dir / "png_pages"
    png_dir.mkdir(exist_ok=True)
    prefix = png_dir / "slide"

    ppm = find_pdftoppm()
    if not ppm:
        return [], (
            "未检测到 pdftoppm（Poppler）。请安装 Poppler，例如："
            "macOS `brew install poppler`，Windows 安装 poppler 并加入 PATH。"
        )

    try:
        subprocess.run(
            [ppm, "-png", "-r", "144", str(pdf_path), str(prefix)],
            check=True,
            capture_output=True,
            timeout=600,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        logger.warning("pdftoppm 失败: %s", e.stderr or e)
        return [], "PDF 转 PNG 失败（pdftoppm）。"

    pngs = list(png_dir.glob("*.png"))
    pngs = _natural_png_sort(pngs)
    if not pngs:
        return [], "未生成预览 PNG 文件。"

    return pngs, None
