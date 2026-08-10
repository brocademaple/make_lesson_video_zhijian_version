from __future__ import annotations

import json
import io
import math
import struct
import subprocess
import wave
from pathlib import Path

from fastapi.testclient import TestClient

from ppt_course_deal.web import app as web_app
from ppt_course_deal import v2_workspace


PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
    b"\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04"
    b"\x00\x01\xf6\x178U\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _wav_bytes(duration_sec: float = 2.0, sample_rate: int = 8000) -> bytes:
    buffer = io.BytesIO()
    frame_count = round(duration_sec * sample_rate)
    with wave.open(buffer, "wb") as target:
        target.setnchannels(1)
        target.setsampwidth(2)
        target.setframerate(sample_rate)
        frames = bytearray()
        for index in range(frame_count):
            sample = int(6000 * math.sin(2 * math.pi * 440 * index / sample_rate))
            frames.extend(struct.pack("<h", sample))
        target.writeframes(bytes(frames))
    return buffer.getvalue()


def _client(monkeypatch, tmp_path: Path) -> TestClient:
    workspace = tmp_path / "workspace"
    renderer = tmp_path / "renderer"
    (renderer / "public").mkdir(parents=True)
    (renderer / "render_tasks").mkdir()
    monkeypatch.setenv("VIDEO_WORKSPACE_ROOT", str(workspace))
    monkeypatch.setenv("VIDEO_RENDERER_ROOT", str(renderer))
    return TestClient(web_app.create_app())


