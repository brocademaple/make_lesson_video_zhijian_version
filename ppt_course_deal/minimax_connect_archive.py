"""MiniMax 连通测试记录：脱敏落盘于数据目录，便于对照每次请求与结果。"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from ppt_course_deal.minimax_client import normalize_minimax_api_key
from ppt_course_deal.task_storage import get_data_root

logger = logging.getLogger(__name__)

CONNECT_TESTS_DIRNAME = "minimax_connect_tests"


def connect_tests_dir() -> Path:
    d = get_data_root() / CONNECT_TESTS_DIRNAME
    d.mkdir(parents=True, exist_ok=True)
    return d


def redact_minimax(mm: dict[str, Any]) -> dict[str, Any]:
    """写入归档用的 MiniMax 配置副本（密钥仅保留尾号）。"""
    out: dict[str, Any] = dict(mm)
    raw_k = out.get("api_key")
    if raw_k is not None and str(raw_k).strip():
        k = normalize_minimax_api_key(str(raw_k))
        out["api_key"] = f"***{k[-4:]}" if len(k) >= 4 else "***"
    else:
        out["api_key"] = ""
    return out


def write_connect_test_record(record: dict[str, Any]) -> str:
    """写入一条 JSON 记录，返回相对于数据根的路径（POSIX）。"""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    name = f"{ts}_{uuid4().hex[:8]}.json"
    path = connect_tests_dir() / name
    try:
        path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        logger.warning("MiniMax 连通测试归档失败", exc_info=True)
        return ""
    try:
        rel = path.relative_to(get_data_root())
        return rel.as_posix()
    except ValueError:
        return name
