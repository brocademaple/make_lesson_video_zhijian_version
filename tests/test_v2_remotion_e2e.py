from __future__ import annotations

import io
import json
import math
import os
import struct
import subprocess
import wave
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from ppt_course_deal.web import app as web_app


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_REMOTION_E2E") != "1",
    reason="set RUN_REMOTION_E2E=1 to run the real Remotion render",
)


def _image_bytes(color: tuple[int, int, int]) -> bytes:
    target = io.BytesIO()
    Image.new("RGB", (720, 1280), color).save(target, format="PNG")
    return target.getvalue()


def _wav_bytes(duration_sec: float, sample_rate: int = 16000) -> bytes:
    target = io.BytesIO()
    with wave.open(target, "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        frames = bytearray()
        for index in range(round(duration_sec * sample_rate)):
            sample = int(7000 * math.sin(2 * math.pi * 330 * index / sample_rate))
            frames.extend(struct.pack("<h", sample))
        output.writeframes(bytes(frames))
    return target.getvalue()


def test_real_text_images_audio_render_contains_video_and_audio(monkeypatch, tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    renderer_root = repo_root / "ppt_course_renderer"
    monkeypatch.setenv("VIDEO_WORKSPACE_ROOT", str(tmp_path / "workspace"))
    monkeypatch.setenv("VIDEO_RENDERER_ROOT", str(renderer_root))
    client = TestClient(web_app.create_app())

    project_id = client.post("/api/v2/projects", json={"title": "Remotion MVP E2E"}).json()["id"]
    assert client.post(
        f"/api/v2/projects/{project_id}/assets",
        data={"asset_type": "text", "content": "文字进入画面。图片跟随旁白切换。最终得到真实视频。"},
    ).status_code == 200

    colors = [(52, 90, 150), (46, 120, 103), (151, 78, 72)]
    for index, color in enumerate(colors):
        response = client.post(
            f"/api/v2/projects/{project_id}/assets",
            data={"asset_type": "image", "title": f"测试画面 {index + 1}"},
            files={"file": (f"frame-{index + 1}.png", _image_bytes(color), "image/png")},
        )
        assert response.status_code == 200

    duration_sec = 2.4
    audio = client.post(
        f"/api/v2/projects/{project_id}/assets",
        data={"asset_type": "audio", "title": "测试旁白"},
        files={"file": ("voice.wav", _wav_bytes(duration_sec), "audio/wav")},
    )
    assert audio.status_code == 200
    assert abs(audio.json()["asset"]["duration_sec"] - duration_sec) < 0.01

    draft = client.post(f"/api/v2/projects/{project_id}/scene-plan/quick")
    assert draft.status_code == 200
    first_scene = draft.json()["scene_plan"]["scenes"][0]
    edited = client.put(
        f"/api/v2/projects/{project_id}/scenes/{first_scene['id']}",
        json={"title": "人工加长的开场", "duration_sec": 1.2},
    )
    assert edited.status_code == 200

    rendered = client.post(
        f"/api/v2/projects/{project_id}/render",
        json={"execute": True, "timeout_sec": 300},
    )
    assert rendered.status_code == 200
    payload = rendered.json()
    assert payload["output"]["status"] == "ready", payload["output"].get("log")
    assert len(payload["project"]["scene_plan"]["scenes"]) == 3
    assert payload["project"]["scene_plan"]["scenes"][0]["title"] == "人工加长的开场"

    video_path = Path(payload["output"]["video_path"])
    assert video_path.is_file()
    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-show_entries",
            "stream=codec_type,codec_name,width,height,avg_frame_rate",
            "-of",
            "json",
            str(video_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    metadata = json.loads(probe.stdout)
    streams = metadata["streams"]
    video = next(stream for stream in streams if stream["codec_type"] == "video")
    audio_stream = next(stream for stream in streams if stream["codec_type"] == "audio")
    assert video["codec_name"] == "h264"
    assert video["width"] == 1080
    assert video["height"] == 1920
    assert video["avg_frame_rate"] == "30/1"
    assert audio_stream["codec_name"] == "aac"
    assert abs(float(metadata["format"]["duration"]) - 2.8) <= 0.1
