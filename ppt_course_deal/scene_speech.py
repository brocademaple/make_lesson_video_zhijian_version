"""Versioned speech for individual director scenes; original assets stay intact."""
from __future__ import annotations

import math
import mimetypes
import time
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException
from pydantic import BaseModel, Field

from ppt_course_deal import external_settings
from ppt_course_deal.audio_duration import probe_audio_duration_seconds
from ppt_course_deal.speech_synthesis import SpeechSynthesisError, synthesize_speech


VOICES = {"zh-CN-XiaoxiaoNeural": "晓晓 · 女声", "zh-CN-YunxiNeural": "云希 · 男声", "zh-CN-XiaoyiNeural": "晓伊 · 女声"}


class SpeechBody(BaseModel):
    provider: str = "edge_tts"
    voice: str = "zh-CN-XiaoxiaoNeural"
    speed: float = Field(default=1, ge=0.5, le=1.5)


class RestoreSpeechBody(BaseModel):
    asset_id: str


class QuickPlanBody(BaseModel):
    audio_mode: str = "imported"


def speech_options() -> dict:
    cfg = external_settings.load_raw()
    return {"voices": VOICES, "default_provider": "edge_tts", "minimax_available": bool(cfg.get("minimax", {}).get("api_key"))}


def find_scene(plan: dict, scene_id: str) -> dict:
    for scene in plan.get("scenes", []):
        if scene.get("id") == scene_id:
            return scene
    raise HTTPException(404, "镜头不存在")


def validate_speech(plan: dict) -> None:
    if plan.get("audio_mode") != "segments":
        return
    for scene in plan.get("scenes", []):
        speech = scene.get("speech") or {}
        text = str(scene.get("narration") or "").strip()
        if (text and not speech) or (speech and speech.get("text") != text):
            raise HTTPException(409, f"{scene.get('title') or scene['id']}：请生成或更新配音后再导出")
        if speech and speech["asset_id"] not in scene.get("asset_ids", []):
            raise HTTPException(409, "镜头的配音素材已移除，请重新生成")
        if speech and float(scene.get("duration_sec") or 0) + 0.001 < speech["duration_sec"]:
            raise HTTPException(409, f"{scene.get('title') or scene['id']}：镜头时长短于配音，请恢复配音时长")


def attach_speech(project_id: str, plan: dict, scene: dict, speech: dict) -> None:
    from ppt_course_deal import v2_workspace as ws

    assets = {a["id"]: a for a in ws.list_assets(project_id)}
    scene["asset_ids"] = [aid for aid in scene.get("asset_ids", []) if assets.get(aid, {}).get("type") != "audio"] + [speech["asset_id"]]
    scene["speech"] = dict(speech)
    scene["speech"]["stale"] = False
    scene["narration"] = speech["text"]
    scene["subtitle"] = speech["text"]
    fps = int(plan.get("fps") or ws.DEFAULT_FPS)
    frames = max(math.ceil(speech["duration_sec"] * fps), math.ceil(0.5 * fps))
    scene["duration_frames"] = frames
    scene["duration_sec"] = round(frames / fps, 6)
    scene.pop("creative_asset", None)
    scene.pop("engine", None)
    if plan.get("primary_audio_asset_id"):
        plan["imported_audio_asset_id"] = plan["primary_audio_asset_id"]
    plan["primary_audio_asset_id"] = ""
    plan["audio_mode"] = "segments"
    plan["total_frames"] = sum(int(s.get("duration_frames") or round(s.get("duration_sec", 4) * fps)) for s in plan["scenes"])
    plan["updated_at"] = ws.now_iso()
    ws.apply_scene_routes(plan["scenes"])
    ws.write_json(ws.scene_plan_path(project_id), plan)


def generate_scene_speech(project_id: str, scene_id: str, body: SpeechBody) -> dict:
    from ppt_course_deal import v2_workspace as ws

    ws.ensure_project(project_id)
    scene = find_scene(ws.read_json(ws.scene_plan_path(project_id), {}), scene_id)
    text = str(scene.get("narration") or "").strip()
    if not text or len(text) > 500:
        raise HTTPException(400, "请填写 1 至 500 字旁白")
    if body.provider not in {"edge_tts", "minimax"}:
        raise HTTPException(400, "配音服务仅支持 Edge 或已配置的 MiniMax")
    if body.provider == "edge_tts" and body.voice not in VOICES:
        raise HTTPException(400, "请选择支持的中文声音")
    cfg = external_settings.load_raw()
    mm = dict(cfg.get("minimax") or {})
    if body.provider == "minimax" and not mm.get("api_key"):
        raise HTTPException(400, "请先在语音设置中配置 MiniMax")
    mm.update(speed=body.speed, audio_format="mp3")
    try:
        result = synthesize_speech(minimax=mm, tts={"provider": body.provider, "fallback_enabled": False, "edge_tts": {"voice": body.voice, "rate": f"{round((body.speed - 1) * 100):+d}%"}}, text=text)
    except SpeechSynthesisError as exc:
        # Provider errors may contain credentials or request details. Keep them off the UI.
        raise HTTPException(502, "配音生成失败，原有配音已保留。请检查网络或语音设置后重试。") from exc
    if result.audio_format not in {"mp3", "wav"} or not result.audio_bytes:
        raise HTTPException(502, "配音服务没有返回可播放的音频")
    aid = str(uuid4())
    path = ws.assets_dir(project_id) / aid / f"speech.{result.audio_format}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(result.audio_bytes)
    duration = probe_audio_duration_seconds(path)
    if not duration or duration > 600:
        raise HTTPException(502, "无法读取配音时长，原有配音已保留")
    speech = {"asset_id": aid, "text": text, "duration_sec": duration, "provider": result.provider, "voice": body.voice if body.provider == "edge_tts" else mm.get("voice_id", ""), "speed": body.speed, "created_at": ws.now_iso()}
    asset = {"schema_version": "asset.v1", "id": aid, "project_id": project_id, "type": "audio", "title": f"配音 · {scene.get('title') or scene_id}", "role": "scene_speech", "tags": [], "filename": path.name, "path": str(path), "mime_type": mimetypes.guess_type(path.name)[0], "size_bytes": len(result.audio_bytes), "duration_sec": duration, "created_at": ws.now_iso(), "created_at_ns": time.time_ns(), "speech": speech}
    ws.write_json(ws.asset_meta_path(project_id, aid), asset)
    ws.sync_asset_to_renderer(project_id, asset)
    with ws.project_lock(project_id):
        plan = ws.read_json(ws.scene_plan_path(project_id), {})
        current = find_scene(plan, scene_id)
        if str(current.get("narration") or "").strip() != text:
            raise HTTPException(409, "生成期间旁白已修改；本次音频保留在素材库，请按新旁白重做")
        current.setdefault("speech_versions", []).append(speech)
        attach_speech(project_id, plan, current, speech)
        return current


def restore_scene_speech(project_id: str, scene_id: str, body: RestoreSpeechBody) -> dict:
    from ppt_course_deal import v2_workspace as ws

    ws.ensure_project(project_id)
    with ws.project_lock(project_id):
        plan = ws.read_json(ws.scene_plan_path(project_id), {})
        scene = find_scene(plan, scene_id)
        speech = next((s for s in scene.get("speech_versions", []) if s["asset_id"] == body.asset_id), None)
        if not speech:
            raise HTTPException(404, "该镜头没有这个配音版本")
        asset = ws.load_asset(project_id, body.asset_id)
        if not Path(asset["path"]).is_file():
            raise HTTPException(404, "配音文件不存在")
        attach_speech(project_id, plan, scene, speech)
        return scene
