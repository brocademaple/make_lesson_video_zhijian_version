"""Real Chinese speech and Remotion acceptance. Run from the repository root.

    .venv/bin/python scripts/verify_stage1_speech.py

Creates a separate review project; does not modify existing projects.
Requires network access to Edge TTS, ffmpeg and installed renderer dependencies.
"""
from __future__ import annotations

import io
import array
import math
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw
from ppt_course_deal.web.app import create_app


def main():
    client = TestClient(create_app())
    if len(sys.argv) > 1:
        project = client.get("/api/v2/projects/" + sys.argv[1]).json()
        verify_result({"project": project, "output": project["outputs"][-1]})
        return
    project = client.post("/api/v2/projects", json={"title": "第一阶段验收 · 逐镜配音"}).json()
    base = f"/api/v2/projects/{project['id']}"
    text = "第一段，声音跟着镜头走。第二段，只改需要修改的旁白。"
    assert client.post(base + "/assets", data={"asset_type": "text", "content": text}).status_code == 200
    for index, color in enumerate(["#294f63", "#715043"]):
        image = Image.new("RGB", (720, 1280), color)
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((80, 210, 640, 820), radius=36, fill="#eee9df")
        draw.text((180, 370), f"SCENE {index + 1}", fill=color, font_size=68)
        stream = io.BytesIO()
        image.save(stream, "PNG")
        assert client.post(base + "/assets", data={"asset_type": "image", "title": f"验收画面 {index + 1}"}, files={"file": (f"scene-{index}.png", stream.getvalue(), "image/png")}).status_code == 200
    r = client.post(base + "/scene-plan/quick", json={"audio_mode": "segments"})
    assert r.status_code == 200, r.text
    voices = ["zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural"]
    for index, voice in enumerate(voices):
        r = client.post(base + f"/scenes/scene-00{index + 1}/speech", json={"voice": voice})
        assert r.status_code == 200, r.text
    original = client.get(base).json()["scene_plan"]["scenes"]
    assert client.put(base + "/scenes/scene-001", json={"narration": "第一段修改完成，只重做这一段。"}).status_code == 200
    assert client.post(base + "/render", json={"execute": False}).status_code == 409
    r = client.post(base + "/scenes/scene-001/speech", json={})
    assert r.status_code == 200, r.text
    modified = r.json()["scene"]
    assert modified["speech"]["asset_id"] != original[0]["speech"]["asset_id"]
    assert client.get(base).json()["scene_plan"]["scenes"][1] == original[1]
    r = client.post(base + "/scenes/scene-001/speech/restore", json={"asset_id": original[0]["speech"]["asset_id"]})
    assert r.status_code == 200, r.text
    assert r.json()["scene"]["narration"] == original[0]["narration"]
    r = client.post(base + "/render", json={"execute": True, "timeout_sec": 300})
    assert r.status_code == 200, r.text
    result = r.json()
    assert result["output"]["status"] == "ready", result["output"].get("log")
    verify_result(result)


def verify_result(result):
    project = result["project"]
    video = Path(result["output"]["video_path"])
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)], capture_output=True, text=True, check=True)
    meta = json.loads(probe.stdout)
    assert {s["codec_type"] for s in meta["streams"]} >= {"video", "audio"}
    duration = sum(s["duration_sec"] for s in result["project"]["scene_plan"]["scenes"])
    assert abs(float(meta["format"]["duration"]) - duration) < 0.1
    # Compare decoded audio on both sides of the scene boundary against the
    # source voices. Merely finding an AAC track would miss muted/reused audio.
    def decode(path):
        pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
        samples = array.array("f")
        samples.frombytes(pcm)
        return samples
    full = decode(video)
    offset = 0
    correlations = []
    offsets = []
    for scene in result["project"]["scene_plan"]["scenes"]:
        asset = next(a for a in result["project"]["assets"] if a["id"] == scene["speech"]["asset_id"])
        source = decode(asset["path"])
        # AAC encoding introduces a small shared delay. Find the source within
        # +/-75 ms, then compare full waveforms. A wrong/muted segment still fails.
        anchor = max(range(0, len(source) - 1024, 512), key=lambda start: sum(x * x for x in source[start:start + 1024]))
        points = list(range(anchor, min(anchor + 4096, len(source)), 16))
        def score(lag):
            valid = [i for i in points if 0 <= offset + lag + i < len(full)]
            return sum(source[i] * full[offset + lag + i] for i in valid)
        lag = max(range(-1200, 1201), key=score)
        aligned = offset + lag
        start = max(0, -aligned)
        length = min(len(source), len(full) - aligned)
        a, b = source[start:length], full[aligned + start:aligned + length]
        length = len(a)
        mean_a, mean_b = sum(a) / length, sum(b) / length
        covariance = sum((x - mean_a) * (y - mean_b) for x, y in zip(a, b))
        correlation = covariance / math.sqrt(sum((x - mean_a) ** 2 for x in a) * sum((y - mean_b) ** 2 for y in b))
        assert correlation > 0.95, correlation
        correlations.append(correlation)
        offsets.append(round(lag / 16000, 6))
        offset += round(scene["duration_sec"] * 16000)
    evidence = ROOT / "video_workspace" / "review-stage1"
    evidence.mkdir(parents=True, exist_ok=True)
    shutil.copy2(video, evidence / "逐镜配音验收.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-frames:v", "1", str(evidence / "成片首帧.png")], check=True)
    report = {"project_id": project["id"], "video": str(evidence / "逐镜配音验收.mp4"), "duration_sec": float(meta["format"]["duration"]), "source_audio_correlations": correlations, "audio_alignment_offsets_sec": offsets, "checks": ["真实中文双声音", "逐镜时长同步", "只重做一段", "过期配音阻止导出", "旧版本恢复", "MP4逐段声音与源音频一致"]}
    (evidence / "验收证据.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
