"""外部 API 配置（落盘于数据目录，密钥不落日志）。"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from ppt_course_deal.task_storage import get_data_root

logger = logging.getLogger(__name__)

CONFIG_DIRNAME = "config"
CONFIG_FILENAME = "external_apis.json"

DEFAULT_MINIMAX: dict[str, Any] = {
    "api_base": "https://api.minimax.io",
    "group_id": "",
    "model": "speech-2.8-hd",
    "voice_id": "Chinese (Mandarin)_Lyrical_Voice",
    "language_boost": "Chinese",
    "output_format": "hex",
    "audio_format": "mp3",
    "sample_rate": 32000,
    "bitrate": 128000,
    "speed": 1.0,
    "vol": 1.0,
    "pitch": 0,
    "stream": False,
}

DEFAULT_AGENT: dict[str, Any] = {
    "provider": "none",
    "note": "",
}


def config_path() -> Path:
    d = get_data_root() / CONFIG_DIRNAME
    d.mkdir(parents=True, exist_ok=True)
    return d / CONFIG_FILENAME


def load_raw() -> dict[str, Any]:
    path = config_path()
    if not path.is_file():
        return {
            "minimax": {**DEFAULT_MINIMAX},
            "agent": {**DEFAULT_AGENT},
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        logger.warning("外部配置损坏，已使用默认")
        return {
            "minimax": {**DEFAULT_MINIMAX},
            "agent": {**DEFAULT_AGENT},
        }
    mm = {**DEFAULT_MINIMAX, **(data.get("minimax") or {})}
    ag = {**DEFAULT_AGENT, **(data.get("agent") or {})}
    return {"minimax": mm, "agent": ag}


def save_raw(data: dict[str, Any]) -> None:
    path = config_path()
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def mask_key(key: str | None) -> dict[str, Any]:
    if not key or not str(key).strip():
        return {"configured": False, "suffix": None}
    s = str(key).strip()
    suf = s[-4:] if len(s) >= 4 else "****"
    return {"configured": True, "suffix": suf}


def public_minimax(mm: dict[str, Any]) -> dict[str, Any]:
    """供 GET 返回（不含完整 api_key）。"""
    key = mm.get("api_key") or ""
    out = {k: v for k, v in mm.items() if k != "api_key"}
    out.update(mask_key(str(key) if key else None))
    return out


def merge_minimax_update(existing: dict[str, Any], body: dict[str, Any]) -> dict[str, Any]:
    merged = {**existing}
    for k, v in body.items():
        if k == "api_key":
            if isinstance(v, str) and v.strip():
                merged["api_key"] = v.strip()
            continue
        if v is not None:
            merged[k] = v
    return merged


def merge_agent_update(existing: dict[str, Any], body: dict[str, Any]) -> dict[str, Any]:
    merged = {**existing}
    for k, v in body.items():
        if v is not None:
            merged[k] = v
    return merged


def get_minimax_for_server_call() -> dict[str, Any]:
    """含明文 api_key，仅服务端合成调用。"""
    raw = load_raw()
    return raw.get("minimax") or {**DEFAULT_MINIMAX}
