from __future__ import annotations

import json
import time
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


def test_pipeline_state_exposes_middle_office_stages(monkeypatch, tmp_path: Path) -> None:
    task_id = "task-1"
    task_root = tmp_path / task_id
    task_root.mkdir()
    (task_root / "raw_material_manifest.json").write_text(
        '{"slides":[{"slide_id":"slide-0000"}]}',
        encoding="utf-8",
    )
    (task_root / "course_material.json").write_text(
        '{"slides":[{"slide_id":"slide-0000"}],"assets":[]}',
        encoding="utf-8",
    )

    monkeypatch.setattr(web_app, "tasks_dir", lambda: tmp_path)
    monkeypatch.setattr(web_app, "load_task", lambda tid: {
        "filename": "demo.pptx",
        "slide_count": 1,
        "slides": [{}],
        "images_available": True,
        "preview_count": 1,
        "preview_source": "libreoffice",
    })
    monkeypatch.setattr(web_app, "load_meta", lambda _kind, _key: {})
    monkeypatch.setattr(
        web_app,
        "render_task_status",
        lambda tid: {
            "task_dir": str(tmp_path / "render_tasks" / tid),
            "input_props_exists": False,
            "output_video_exists": False,
            "render_command": "npx remotion render ...",
        },
    )

    client = TestClient(web_app.create_app())
    res = client.get(f"/api/tasks/{task_id}/pipeline-state")

    assert res.status_code == 200
    data = res.json()
    labels = [stage["label"] for stage in data["pipeline"]["stages"]]
    assert "素材地图" in labels
    assert "导演台" in labels
    assert data["pipeline"]["stage_count"] == 7
    assert data["pipeline"]["ready_count"] >= 3


def test_pipeline_run_step_delegates_render_plan(monkeypatch) -> None:
    task_id = "task-1"
    received = {}

    monkeypatch.setattr(web_app, "load_task", lambda tid: {"task_id": tid, "slides": [{}]})

    def fake_write_render_plan(tid, **kwargs):
        received["tid"] = tid
        received["kwargs"] = kwargs
        return {
            "source": "director_manifest",
            "render_plan_path": "/tmp/render_plan.json",
            "input_props_path": "/tmp/input-props.json",
            "output_video_path": "/tmp/video.mp4",
            "render_command": "npx remotion render ...",
        }

    monkeypatch.setattr(web_app, "write_render_plan_from_task", fake_write_render_plan)

    client = TestClient(web_app.create_app())
    res = client.post(
        f"/api/tasks/{task_id}/pipeline/run-step",
        json={"step": "render_plan", "fps": 24, "max_slides": 4},
    )

    assert res.status_code == 200
    data = res.json()
    assert data["stage"] == "render_plan"
    assert data["source"] == "director_manifest"
    assert received["tid"] == task_id
    assert received["kwargs"]["fps"] == 24
    assert received["kwargs"]["max_scenes"] == 4


def test_pipeline_job_endpoint_runs_async_step(monkeypatch) -> None:
    task_id = "task-1"
    received = {}

    monkeypatch.setattr(web_app, "load_task", lambda tid: {"task_id": tid, "slides": [{}]})

    def fake_run_pipeline_step(tid, task, payload):
        received["tid"] = tid
        received["task"] = task
        received["step"] = payload.step
        return {"ok": True, "stage": payload.step, "message": "fake done"}

    monkeypatch.setattr(web_app, "run_pipeline_step", fake_run_pipeline_step)

    client = TestClient(web_app.create_app())
    create_res = client.post(
        f"/api/tasks/{task_id}/pipeline/jobs",
        json={"step": "render_plan"},
    )

    assert create_res.status_code == 202
    job_id = create_res.json()["job_id"]
    final = None
    for _ in range(20):
        poll_res = client.get(f"/api/pipeline/jobs/{job_id}")
        assert poll_res.status_code == 200
        final = poll_res.json()
        if final["status"] == "succeeded":
            break
        time.sleep(0.05)

    assert final is not None
    assert final["status"] == "succeeded"
    assert final["result"]["message"] == "fake done"
    assert received["tid"] == task_id
    assert received["step"] == "render_plan"


def test_pipeline_audio_step_reports_missing_artifacts(monkeypatch, tmp_path: Path) -> None:
    task_id = "task-1"
    monkeypatch.setattr(web_app, "tasks_dir", lambda: tmp_path)
    monkeypatch.setattr(web_app, "load_task", lambda tid: {
        "filename": "demo.pptx",
        "slide_count": 1,
        "slides": [{}],
        "images_available": True,
        "preview_count": 1,
    })
    monkeypatch.setattr(web_app, "load_meta", lambda _kind, _key: {})
    monkeypatch.setattr(
        web_app,
        "render_task_status",
        lambda tid: {"task_dir": str(tmp_path / "render_tasks" / tid)},
    )

    client = TestClient(web_app.create_app())
    res = client.post(
        f"/api/tasks/{task_id}/pipeline/run-step",
        json={"step": "audio"},
    )

    assert res.status_code == 400
    detail = res.json()["detail"]
    assert detail["stage"] == "audio"
    assert "audio_workspace/generated_files" in detail["missing_artifacts"]


