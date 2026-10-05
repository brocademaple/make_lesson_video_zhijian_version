from pathlib import Path

import pytest

from ppt_course_deal import scene_speech, v2_workspace as ws
from ppt_course_deal.speech_synthesis import SpeechSynthesisError, SpeechSynthesisResult
from test_v2_video_workbench import _client, _wav_bytes, PNG_1X1


def setup_project(client, text="第一段旁白。第二段旁白。", image_count=2, mode="segments"):
    pid = client.post("/api/v2/projects", json={"title": "逐镜配音验收"}).json()["id"]
    base = f"/api/v2/projects/{pid}"
    client.post(base + "/assets", data={"asset_type": "text", "content": text})
    for i in range(image_count):
        client.post(base + "/assets", data={"asset_type": "image"}, files={"file": (f"{i}.png", PNG_1X1, "image/png")})
    if mode == "imported":
        client.post(base + "/assets", data={"asset_type": "audio"}, files={"file": ("voice.wav", _wav_bytes(4), "audio/wav")})
    response = client.post(base + "/scene-plan/quick", json={"audio_mode": mode})
    assert response.status_code == 200, response.text
    return base, response.json()["scene_plan"]


@pytest.fixture
def context(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)
    monkeypatch.setattr(scene_speech, "synthesize_speech", lambda **kw: SpeechSynthesisResult(_wav_bytes(1.213), "wav", "edge_tts"))
    return client, monkeypatch


def test_text_images_can_start_without_audio_and_preserve_full_narration(context):
    client, _ = context
    text = "长旁白" * 60 + "。"
    base, plan = setup_project(client, text=text)
    assert "".join(s["narration"] for s in plan["scenes"]) == text
    assert plan["scenes"][1]["narration"] == ""
    assert client.post(base + "/render", json={"execute": False}).status_code == 409


def test_version_restore_and_single_scene_regeneration(context):
    client, _ = context
    base, _ = setup_project(client)
    first = client.post(base + "/scenes/scene-001/speech", json={}).json()["scene"]
    assert first["duration_frames"] == 37
    assert first["duration_sec"] >= first["speech"]["duration_sec"]
    original = first["speech"]["asset_id"]
    second = client.post(base + "/scenes/scene-002/speech", json={}).json()["scene"]
    client.put(base + "/scenes/scene-001", json={"narration": "改过的旁白。"})
    stale = client.get(base).json()["scene_plan"]["scenes"][0]
    assert stale["speech"]["stale"]
    assert client.post(base + "/render", json={"execute": False}).status_code == 409
    new = client.post(base + "/scenes/scene-001/speech", json={}).json()["scene"]
    assert new["speech"]["asset_id"] != original
    assert len(new["speech_versions"]) == 2
    assert client.get(base).json()["scene_plan"]["scenes"][1] == second
    assert client.post(base + "/render-plan", json={}).status_code == 200
    restored = client.post(base + "/scenes/scene-001/speech/restore", json={"asset_id": original}).json()["scene"]
    assert restored["narration"] == "第一段旁白。"
    assert restored["speech"]["asset_id"] == original
    assert not restored["speech"]["stale"]
    assert len(client.get(base).json()["assets"]) == 6
    assert client.post(base + "/scenes/scene-002/speech/restore", json={"asset_id": original}).status_code == 404


def test_failure_preserves_audio_and_shortened_scene_blocks_render(context):
    client, monkeypatch = context
    base, _ = setup_project(client)
    original = client.post(base + "/scenes/scene-001/speech", json={}).json()["scene"]
    def fail(**kwargs):
        raise SpeechSynthesisError("private-token-must-not-leak")
    monkeypatch.setattr(scene_speech, "synthesize_speech", fail)
    response = client.post(base + "/scenes/scene-001/speech", json={})
    assert response.status_code == 502
    assert "private-token" not in response.text
    assert client.get(base).json()["scene_plan"]["scenes"][0] == original
    client.put(base + "/scenes/scene-001", json={"duration_sec": 0.5})
    assert client.post(base + "/render-plan", json={}).status_code == 409


def test_original_upload_survives_switch_to_scene_speech(context):
    client, _ = context
    base, plan = setup_project(client, mode="imported")
    aid = plan["primary_audio_asset_id"]
    client.post(base + "/scenes/scene-001/speech", json={})
    new = client.get(base).json()["scene_plan"]
    assert new["audio_mode"] == "segments"
    assert new["primary_audio_asset_id"] == ""
    assert new["imported_audio_asset_id"] == aid
    assert client.get(base + f"/assets/{aid}/file").status_code == 200
    assert client.post(base + "/render", json={"execute": False}).status_code == 409


def test_edit_during_synthesis_does_not_attach_old_voice(context):
    client, monkeypatch = context
    base, _ = setup_project(client)
    pid = base.rsplit("/", 1)[1]
    def concurrent(**kwargs):
        ws.update_scene(pid, "scene-001", ws.SceneUpdateBody(narration="后来修改的内容"))
        return SpeechSynthesisResult(_wav_bytes(1), "wav", "edge_tts")
    monkeypatch.setattr(scene_speech, "synthesize_speech", concurrent)
    assert client.post(base + "/scenes/scene-001/speech", json={}).status_code == 409
    scene = client.get(base).json()["scene_plan"]["scenes"][0]
    assert scene["narration"] == "后来修改的内容"
    assert not scene.get("speech")


def test_invalid_voice_speed_and_empty_narration(context):
    client, _ = context
    base, _ = setup_project(client)
    for payload, code in [({"voice": "invalid"}, 400), ({"provider": "unknown"}, 400), ({"speed": 9}, 422)]:
        assert client.post(base + "/scenes/scene-001/speech", json=payload).status_code == code
    client.put(base + "/scenes/scene-001", json={"narration": ""})
    assert client.post(base + "/scenes/scene-001/speech", json={}).status_code == 400


def test_export_fps_conversion_and_missing_audio(context):
    client, _ = context
    base, _ = setup_project(client, image_count=1)
    response = client.post(base + "/scenes/scene-001/speech", json={})
    assert response.status_code == 200
    scene = response.json()["scene"]
    plan_response = client.post(base + "/render-plan", json={"fps": 60})
    assert plan_response.status_code == 200
    import json
    props = json.loads(Path(plan_response.json()["render_plan"]["input_props_path"]).read_text())
    assert props["scenes"][0]["durationInFrames"] == 74
    asset = next(a for a in client.get(base).json()["assets"] if a["id"] == scene["speech"]["asset_id"])
    Path(asset["path"]).unlink()
    assert client.post(base + "/render-plan", json={}).status_code == 409
