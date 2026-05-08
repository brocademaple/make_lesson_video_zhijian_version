"""探测已写入磁盘的音频时长（秒），供成片帧数规划与 Remotion 衔接。"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def probe_audio_duration_seconds(path: Path) -> float | None:
    """返回音频时长（秒）；格式不支持或探测失败时返回 None。"""
    try:
        from tinytag import TinyTag
    except ImportError:
        logger.warning("tinytag 未安装，无法探测音频时长")
        return None
    try:
        p = Path(path)
        if not p.is_file():
            return None
        info = TinyTag.get(str(p))
        if info is None or info.duration is None:
            return None
        d = float(info.duration)
        if d <= 0 or d > 86400:
            return None
        return d
    except Exception:
        logger.debug("探测音频时长失败 %s", path, exc_info=True)
        return None
