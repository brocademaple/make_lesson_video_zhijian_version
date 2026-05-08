"""external_apis.json 中旧版口播追加规则迁移。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppt_course_deal.external_settings import (
    DEFAULT_TRANSCRIPT_REWRITE_EXTRA_INSTRUCTIONS,
    LEGACY_TRANSCRIPT_REWRITE_EXTRA_INSTRUCTIONS_V1,
    LEGACY_TRANSCRIPT_REWRITE_FULL_DISK_DEFAULT_V2,
    load_raw,
)


def test_migrate_legacy_v1_exact_match(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PPT_COURSE_DATA", str(tmp_path))
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    path = cfg_dir / "external_apis.json"
    path.write_text(
        json.dumps(
            {
                "minimax": {},
                "agent": {},
                "transcript_rewrite": {
                    "provider": "openai_compatible",
                    "extra_instructions": LEGACY_TRANSCRIPT_REWRITE_EXTRA_INSTRUCTIONS_V1,
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    data = load_raw()
    assert data["transcript_rewrite"]["extra_instructions"] == (
        DEFAULT_TRANSCRIPT_REWRITE_EXTRA_INSTRUCTIONS
    )
    reloaded = json.loads(path.read_text(encoding="utf-8"))
    assert reloaded["transcript_rewrite"]["extra_instructions"] == ""


def test_migrate_user_saved_short_template(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """与仓库里曾保存的「如 (sighs)、(breath) 等」模板一致时升级。"""
    monkeypatch.setenv("PPT_COURSE_DATA", str(tmp_path))
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    short = (
        "【场景与语气】\n面向在线课程录播：普通话、条理清晰、像在教室里对学生讲解。"
        "可适当使用简短口语衔接（例如「那么」「接下来」「我们看一下」），但不要堆砌口头禅；"
        "不要用括号自创中文语气符号。\n\n【与 MiniMax T2A 对齐】\n改写后的文稿将直接送入 MiniMax 语音合成。"
        "除服务端已声明的白名单英文插入语（如 (sighs)、(breath) 等）与停顿标记 <#秒数#> 外，"
        "不要再发明其它括号标记或魔法字符串。\n"
    )
    (cfg_dir / "external_apis.json").write_text(
        json.dumps(
            {
                "transcript_rewrite": {"extra_instructions": short},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    data = load_raw()
    assert data["transcript_rewrite"]["extra_instructions"] == ""


def test_no_migrate_when_already_new_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PPT_COURSE_DATA", str(tmp_path))
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    custom = (
        LEGACY_TRANSCRIPT_REWRITE_FULL_DISK_DEFAULT_V2
        + "\n\n【课程专用】仅本课：少说笑话。"
    )
    (cfg_dir / "external_apis.json").write_text(
        json.dumps({"transcript_rewrite": {"extra_instructions": custom}}, ensure_ascii=False),
        encoding="utf-8",
    )
    data = load_raw()
    assert "【课程专用】" in data["transcript_rewrite"]["extra_instructions"]