def test_v2_project_assets_scene_and_render_plan(monkeypatch, tmp_path: Path) -> None:
    client = _client(monkeypatch, tmp_path)

    created = client.post(
        "/api/v2/projects",
        json={
            "title": "我的产品介绍视频",
            "goal": "用图片和旁白介绍一个新工具",
            "aspect_ratio": "9:16",
            "target_duration_sec": 18,
        },
    )
    assert created.status_code == 200
    project_id = created.json()["id"]

    text_res = client.post(
        f"/api/v2/projects/{project_id}/assets",
        data={
            "asset_type": "text",
            "title": "核心文案",
            "content": "这是一个把文本、图片、音频变成短视频的个人工具台。",
        },
    )
    assert text_res.status_code == 200
    text_asset = text_res.json()["asset"]
    assert text_asset["type"] == "text"
    assert text_asset["char_count"] > 0

    image_res = client.post(
        f"/api/v2/projects/{project_id}/assets",
        data={"asset_type": "image", "title": "主视觉"},
        files={"file": ("hero.png", PNG_1X1, "image/png")},
    )
    assert image_res.status_code == 200
    image_asset = image_res.json()["asset"]
    assert image_asset["type"] == "image"
    assert image_asset["width"] == 1
    assert image_asset["renderer_relative"].startswith("v2_assets/")

    audio_res = client.post(
        f"/api/v2/projects/{project_id}/assets",
        data={"asset_type": "audio", "title": "旁白"},
        files={"file": ("voice.mp3", b"ID3\x00\x00\x00", "audio/mpeg")},
    )
    assert audio_res.status_code == 200
    audio_asset = audio_res.json()["asset"]
    assert audio_asset["type"] == "audio"

    brief = client.post(
        f"/api/v2/projects/{project_id}/brief",
        json={"goal": "做一个 18 秒产品介绍", "style": "clean", "audience": "个人创作者"},
    )
    assert brief.status_code == 200

    scene_plan = client.post(f"/api/v2/projects/{project_id}/scene-plan")
    assert scene_plan.status_code == 200
    scenes = scene_plan.json()["scene_plan"]["scenes"]
    assert scenes

    scene_id = scenes[0]["id"]
    updated = client.put(
        f"/api/v2/projects/{project_id}/scenes/{scene_id}",
        json={
            "asset_ids": [text_asset["id"], image_asset["id"], audio_asset["id"]],
            "onscreen_text": "素材库到 Scene 工作台",
            "narration": "先把材料整理成可导演的镜头。",
            "duration_sec": 4,
            "renderer": "remotion",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["scene"]["asset_ids"] == [
        text_asset["id"],
        image_asset["id"],
        audio_asset["id"],
    ]

    render = client.post(
        f"/api/v2/projects/{project_id}/render-plan",
        json={"fps": 30, "no_audio_seconds": 4},
    )
    assert render.status_code == 200
    plan = render.json()["render_plan"]
    input_props_path = Path(plan["input_props_path"])
    assert input_props_path.is_file()
    props = json.loads(input_props_path.read_text(encoding="utf-8"))
    assert props["schemaVersion"] == "visual_project_props.v1"
    assert props["scenes"][0]["asset"]["relative"].startswith("v2_assets/")
    assert props["scenes"][0]["audio"]["relative"].startswith("v2_assets/")

    output = client.post(f"/api/v2/projects/{project_id}/render", json={"execute": False})
    assert output.status_code == 200
    output_meta = output.json()["output"]
    assert output_meta["status"] == "planned"
    assert client.get(output_meta["file_url"]).status_code == 409


def test_quick_compose_uses_audio_duration_and_unique_outputs(monkeypatch, tmp_path: Path) -> None:
    client = _client(monkeypatch, tmp_path)
    project_id = client.post("/api/v2/projects", json={"title": "真实素材 MVP"}).json()["id"]

    text = client.post(
        f"/api/v2/projects/{project_id}/assets",
        data={"asset_type": "text", "content": "第一张介绍产品。第二张展示流程。第三张给出结果。"},
    )
    assert text.status_code == 200
    for index in range(3):
        image = client.post(
            f"/api/v2/projects/{project_id}/assets",
            data={"asset_type": "image", "title": f"画面 {index + 1}"},
            files={"file": (f"image-{index + 1}.png", PNG_1X1, "image/png")},
        )
        assert image.status_code == 200
    audio = client.post(
        f"/api/v2/projects/{project_id}/assets",
        data={"asset_type": "audio", "title": "主旁白"},
        files={"file": ("voice.wav", _wav_bytes(2.0), "audio/wav")},
    )
    assert audio.status_code == 200
    assert audio.json()["asset"]["duration_sec"] == 2.0

    def fake_render(command, **kwargs):
        output_path = Path(command[5])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"rendered mp4")
        return subprocess.CompletedProcess(command, 0, "rendered", "")

    monkeypatch.setattr(v2_workspace.subprocess, "run", fake_render)
    first = client.post(f"/api/v2/projects/{project_id}/render", json={"execute": True})
    assert first.status_code == 200
    first_output = first.json()["output"]
    assert first_output["status"] == "ready"

    project = first.json()["project"]
    plan = project["render_plan"]
    props = plan["props"]
    assert plan["fps"] == 30
    assert plan["total_frames"] == 60
    assert plan["duration_sec"] == 2.0
    assert len(props["scenes"]) == 3
    assert sum(scene["durationInFrames"] for scene in props["scenes"]) == 60
    assert [scene["durationInFrames"] for scene in props["scenes"]] == [20, 20, 20]
    assert [scene["asset"]["label"] for scene in props["scenes"]] == ["画面 1", "画面 2", "画面 3"]
    assert props["audio"]["relative"].endswith("voice.wav")
    assert all(not scene.get("audio") for scene in props["scenes"])

    second = client.post(f"/api/v2/projects/{project_id}/render", json={"execute": True})
    assert second.status_code == 200
    second_output = second.json()["output"]
    assert second_output["status"] == "ready"
    assert second_output["video_path"] != first_output["video_path"]


def test_quick_compose_reports_missing_and_invalid_audio(monkeypatch, tmp_path: Path) -> None:
    client = _client(monkeypatch, tmp_path)
    project_id = client.post("/api/v2/projects", json={"title": "缺素材"}).json()["id"]
    missing = client.post(f"/api/v2/projects/{project_id}/render", json={"execute": True})
    assert missing.status_code == 400
    assert "文字" in missing.json()["detail"]
    assert "图片" in missing.json()["detail"]
    assert "旁白音频" in missing.json()["detail"]

    client.post(
        f"/api/v2/projects/{project_id}/assets",
        data={"asset_type": "text", "content": "有效文字"},
    )
    client.post(
        f"/api/v2/projects/{project_id}/assets",
        data={"asset_type": "image"},
        files={"file": ("image.png", PNG_1X1, "image/png")},
    )
    client.post(
        f"/api/v2/projects/{project_id}/assets",
        data={"asset_type": "audio"},
        files={"file": ("broken.mp3", b"not audio", "audio/mpeg")},
    )
    invalid = client.post(f"/api/v2/projects/{project_id}/render", json={"execute": True})
    assert invalid.status_code == 400
    assert "无法解析旁白音频时长" in invalid.json()["detail"]


def test_v03_scene_director_crud_order_and_render_preserves_edits(monkeypatch, tmp_path: Path) -> None:
    client = _client(monkeypatch, tmp_path)
    project_id = client.post("/api/v2/projects", json={"title": "V0.3 导演台"}).json()["id"]
    text_asset = client.post(
        f"/api/v2/projects/{project_id}/assets",
        data={"asset_type": "text", "content": "第一镜介绍问题。第二镜展示方案。"},
    ).json()["asset"]
    image_ids = []
    for index in range(2):
        response = client.post(
            f"/api/v2/projects/{project_id}/assets",
            data={"asset_type": "image", "title": f"导演画面 {index + 1}"},
            files={"file": (f"director-{index + 1}.png", PNG_1X1, "image/png")},
        )
        image_ids.append(response.json()["asset"]["id"])
    client.post(
        f"/api/v2/projects/{project_id}/assets",
        data={"asset_type": "audio", "title": "导演旁白"},
        files={"file": ("director.wav", _wav_bytes(4.0), "audio/wav")},
    )

    quick = client.post(f"/api/v2/projects/{project_id}/scene-plan/quick")
    assert quick.status_code == 200
    first, second = quick.json()["scene_plan"]["scenes"]

    updated = client.put(
        f"/api/v2/projects/{project_id}/scenes/{first['id']}",
        json={
            "title": "手工修改的开场",
            "onscreen_text": "先看真实问题",
            "narration": "这是用户保存后的导演稿。",
            "duration_sec": 1.5,
            "asset_ids": [text_asset["id"], image_ids[1]],
        },
    )
    assert updated.status_code == 200

    duplicated = client.post(f"/api/v2/projects/{project_id}/scenes/{first['id']}/duplicate")
    assert duplicated.status_code == 200
    duplicate_id = duplicated.json()["scene"]["id"]
    created = client.post(
        f"/api/v2/projects/{project_id}/scenes",
        json={"after_scene_id": duplicate_id, "title": "新增收束镜头", "duration_sec": 0.5},
    )
    assert created.status_code == 200
    created_id = created.json()["scene"]["id"]

    order = [created_id, second["id"], first["id"], duplicate_id]
    reordered = client.put(
        f"/api/v2/projects/{project_id}/scene-order",
        json={"scene_ids": order},
    )
    assert reordered.status_code == 200
    assert [scene["id"] for scene in reordered.json()["scenes"]] == order

    deleted = client.delete(f"/api/v2/projects/{project_id}/scenes/{duplicate_id}")
    assert deleted.status_code == 200
    assert deleted.json()["scene_count"] == 3

    def fake_render(command, **kwargs):
        output_path = Path(command[5])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"v03 rendered mp4")
        return subprocess.CompletedProcess(command, 0, "rendered", "")

    monkeypatch.setattr(v2_workspace.subprocess, "run", fake_render)
    rendered = client.post(f"/api/v2/projects/{project_id}/render", json={"execute": True})
    assert rendered.status_code == 200
    payload = rendered.json()
    assert payload["output"]["status"] == "ready"
    scenes = payload["project"]["scene_plan"]["scenes"]
    assert [scene["id"] for scene in scenes] == [created_id, second["id"], first["id"]]
    assert next(scene for scene in scenes if scene["id"] == first["id"])["title"] == "手工修改的开场"
    props = payload["project"]["render_plan"]["props"]["scenes"]
    assert [scene["id"] for scene in props] == [created_id, second["id"], first["id"]]
    assert next(scene for scene in props if scene["id"] == first["id"])["title"] == "手工修改的开场"


