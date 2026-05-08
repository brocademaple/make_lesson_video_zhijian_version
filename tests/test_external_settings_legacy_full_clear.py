"""磁盘上曾保存的完整 V2 默认追加规则应被清空。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppt_course_deal.external_settings import (
    LEGACY_TRANSCRIPT_REWRITE_FULL_DISK_DEFAULT_V2,
    load_raw,
)


def test_clear_exact_legacy_full_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PPT_COURSE_DATA", str(tmp_path))
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    (cfg_dir / "external_apis.json").write_text(
        json.dumps(
            {
                "transcript_rewrite": {
                    "extra_instructions": LEGACY_TRANSCRIPT_REWRITE_FULL_DISK_DEFAULT_V2,
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    data = load_raw()
    assert data["transcript_rewrite"]["extra_instructions"] == ""
