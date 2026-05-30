from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from ppt_course_deal.web import app as web_app


def test_rebuild_course_accepts_llm_options(monkeypatch, tmp_path: Path) -> None:
    task_id = "task-1"
    raw_path = tmp_path / task_id / "raw_material_manifest.json"
    raw_path.parent.mkdir(parents=True)
    raw_path.write_text("{}", encoding="utf-8")

    received = {}

    monkeypatch.setattr(web_app, "load_task", lambda tid: {"task_id": tid})
    monkeypatch.setattr(web_app, "tasks_dir", lambda: tmp_path)
    monkeypatch.setattr(web_app, "build_raw_material_manifest", lambda tid: {})

    def fake_rebuild(raw, out, options):
        received["raw"] = raw
        received["out"] = out
        received["options"] = options
        return {
            "assets": [],
            "scenes": [{"scene_id": "s1"}],
            "generation": {
                "planning_mode": "heuristic_v1",
                "llm_model": "",
                "llm_error": "disabled",
            },
        }

    monkeypatch.setattr(web_app, "rebuild_course_from_raw_manifest", fake_rebuild)

    client = TestClient(web_app.create_app())
    res = client.post(
        f"/api/tasks/{task_id}/rebuild-course",
        json={"use_llm": False, "llm_max_slides": 3},
    )

    assert res.status_code == 200
    data = res.json()
    assert data["planning_mode"] == "heuristic_v1"
    assert data["llm_error"] == "disabled"
    assert received["options"] == {"use_llm": False, "llm_max_slides": 3}


def test_remotion_render_task_endpoint_returns_command(monkeypatch) -> None:
    task_id = "task-1"

    monkeypatch.setattr(web_app, "load_task", lambda tid: {"task_id": tid})

    def fake_create_render_task(tid, **kwargs):
        assert tid == task_id
        assert kwargs["fps"] == 24
        return {
            "task_name": "task-1",
            "input_props_path": "/tmp/render_tasks/task-1/input-props.json",
            "output_video_path": "/tmp/render_tasks/task-1/out/video.mp4",
            "render_command": "cd renderer && npx remotion render ...",
            "slide_count": 2,
            "total_frames": 120,
            "duration_sec": 5,
            "audio_slide_count": 1,
            "missing_audio_slide_indexes": [1],
        }

    monkeypatch.setattr(web_app, "create_render_task", fake_create_render_task)

    client = TestClient(web_app.create_app())
    res = client.post(
        f"/api/tasks/{task_id}/remotion-render-task",
        json={"fps": 24, "no_audio_frames": 72},
    )

    assert res.status_code == 200
    data = res.json()
    assert data["task_id"] == task_id
    assert data["input_props_path"].endswith("input-props.json")
    assert data["missing_audio_slide_indexes"] == [1]
    assert "remotion render" in data["render_command"]


def test_remotion_render_plan_endpoint_prefers_adapter(monkeypatch) -> None:
    task_id = "task-1"

    monkeypatch.setattr(web_app, "load_task", lambda tid: {"task_id": tid})

    def fake_write_render_plan(tid, **kwargs):
        assert tid == task_id
        assert kwargs["fps"] == 24
        return {
            "source": "director_manifest",
            "render_plan_path": "/tmp/render_tasks/task-1/render_plan.json",
            "input_props_path": "/tmp/render_tasks/task-1/input-props.json",
            "output_video_path": "/tmp/render_tasks/task-1/out/video.mp4",
            "render_command": "cd renderer && npx remotion render ...",
            "slide_count": 1,
            "total_frames": 120,
            "duration_sec": 5,
            "audio_slide_count": 0,
            "missing_audio_slide_indexes": [0],
        }

    monkeypatch.setattr(web_app, "write_render_plan_from_task", fake_write_render_plan)

    client = TestClient(web_app.create_app())
    res = client.post(
        f"/api/tasks/{task_id}/remotion-render-plan",
        json={"fps": 24, "no_audio_frames": 72},
    )

    assert res.status_code == 200
    data = res.json()
    assert data["source"] == "director_manifest"
    assert data["render_plan_path"].endswith("render_plan.json")


def test_workspace_status_summarizes_subsystems(monkeypatch, tmp_path: Path) -> None:
    task_id = "task-1"
    task_root = tmp_path / task_id
    task_root.mkdir()
    (task_root / "raw_material_manifest.json").write_text(
        '{"slides":[{"slide_id":"slide-0000"}]}',
        encoding="utf-8",
    )
    (task_root / "director_manifest.json").write_text(
        '{"assets":[{}],"scenes":[{"scene_id":"s1"}],"review":{"pending_count":1},"generation":{"planning_mode":"llm_director_v0"}}',
        encoding="utf-8",
    )

    task = {
        "filename": "demo.pptx",
        "slide_count": 1,
        "slides": [{}],
        "images_available": True,
        "preview_count": 1,
        "preview_source": "libreoffice",
    }

    monkeypatch.setattr(web_app, "tasks_dir", lambda: tmp_path)
    monkeypatch.setattr(
        web_app,
        "load_meta",
        lambda _kind, _key: {
            "transcript_segments": [["hello"]],
            "generated_files": {"0-0": "slide-0000/a.mp3"},
            "segment_duration_sec": {"0-0": 2.5},
        },
    )
    monkeypatch.setattr(
        web_app,
        "render_task_status",
        lambda tid: {
            "input_props_exists": True,
            "output_video_exists": False,
            "total_frames": 75,
            "missing_audio_slide_indexes": [],
        },
    )

    status = web_app.build_task_workspace_status(task_id, task)

    assert status["deal"]["images_available"] is True
    assert status["audio"]["slides_with_audio"] == 1
    assert status["rebuilder"]["raw_manifest_exists"] is True
    assert status["rebuilder"]["director_manifest_exists"] is True
    assert status["rebuilder"]["planning_mode"] == "llm_director_v0"
    assert status["remotion"]["input_props_exists"] is True
