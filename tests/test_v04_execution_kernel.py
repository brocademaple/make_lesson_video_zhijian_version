from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

from fastapi.testclient import TestClient

from ppt_course_deal import v2_workspace
from ppt_course_deal.execution_kernel import (
    apply_scene_routes,
    discover_capabilities,
    route_scene_engine,
)
from ppt_course_deal.web import app as web_app


PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
    b"\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04"
    b"\x00\x01\xf6\x178U\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _wav_bytes() -> bytes:
    spec = importlib.util.spec_from_file_location("v2_test_helpers", Path(__file__).with_name("test_v2_video_workbench.py"))
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._wav_bytes(2.0)


def _client(monkeypatch, tmp_path: Path) -> TestClient:
    workspace = tmp_path / "workspace"
    renderer = tmp_path / "renderer"
    (renderer / "public").mkdir(parents=True)
    (renderer / "render_tasks").mkdir()
    monkeypatch.setenv("VIDEO_WORKSPACE_ROOT", str(workspace))
    monkeypatch.setenv("VIDEO_RENDERER_ROOT", str(renderer))
    return TestClient(web_app.create_app())


def _project_with_scenes(client: TestClient) -> tuple[str, list[dict]]:
    project_id = client.post("/api/v2/projects", json={"title": "V0.4 双引擎"}).json()["id"]
    client.post(
        f"/api/v2/projects/{project_id}/assets",
        data={"asset_type": "text", "content": "开场建立识别。第二镜解释流程。第三镜收束结论。"},
    )
    for index in range(3):
        client.post(
            f"/api/v2/projects/{project_id}/assets",
            data={"asset_type": "image", "title": f"画面 {index + 1}"},
            files={"file": (f"scene-{index + 1}.png", PNG_1X1, "image/png")},
        )
    client.post(
        f"/api/v2/projects/{project_id}/assets",
        data={"asset_type": "audio"},
        files={"file": ("voice.wav", _wav_bytes(), "audio/wav")},
    )
    response = client.post(f"/api/v2/projects/{project_id}/scene-plan/quick")
    assert response.status_code == 200
    return project_id, response.json()["scene_plan"]["scenes"]


def test_v04_auto_router_is_explainable_and_honors_manual_override() -> None:
    scenes = [
        {"id": "a", "purpose": "开场", "renderer": "auto"},
        {"id": "b", "purpose": "解释流程", "renderer": "auto"},
        {"id": "c", "purpose": "说明罚款金额 10 万元", "renderer": "auto"},
        {"id": "d", "purpose": "结尾", "renderer": "auto"},
    ]
    apply_scene_routes(scenes)
    assert [scene["engine"]["resolved"] for scene in scenes] == [
        "hyperframes",
        "hybrid",
        "remotion",
        "hyperframes",
    ]
    assert all(scene["engine"]["reason"] for scene in scenes)
    manual = route_scene_engine({"renderer": "remotion", "purpose": "创意开场"}, 0, 3)
    assert manual["resolved"] == "remotion"
    assert "手动指定" in manual["reason"]


def test_v04_capability_registry_has_local_execution_contract(tmp_path: Path) -> None:
    registry = discover_capabilities(tmp_path / "renderer", tmp_path / "workspace")
    ids = {item["id"] for item in registry["capabilities"]}
    assert registry["schema_version"] == "capability_registry.v1"
    assert registry["local_first"] is True
    assert {"storage.local", "remotion.render_project", "hyperframes.render_scene", "media.ffmpeg"} <= ids


