from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ppt_course_deal.cli import app
from ppt_course_deal.data_cleanup import cleanup_project_data
from ppt_course_deal.task_storage import get_data_root
from ppt_course_deal.v2_workspace import renderer_root, workspace_root


runner = CliRunner()


def test_cli_uses_any2video_brand_and_exposes_cleanup() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "any2video" in result.output
    assert "clear-project-data" in result.output


def test_any2video_environment_variables_take_precedence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy_data = tmp_path / "legacy-data"
    legacy_workspace = tmp_path / "legacy-workspace"
    legacy_renderer = tmp_path / "legacy-renderer"
    new_data = tmp_path / "new-data"
    new_workspace = tmp_path / "new-workspace"
    new_renderer = tmp_path / "new-renderer"

    monkeypatch.setenv("PPT_COURSE_DATA", str(legacy_data))
    monkeypatch.setenv("VIDEO_WORKSPACE_ROOT", str(legacy_workspace))
    monkeypatch.setenv("VIDEO_RENDERER_ROOT", str(legacy_renderer))
    monkeypatch.setenv("ANY2VIDEO_DATA_ROOT", str(new_data))
    monkeypatch.setenv("ANY2VIDEO_WORKSPACE_ROOT", str(new_workspace))
    monkeypatch.setenv("ANY2VIDEO_RENDERER_ROOT", str(new_renderer))

    assert get_data_root() == new_data.resolve()
    assert workspace_root() == new_workspace.resolve()
    assert renderer_root() == new_renderer.resolve()


def test_cleanup_removes_only_runtime_data(tmp_path: Path) -> None:
    config = tmp_path / "ppt_course_data" / "config" / "external_apis.json"
    connection_log = tmp_path / "ppt_course_data" / "minimax_connect_tests" / "test.json"
    old_task = tmp_path / "ppt_course_data" / "tasks" / "old" / "meta.json"
    old_audio = tmp_path / "ppt_course_data" / "audio_workspace" / "task" / "old" / "voice.mp3"
    old_project = tmp_path / "video_workspace" / "projects" / "old" / "project.json"
    render_root = tmp_path / "ppt_course_renderer" / "render_tasks"
    runtime_render = render_root / "v2-old" / "out" / "video.mp4"
    example = render_root / "product-experience-demo" / "video_project.json"
    legacy_example = render_root / "my-video-test1" / "input-props.json"
    caption_example = render_root / "task-2555-pages1-4" / "input-props.json"
    readme = render_root / "README.md"
    public_asset = tmp_path / "ppt_course_renderer" / "public" / "v2_assets" / "old" / "image.png"

    for path in (
        config,
        connection_log,
        old_task,
        old_audio,
        old_project,
        runtime_render,
        example,
        legacy_example,
        caption_example,
        readme,
        public_asset,
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"data")

    preview = cleanup_project_data(repo_root=tmp_path)
    assert preview["executed"] is False
    assert old_task.is_file()
    assert preview["file_count"] == 5

    report = cleanup_project_data(execute=True, repo_root=tmp_path)
    assert report["executed"] is True
    assert not old_task.exists()
    assert not old_audio.exists()
    assert not old_project.exists()
    assert not runtime_render.exists()
    assert not public_asset.exists()
    assert config.read_bytes() == b"data"
    assert connection_log.read_bytes() == b"data"
    assert example.read_bytes() == b"data"
    assert legacy_example.read_bytes() == b"data"
    assert caption_example.read_bytes() == b"data"
    assert readme.read_bytes() == b"data"


def test_cleanup_refuses_symlinked_targets(tmp_path: Path) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    data = tmp_path / "ppt_course_data"
    data.mkdir()
    (data / "tasks").symlink_to(outside, target_is_directory=True)

    with pytest.raises(RuntimeError, match="符号链接"):
        cleanup_project_data(repo_root=tmp_path)
