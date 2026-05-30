from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppt_course_deal import remotion_input_props as rip


def test_build_props_adds_caption_from_task_meta(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    task_id = "task-1"
    data_root = tmp_path / "ppt_course_data"
    task_root = data_root / "tasks" / task_id
    slide_root = task_root / "previews" / "slide-0000"
    slide_root.mkdir(parents=True)
    (slide_root / "full.png").write_bytes(b"png")
    (task_root / "meta.json").write_text(
        json.dumps(
            {
                "slides": [
                    {
                        "title": "课程开场",
                        "text": "课程开场\n这是第一段正文",
                        "text_blocks": ["课程开场", "这是第一段正文"],
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(rip, "get_data_root", lambda: data_root)
    monkeypatch.setattr(rip, "slide_count_for_task", lambda _: 1)
    monkeypatch.setattr(rip, "load_meta", lambda _kind, _key: {})
    monkeypatch.setattr(
        rip, "resolve_workspace_audio_path", lambda *_args, **_kwargs: None
    )

    props = rip.build_props(
        task_id,
        fps=30,
        max_slides=None,
        no_audio_frames=90,
        remotion_workspace_root=tmp_path,
    )

    slide = props["slides"][0]
    assert slide["caption"] == {
        "title": "课程开场",
        "subtitle": "这是第一段正文",
    }


def test_create_render_task_writes_props_and_reports_status(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    task_id = "task-1"
    data_root = tmp_path / "ppt_course_data"
    task_root = data_root / "tasks" / task_id
    for idx in range(2):
        slide_root = task_root / "previews" / f"slide-{idx:04d}"
        slide_root.mkdir(parents=True)
        (slide_root / "full.png").write_bytes(b"png")
    (task_root / "meta.json").write_text(
        json.dumps(
            {
                "slides": [
                    {"title": "第一页", "text_blocks": ["第一页", "正文 A"]},
                    {"title": "第二页", "text_blocks": ["第二页", "正文 B"]},
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(rip, "get_data_root", lambda: data_root)
    monkeypatch.setattr(rip, "slide_count_for_task", lambda _: 2)
    monkeypatch.setattr(rip, "load_meta", lambda _kind, _key: {})
    monkeypatch.setattr(
        rip, "resolve_workspace_audio_path", lambda *_args, **_kwargs: None
    )

    renderer_root = tmp_path / "ppt_course_renderer"
    result = rip.create_render_task(
        task_id,
        fps=30,
        no_audio_frames=90,
        remotion_workspace_root=tmp_path,
        root=renderer_root,
    )

    input_props = Path(result["input_props_path"])
    assert input_props.is_file()
    assert result["task_name"] == "task-1"
    assert result["slide_count"] == 2
    assert result["total_frames"] == 180
    assert result["missing_audio_slide_indexes"] == [0, 1]
    assert "render_tasks/task-1/input-props.json" in result["render_command"]

    status = rip.render_task_status(task_id, root=renderer_root)
    assert status["input_props_exists"] is True
    assert status["output_video_exists"] is False
    assert status["slide_count"] == 2