def test_output_video_endpoint_serves_rendered_mp4(monkeypatch, tmp_path: Path) -> None:
    task_id = "task-1"
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake-mp4")

    monkeypatch.setattr(web_app, "load_task", lambda tid: {"task_id": tid})
    monkeypatch.setattr(
        web_app,
        "render_task_status",
        lambda tid: {"output_video_path": str(video), "output_video_exists": True},
    )

    client = TestClient(web_app.create_app())
    res = client.get(f"/api/tasks/{task_id}/output-video")

    assert res.status_code == 200
    assert res.content == b"fake-mp4"
    assert res.headers["content-type"].startswith("video/mp4")


def test_videos_endpoint_summarizes_rendered_projects(monkeypatch, tmp_path: Path) -> None:
    task_id = "task-1"
    render_dir = tmp_path / "render_tasks" / task_id
    render_dir.mkdir(parents=True)
    (render_dir / "render_plan.json").write_text(
        '{"engine_counts":{"hybrid":2},"duration_sec":12.5}',
        encoding="utf-8",
    )
    task_root = tmp_path / "tasks" / task_id
    task_root.mkdir(parents=True)
    (task_root / "meta.json").write_text("{}", encoding="utf-8")

    monkeypatch.setattr(web_app, "tasks_dir", lambda: tmp_path / "tasks")
    monkeypatch.setattr(
        web_app,
        "list_task_summaries",
        lambda: [
            {
                "id": task_id,
                "filename": "demo.pdf",
                "source_type": "pdf",
                "project_kind": "training",
                "slide_count": 3,
                "created_at": "2026-06-07T00:00:00Z",
                "has_render_plan": True,
                "has_director_manifest": True,
            }
        ],
    )
    monkeypatch.setattr(
        web_app,
        "render_task_status",
        lambda tid: {
            "task_dir": str(render_dir),
            "output_video_exists": True,
            "output_video_path": str(render_dir / "out" / "video.mp4"),
            "duration_sec": 12.5,
        },
    )

    client = TestClient(web_app.create_app())
    res = client.get("/api/videos")

    assert res.status_code == 200
    data = res.json()
    assert data["output_count"] == 1
    video = data["videos"][0]
    assert video["task_id"] == task_id
    assert video["output_video_url"] == f"/api/tasks/{task_id}/output-video"
    assert video["render_engine_counts"] == {"hybrid": 2}
    assert video["source_type_label"] == "PDF"


def test_render_artifacts_endpoint_returns_raw_and_explanation(monkeypatch, tmp_path: Path) -> None:
    task_id = "task-1"
    render_dir = tmp_path / "render_tasks" / task_id
    render_dir.mkdir(parents=True)
    input_props_path = render_dir / "input-props.json"
    render_plan_path = render_dir / "render_plan.json"
    render_plan_path.write_text(
        json.dumps(
            {
                "engine_counts": {"hyperframes_creative": 1},
                "timeline_items": [
                    {
                        "scene_id": "s1",
                        "scene_role": "intro",
                        "render_engine": "hyperframes_creative",
                        "fallback_engine": "remotion_stable",
                        "start_frame": 0,
                        "duration_frames": 60,
                        "end_frame": 60,
                        "source_slide_ids": ["slide-0000"],
                        "creative_asset": {"exists": False},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    input_props_path.write_text(
        json.dumps(
            {
                "fps": 30,
                "slides": [
                    {
                        "sceneId": "s1",
                        "durationInFrames": 60,
                        "caption": {"title": "开场页"},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(web_app, "load_task", lambda tid: {"task_id": tid})
    monkeypatch.setattr(
        web_app,
        "render_task_status",
        lambda tid: {
            "task_dir": str(render_dir),
            "input_props_path": str(input_props_path),
            "input_props_exists": True,
            "output_video_path": str(render_dir / "out" / "video.mp4"),
            "output_video_exists": False,
            "render_command": "npx remotion render ...",
        },
    )

    client = TestClient(web_app.create_app())
    res = client.get(f"/api/tasks/{task_id}/render-artifacts")

    assert res.status_code == 200
    data = res.json()
    assert data["render_plan_raw"]["engine_counts"] == {"hyperframes_creative": 1}
    assert data["input_props_raw"]["fps"] == 30
    assert data["explanation"]["summary"]["timeline_item_count"] == 1
    assert data["explanation"]["summary"]["fallback_count"] == 1
    assert data["explanation"]["timeline"][0]["role_label"] == "片头"
    assert "回退 Remotion" in data["explanation"]["timeline"][0]["status"]


def test_render_artifacts_endpoint_handles_missing_files(monkeypatch, tmp_path: Path) -> None:
    task_id = "task-1"
    render_dir = tmp_path / "render_tasks" / task_id
    render_dir.mkdir(parents=True)

    monkeypatch.setattr(web_app, "load_task", lambda tid: {"task_id": tid})
    monkeypatch.setattr(
        web_app,
        "render_task_status",
        lambda tid: {
            "task_dir": str(render_dir),
            "input_props_path": str(render_dir / "input-props.json"),
            "input_props_exists": False,
            "output_video_path": str(render_dir / "out" / "video.mp4"),
            "output_video_exists": False,
        },
    )

    client = TestClient(web_app.create_app())
    res = client.get(f"/api/tasks/{task_id}/render-artifacts")

    assert res.status_code == 200
    data = res.json()
    assert data["render_plan_raw"] == {}
    assert data["input_props_raw"] == {}
    assert data["file_paths"]["render_plan_exists"] is False
    assert data["explanation"]["risks"]
