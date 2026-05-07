"""日志、路径、占位素材生成。"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

try:
    from rich.console import Console
    from rich.logging import RichHandler

    _console = Console(stderr=True)
    _handler = RichHandler(console=_console, rich_tracebacks=True)
except ImportError:
    _handler = logging.StreamHandler(sys.stderr)

LOG_FORMAT = "%(message)s"


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        handlers=[_handler],
        force=True,
    )


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_placeholder_assets(assets_dir: Path) -> None:
    """若图标缺失，用 Pillow 生成简单占位 PNG。"""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        logging.warning("Pillow 未安装，跳过本地图标生成")
        return

    assets_dir.mkdir(parents=True, exist_ok=True)
    specs = {
        "warning.png": ((255, 180, 0), "!"),
        "check.png": ((40, 167, 69), "✓"),
        "cross.png": ((220, 53, 69), "✗"),
        "phone.png": ((26, 86, 158), "☎"),
        "shield.png": ((106, 90, 205), "◆"),
    }
    for name, (color, _) in specs.items():
        fp = assets_dir / name
        if fp.is_file():
            continue
        img = Image.new("RGBA", (128, 128), (255, 255, 255, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([8, 8, 120, 120], radius=16, fill=color + (255,))
        img.save(fp, "PNG")
        logging.debug("已生成占位图标 %s", fp)