def test_v04_prepare_sources_and_persist_run_ledger(monkeypatch, tmp_path: Path) -> None:
    client = _client(monkeypatch, tmp_path)
    project_id, scenes = _project_with_scenes(client)
    response = client.post(
        f"/api/v2/projects/{project_id}/creative-scenes/prepare",
        json={"execute": False},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["run"]["status"] == "ready"
    assert payload["tasks"]
    for task in payload["tasks"]:
        source = Path(task["source_html"])
        assert source.is_file()
        assert (source.parent / "DESIGN.md").is_file()
        assert (source.parent / "creative_brief.json").is_file()
    detail = client.get(f"/api/v2/projects/{project_id}").json()
    assert detail["runs"][0]["id"] == payload["run"]["id"]
    by_id = {scene["id"]: scene for scene in detail["scene_plan"]["scenes"]}
    assert all(by_id[task["scene_id"]]["engine"]["status"] == "prepared" for task in payload["tasks"])
    invalid = client.put(
        f"/api/v2/projects/{project_id}/scenes/{scenes[0]['id']}",
        json={"renderer": "unknown-engine"},
    )
    assert invalid.status_code == 400


def test_v04_hyperframes_failure_falls_back_without_blocking_plan(monkeypatch, tmp_path: Path) -> None:
    client = _client(monkeypatch, tmp_path)
    project_id, scenes = _project_with_scenes(client)
    monkeypatch.setattr(v2_workspace, "hyperframes_command", lambda registry, allow_on_demand=False: [])
    response = client.post(
        f"/api/v2/projects/{project_id}/scenes/{scenes[0]['id']}/prepare",
        json={"execute": True, "allow_on_demand": False},
    )
    assert response.status_code == 200
    assert response.json()["tasks"][0]["status"] == "fallback"
    assert response.json()["project"]["scene_plan"]["scenes"][0]["engine"]["status"] == "fallback"
    planned = client.post(f"/api/v2/projects/{project_id}/render", json={"execute": False})
    assert planned.status_code == 200
    assert planned.json()["output"]["status"] == "planned"
    assert planned.json()["output"]["run_id"]


def test_v04_ready_creative_clip_enters_unified_remotion_props(monkeypatch, tmp_path: Path) -> None:
    client = _client(monkeypatch, tmp_path)
    project_id, scenes = _project_with_scenes(client)
    monkeypatch.setattr(v2_workspace, "hyperframes_command", lambda registry, allow_on_demand=False: ["hyperframes"])

    def fake_hyperframes(command, **kwargs):
        output_path = Path(command[command.index("--output") + 1])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"creative clip")
        return subprocess.CompletedProcess(command, 0, "rendered", "")

    monkeypatch.setattr(v2_workspace.subprocess, "run", fake_hyperframes)
    prepared = client.post(
        f"/api/v2/projects/{project_id}/scenes/{scenes[0]['id']}/prepare",
        json={"execute": True},
    )
    assert prepared.status_code == 200
    assert prepared.json()["tasks"][0]["status"] == "ready"
    plan = client.post(f"/api/v2/projects/{project_id}/render-plan", json={"fps": 30})
    assert plan.status_code == 200
    first = plan.json()["render_plan"]["props"]["scenes"][0]
    assert first["rendererResolved"] == "hyperframes"
    assert first["rendererStatus"] == "ready"
    assert first["creativeAsset"]["relative"].endswith("clip.mp4")

    monkeypatch.setattr(v2_workspace, "hyperframes_command", lambda registry, allow_on_demand=False: [])

    def fake_remotion(command, **kwargs):
        assert command[:2] == ["npx", "remotion"]
        output_path = Path(command[5])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"final video with creative layer")
        return subprocess.CompletedProcess(command, 0, "rendered", "")

    monkeypatch.setattr(v2_workspace.subprocess, "run", fake_remotion)
    rendered = client.post(f"/api/v2/projects/{project_id}/render", json={"execute": True})
    assert rendered.status_code == 200
    assert rendered.json()["output"]["status"] == "ready"
    rendered_scene = rendered.json()["project"]["render_plan"]["props"]["scenes"][0]
    assert rendered_scene["creativeAsset"]["relative"].endswith("clip.mp4")
    assert rendered_scene["rendererStatus"] == "ready"