def test_text_over_mvp_limit_is_rejected(monkeypatch, tmp_path: Path) -> None:
    client = _client(monkeypatch, tmp_path)
    project_id = client.post("/api/v2/projects", json={"title": "文字限制"}).json()["id"]
    response = client.post(
        f"/api/v2/projects/{project_id}/assets",
        data={"asset_type": "text", "content": "字" * 301},
    )
    assert response.status_code == 400
    assert "最多 300 字" in response.json()["detail"]


def test_supported_image_metadata_and_format_validation(monkeypatch, tmp_path: Path) -> None:
    client = _client(monkeypatch, tmp_path)
    project_id = client.post("/api/v2/projects", json={"title": "图片格式"}).json()["id"]
    svg = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360"></svg>'
    response = client.post(
        f"/api/v2/projects/{project_id}/assets",
        data={"asset_type": "image"},
        files={"file": ("cover.svg", svg, "image/svg+xml")},
    )
    assert response.status_code == 200
    assert response.json()["asset"]["width"] == 640
    assert response.json()["asset"]["height"] == 360

    unsupported = client.post(
        f"/api/v2/projects/{project_id}/assets",
        data={"asset_type": "image"},
        files={"file": ("animation.gif", b"GIF89a", "image/gif")},
    )
    assert unsupported.status_code == 400
    assert "PNG、JPEG、WebP 或 SVG" in unsupported.json()["detail"]


def test_v2_missing_project_returns_404(monkeypatch, tmp_path: Path) -> None:
    client = _client(monkeypatch, tmp_path)
    res = client.get("/api/v2/projects/missing")
    assert res.status_code == 404
