"""可选：使用 LibreOffice/soffice 将 PPTX 导出为 PNG。"""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def find_soffice() -> Optional[str]:
    for name in ("soffice", "libreoffice"):
        p = shutil.which(name)
        if p:
            return p
    return None


def export_pptx_to_png(pptx_path: Path, out_dir: Path) -> bool:
    """
    将每一页导出为 PNG。需要本机安装 LibreOffice。
    成功返回 True；不可用或失败返回 False（不抛异常阻塞主流程）。
    """
    soffice = find_soffice()
    if not soffice:
        logger.warning("未找到 LibreOffice CLI（soffice/libreoffice），跳过图片导出")
        return False

    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            [
                soffice,
                "--headless",
                "--convert-to",
                "png",
                "--outdir",
                str(out_dir),
                str(pptx_path.resolve()),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=600,
        )
        logger.info("已导出 PNG 到 %s", out_dir)
        return True
    except Exception as e:
        logger.warning("LibreOffice 导出失败：%s", e)
        return False
