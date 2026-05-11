"""raw_material_manifest：基于任务目录写出 JSON。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppt_course_deal import task_storage as ts
from ppt_course_deal.raw_material_manifest import build_raw_material_manifest


def test_build_raw_material_manifest_writes_nonempty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tid = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    data_root = tmp_path / "ppt_course_data"
    tasks_root = data_root / "tasks"
    tasks_root.mkdir(parents=True)
    base = tasks_root / tid
    base.mkdir(parents=True)
    (base / "source.pptx").write_bytes(b"PK\x03\x04fake")

    monkeypatch.setattr(ts, "get_data_root", lambda: data_root)
    monkeypatch.setattr(ts, "tasks_dir", lambda: tasks_root)

    meta = {
        "id": tid,
        "filename": "demo.pptx",
        "slide_count": 1,
        "slides": [
            {
                "index": 0,
                "title": "页标题",
                "text": "正文内容",
                "text_blocks": ["正文内容"],
                "notes": "备注一行",
            }
        ],
    }
    (base / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    out = build_raw_material_manifest(tid)
    assert out["task_id"] == tid
    assert len(out["slides"]) == 1
    assert out["slides"][0]["raw_text"]
    path = base / "raw_material_manifest.json"
    assert path.is_file()
    disk = json.loads(path.read_text(encoding="utf-8"))
    assert disk["slides"][0]["slide_id"] == "slide-0000"
