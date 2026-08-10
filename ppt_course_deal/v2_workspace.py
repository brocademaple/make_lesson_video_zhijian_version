"""V2 local video workspace for the personal AI video workbench."""

from __future__ import annotations

import json
import math
import mimetypes
import os
import re
import shlex
import shutil
import struct
import subprocess
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from ppt_course_deal.audio_duration import probe_audio_duration_seconds
from ppt_course_deal.execution_kernel import (
    ENGINE_HYBRID,
    ENGINE_HYPERFRAMES,
    ENGINE_REMOTION,
    VALID_ENGINES,
    apply_scene_routes,
    capability_by_id,
    create_run,
    discover_capabilities,
    finish_run,
    hyperframes_command,
    list_runs,
    update_run_step,
    write_hyperframes_scene,
)
from ppt_course_deal.video_project import write_video_project_props


ROOT = Path(__file__).resolve().parents[1]
SUPPORTED_ASSET_TYPES = {"text", "image", "audio", "video"}
SUPPORTED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
SUPPORTED_AUDIO_SUFFIXES = {".mp3", ".wav", ".m4a"}
DEFAULT_FPS = 30
DEFAULT_NO_AUDIO_SECONDS = 4.0
MAX_MVP_TEXT_CHARS = 300
MAX_MVP_IMAGES = 8


def workspace_root() -> Path:
    raw = (
        os.environ.get("ANY2VIDEO_WORKSPACE_ROOT")
        or os.environ.get("VIDEO_WORKSPACE_ROOT")
        or ""
    ).strip()
    return Path(raw).expanduser().resolve() if raw else (ROOT / "video_workspace").resolve()


def renderer_root() -> Path:
    raw = (
        os.environ.get("ANY2VIDEO_RENDERER_ROOT")
        or os.environ.get("VIDEO_RENDERER_ROOT")
        or ""
    ).strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return (ROOT / "ppt_course_renderer").resolve()


def public_assets_root() -> Path:
    return renderer_root() / "public" / "v2_assets"


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def read_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"JSON 损坏：{path}") from exc


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def clean_text(value: Any, limit: int = 200) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def slug_filename(filename: str, fallback: str) -> str:
    stem = Path(filename or fallback).stem or fallback
    suffix = Path(filename or "").suffix.lower()
    safe = "".join(ch if ch.isalnum() or ch in "-_." else "-" for ch in stem).strip("-._")
    return f"{safe or fallback}{suffix}"


def project_dir(project_id: str) -> Path:
    return workspace_root() / "projects" / project_id


def project_json_path(project_id: str) -> Path:
    return project_dir(project_id) / "project.json"


def ensure_project(project_id: str) -> dict[str, Any]:
    project = read_json(project_json_path(project_id), None)
    if not isinstance(project, dict):
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


def assets_dir(project_id: str) -> Path:
    return project_dir(project_id) / "assets"


def asset_meta_path(project_id: str, asset_id: str) -> Path:
    return assets_dir(project_id) / f"{asset_id}.json"


def load_asset(project_id: str, asset_id: str) -> dict[str, Any]:
    asset = read_json(asset_meta_path(project_id, asset_id), None)
    if not isinstance(asset, dict):
        raise HTTPException(status_code=404, detail="素材不存在")
    return asset


def list_assets(project_id: str) -> list[dict[str, Any]]:
    root = assets_dir(project_id)
    if not root.is_dir():
        return []
    assets = []
    for path in sorted(root.glob("*.json")):
        data = read_json(path, None)
        if isinstance(data, dict):
            assets.append(data)
    return sorted(
        assets,
        key=lambda item: (str(item.get("created_at") or ""), int(item.get("created_at_ns") or 0), str(item.get("id") or "")),
    )


def scene_plan_path(project_id: str) -> Path:
    return project_dir(project_id) / "scene_plan.json"


def render_plan_path(project_id: str) -> Path:
    return project_dir(project_id) / "render_plan.json"


def outputs_dir(project_id: str) -> Path:
    return project_dir(project_id) / "outputs"


def creative_assets_dir(project_id: str) -> Path:
    return renderer_root() / "render_tasks" / f"v2-{project_id}" / "creative_assets"


def creative_public_dir(project_id: str) -> Path:
    return renderer_root() / "public" / "v2_creative" / project_id


def output_meta_path(project_id: str, output_id: str) -> Path:
    return outputs_dir(project_id) / f"{output_id}.json"


def brief_path(project_id: str) -> Path:
    return project_dir(project_id) / "brief.json"


def video_project_path(project_id: str) -> Path:
    return project_dir(project_id) / "video_project.json"


def infer_asset_type(filename: str, content_type: str, explicit: Optional[str]) -> str:
    if explicit:
        value = explicit.strip().lower()
        if value not in SUPPORTED_ASSET_TYPES:
            raise HTTPException(status_code=400, detail="asset_type 仅支持 text / image / audio / video")
        return value
    guess = (content_type or mimetypes.guess_type(filename or "")[0] or "").lower()
    if guess.startswith("image/"):
        return "image"
    if guess.startswith("audio/"):
        return "audio"
    if guess.startswith("video/"):
        return "video"
    return "text"


def png_size(path: Path) -> Optional[tuple[int, int]]:
    with path.open("rb") as f:
        header = f.read(24)
    if header.startswith(b"\x89PNG\r\n\x1a\n") and len(header) >= 24:
        width, height = struct.unpack(">II", header[16:24])
        return int(width), int(height)
    return None


def jpeg_size(path: Path) -> Optional[tuple[int, int]]:
    with path.open("rb") as f:
        data = f.read()
    idx = 2
    while idx + 9 < len(data):
        if data[idx] != 0xFF:
            idx += 1
            continue
        marker = data[idx + 1]
        idx += 2
        if marker in {0xC0, 0xC1, 0xC2, 0xC3}:
            height, width = struct.unpack(">HH", data[idx + 3 : idx + 7])
            return int(width), int(height)
        if idx + 2 > len(data):
            break
        size = struct.unpack(">H", data[idx : idx + 2])[0]
        idx += max(2, size)
    return None


def image_size(path: Path) -> Optional[tuple[int, int]]:
    try:
        direct = png_size(path) or jpeg_size(path)
        if direct:
            return direct
        if path.suffix.lower() == ".svg":
            root = ET.parse(path).getroot()

            def svg_number(value: Any) -> Optional[float]:
                match = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)", str(value or ""))
                return float(match.group(1)) if match else None

            width = svg_number(root.attrib.get("width"))
            height = svg_number(root.attrib.get("height"))
            if width and height:
                return round(width), round(height)
            view_box = str(root.attrib.get("viewBox") or "").replace(",", " ").split()
            if len(view_box) == 4:
                return round(float(view_box[2])), round(float(view_box[3]))
            return None
        from PIL import Image

        with Image.open(path) as image:
            return int(image.width), int(image.height)
    except Exception:
        return None


def summary_for_text(text: str) -> str:
    text = " ".join(text.split())
    if not text:
        return "空文本素材"
    return clean_text(text, 80)


async def read_upload(upload: Optional[UploadFile], max_bytes: int) -> bytes:
    if upload is None:
        return b""
    out = bytearray()
    while True:
        chunk = await upload.read(1024 * 1024)
        if not chunk:
            break
        if len(out) + len(chunk) > max_bytes:
            raise HTTPException(status_code=400, detail="文件过大")
        out.extend(chunk)
    return bytes(out)


def project_summary(project: dict[str, Any]) -> dict[str, Any]:
    project_id = str(project["id"])
    assets = list_assets(project_id)
    scene_plan = read_json(scene_plan_path(project_id), {})
    scenes = scene_plan.get("scenes") if isinstance(scene_plan, dict) else []
    outputs = list_outputs(project_id)
    return {
        **project,
        "asset_count": len(assets),
        "scene_count": len(scenes) if isinstance(scenes, list) else 0,
        "output_count": len(outputs),
    }


def list_projects() -> list[dict[str, Any]]:
    root = workspace_root() / "projects"
    if not root.is_dir():
        return []
    projects = []
    for path in sorted(root.glob("*/project.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        data = read_json(path, None)
        if isinstance(data, dict):
            projects.append(project_summary(data))
    return projects


def detail_project(project_id: str) -> dict[str, Any]:
    project = ensure_project(project_id)
    scene_plan = read_json(scene_plan_path(project_id), {"scenes": []})
    if isinstance(scene_plan, dict) and isinstance(scene_plan.get("scenes"), list):
        apply_scene_routes(scene_plan["scenes"])
    return {
        **project_summary(project),
        "assets": list_assets(project_id),
        "brief": read_json(brief_path(project_id), {}),
        "scene_plan": scene_plan,
        "render_plan": read_json(render_plan_path(project_id), {}),
        "outputs": list_outputs(project_id),
        "runs": list_runs(project_dir(project_id), limit=12),
    }


class ProjectCreateBody(BaseModel):
    title: str = Field(default="未命名视频")
    aspect_ratio: str = Field(default="9:16")
    platform: str = Field(default="小红书 / 抖音")
    style: str = Field(default="clean")
    target_duration_sec: float = Field(default=30, ge=3, le=60 * 30)
    goal: str = Field(default="")


class BriefBody(BaseModel):
    goal: str = ""
    platform: str = ""
    aspect_ratio: str = ""
    target_duration_sec: Optional[float] = Field(default=None, ge=3, le=60 * 30)
    style: str = ""
    audience: str = ""
    notes: str = ""


class SceneUpdateBody(BaseModel):
    title: Optional[str] = None
    purpose: Optional[str] = None
    asset_ids: Optional[list[str]] = None
    onscreen_text: Optional[str] = None
    narration: Optional[str] = None
    subtitle: Optional[str] = None
    duration_sec: Optional[float] = Field(default=None, ge=0.5, le=60 * 10)
    renderer: Optional[str] = None
    template: Optional[str] = None
    status: Optional[str] = None


class SceneCreateBody(SceneUpdateBody):
    after_scene_id: Optional[str] = None


class SceneOrderBody(BaseModel):
    scene_ids: list[str]


class PrepareScenesBody(BaseModel):
    execute: bool = True
    allow_on_demand: bool = False
    timeout_sec: int = Field(default=180, ge=5, le=60 * 20)


class RenderPlanBody(BaseModel):
    fps: int = Field(default=DEFAULT_FPS, ge=12, le=60)
    no_audio_seconds: float = Field(default=DEFAULT_NO_AUDIO_SECONDS, ge=0.5, le=30)


class RenderBody(BaseModel):
    execute: bool = True
    timeout_sec: int = Field(default=180, ge=5, le=60 * 30)


def create_project(body: ProjectCreateBody) -> dict[str, Any]:
    project_id = str(uuid4())
    now = now_iso()
    project = {
        "schema_version": "video_workbench_project.v2",
        "id": project_id,
        "title": clean_text(body.title, 120) or "未命名视频",
        "goal": clean_text(body.goal, 500),
        "aspect_ratio": body.aspect_ratio,
        "platform": body.platform,
        "style": body.style,
        "target_duration_sec": body.target_duration_sec,
        "status": "draft",
        "created_at": now,
        "updated_at": now,
    }
    write_json(project_json_path(project_id), project)
    write_json(scene_plan_path(project_id), {"schema_version": "scene_plan.v1", "scenes": []})
    write_json(outputs_dir(project_id) / ".keep.json", {"created_at": now})
    return detail_project(project_id)


def save_project(project: dict[str, Any]) -> None:
    project["updated_at"] = now_iso()
    write_json(project_json_path(str(project["id"])), project)


def asset_relative_for_renderer(project_id: str, asset: dict[str, Any]) -> str:
    rel = asset.get("renderer_relative")
    return str(rel or "")


def sync_asset_to_renderer(project_id: str, asset: dict[str, Any]) -> str:
    if not asset.get("path"):
        return ""
    src = Path(str(asset["path"]))
    if not src.is_file():
        return ""
    dst = public_assets_root() / project_id / str(asset["id"]) / src.name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    rel = dst.relative_to(renderer_root() / "public").as_posix()
    asset["renderer_relative"] = rel
    write_json(asset_meta_path(project_id, str(asset["id"])), asset)
    return rel


async def add_asset(
    project_id: str,
    *,
    upload: Optional[UploadFile],
    content: str,
    asset_type: Optional[str],
    title: str,
    role: str,
    tags: str,
    max_bytes: int,
) -> dict[str, Any]:
    project = ensure_project(project_id)
    raw = await read_upload(upload, max_bytes)
    filename = upload.filename if upload else ""
    inferred = infer_asset_type(filename, upload.content_type if upload else "text/plain", asset_type)
    suffix = Path(filename or "").suffix.lower()
    if inferred == "image" and suffix not in SUPPORTED_IMAGE_SUFFIXES:
        raise HTTPException(status_code=400, detail="图片仅支持 PNG、JPEG、WebP 或 SVG")
    if inferred == "audio" and suffix not in SUPPORTED_AUDIO_SUFFIXES:
        raise HTTPException(status_code=400, detail="旁白音频仅支持 MP3、WAV 或 M4A")
    if inferred == "text" and not raw and not content.strip():
        raise HTTPException(status_code=400, detail="文本素材不能为空")
    asset_id = str(uuid4())
    root = assets_dir(project_id) / asset_id
    root.mkdir(parents=True, exist_ok=True)
    path = root / slug_filename(filename, f"{asset_id}.txt")
    text_content = content
    if inferred == "text":
        if raw:
            text_content = raw.decode("utf-8", errors="replace")
        if len(text_content.strip()) > MAX_MVP_TEXT_CHARS:
            raise HTTPException(status_code=400, detail=f"MVP 文本最多 {MAX_MVP_TEXT_CHARS} 字")
        path = root / "content.txt"
        path.write_text(text_content, encoding="utf-8")
    else:
        if not raw:
            raise HTTPException(status_code=400, detail="文件素材不能为空")
        path.write_bytes(raw)
    meta: dict[str, Any] = {
        "schema_version": "asset.v1",
        "id": asset_id,
        "project_id": project_id,
        "type": inferred,
        "title": clean_text(title or filename or f"{inferred} asset", 120),
        "role": clean_text(role or inferred, 80),
        "tags": [clean_text(tag, 40) for tag in tags.split(",") if tag.strip()],
        "filename": filename or path.name,
        "path": str(path),
        "mime_type": upload.content_type if upload else "text/plain",
        "size_bytes": path.stat().st_size,
        "created_at": now_iso(),
        "created_at_ns": time.time_ns(),
        "summary": "",
    }
    if inferred == "text":
        meta["content"] = text_content
        meta["char_count"] = len(text_content)
        meta["summary"] = summary_for_text(text_content)
    elif inferred == "image":
        size = image_size(path)
        if size:
            meta["width"], meta["height"] = size
        meta["summary"] = clean_text(title or filename or "图片素材", 80)
        sync_asset_to_renderer(project_id, meta)
    elif inferred == "audio":
        try:
            meta["duration_sec"] = probe_audio_duration_seconds(path)
        except Exception:
            meta["duration_sec"] = None
        meta["summary"] = clean_text(title or filename or "音频素材", 80)
        sync_asset_to_renderer(project_id, meta)
    else:
        meta["summary"] = clean_text(title or filename or "视频素材（预留）", 80)
    write_json(asset_meta_path(project_id, asset_id), meta)
    project["status"] = "materials_ready"
    save_project(project)
    return meta


def save_brief(project_id: str, body: BriefBody) -> dict[str, Any]:
    project = ensure_project(project_id)
    brief = {
        "schema_version": "creative_brief.v1",
        "goal": body.goal or project.get("goal") or "",
        "platform": body.platform or project.get("platform") or "",
        "aspect_ratio": body.aspect_ratio or project.get("aspect_ratio") or "9:16",
        "target_duration_sec": body.target_duration_sec or project.get("target_duration_sec") or 30,
        "style": body.style or project.get("style") or "clean",
        "audience": body.audience,
        "notes": body.notes,
        "updated_at": now_iso(),
    }
    write_json(brief_path(project_id), brief)
    project.update(
        {
            "goal": brief["goal"],
            "platform": brief["platform"],
            "aspect_ratio": brief["aspect_ratio"],
            "style": brief["style"],
            "target_duration_sec": brief["target_duration_sec"],
            "status": "brief_ready",
        }
    )
    save_project(project)
    return brief


def _asset_groups(assets: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups = {kind: [] for kind in SUPPORTED_ASSET_TYPES}
    for asset in assets:
        groups.setdefault(str(asset.get("type") or "text"), []).append(asset)
    return groups


def _scene_text_from(asset: Optional[dict[str, Any]], fallback: str) -> str:
    if not asset:
        return fallback
    if asset.get("type") == "text":
        return clean_text(asset.get("content") or asset.get("summary") or fallback, 160)
    return clean_text(asset.get("summary") or asset.get("title") or fallback, 160)


def _latest_asset(items: list[dict[str, Any]]) -> Optional[dict[str, Any]]:
    return items[-1] if items else None


def _split_copy_for_images(text: str, image_count: int) -> tuple[list[str], list[str]]:
    normalized = text.strip()
    chunks = [part.strip() for part in re.split(r"(?:\r?\n)+|(?<=[。！？!?])\s*", normalized) if part.strip()]
    chunks = chunks or [normalized]
    if len(chunks) > image_count:
        grouped: list[str] = []
        for index in range(image_count):
            start = math.floor(index * len(chunks) / image_count)
            end = math.floor((index + 1) * len(chunks) / image_count)
            grouped.append("".join(chunks[start:end]))
        chunks = grouped
    elif len(chunks) < image_count:
        chunks = [chunks[index % len(chunks)] for index in range(image_count)]

    warnings = []
    result = []
    for index, chunk in enumerate(chunks[:image_count]):
        shortened = clean_text(chunk, 90)
        if shortened != " ".join(chunk.split()):
            warnings.append(f"第 {index + 1} 段屏幕文字已截断")
        result.append(shortened)
    return result, warnings


def build_quick_scene_plan(project_id: str, fps: int = DEFAULT_FPS) -> dict[str, Any]:
    project = ensure_project(project_id)
    groups = _asset_groups(list_assets(project_id))
    text_asset = _latest_asset(groups.get("text", []))
    images = groups.get("image", [])
    audio_asset = _latest_asset(groups.get("audio", []))

    missing = []
    if not text_asset:
        missing.append("文字")
    if not images:
        missing.append("图片")
    if not audio_asset:
        missing.append("旁白音频")
    if missing:
        raise HTTPException(status_code=400, detail="缺少必需素材：" + "、".join(missing))
    if len(images) > MAX_MVP_IMAGES:
        raise HTTPException(status_code=400, detail=f"MVP 最多支持 {MAX_MVP_IMAGES} 张图片")

    content = str(text_asset.get("content") or "").strip()
    if not content:
        raise HTTPException(status_code=400, detail="文字素材不能为空")
    if len(content) > MAX_MVP_TEXT_CHARS:
        raise HTTPException(status_code=400, detail=f"MVP 文本最多 {MAX_MVP_TEXT_CHARS} 字")
    duration = audio_asset.get("duration_sec")
    if not isinstance(duration, (int, float)) or duration <= 0:
        raise HTTPException(status_code=400, detail="无法解析旁白音频时长，请上传有效的 MP3、WAV 或 M4A")

    total_frames = max(1, round(float(duration) * fps))
    base_frames, remainder = divmod(total_frames, len(images))
    if base_frames < 1:
        raise HTTPException(status_code=400, detail="旁白音频过短，无法分配给当前图片")
    copy_segments, warnings = _split_copy_for_images(content, len(images))
    scenes = []
    assigned_frames = 0
    for index, image in enumerate(images):
        frames = base_frames + (remainder if index == len(images) - 1 else 0)
        assigned_frames += frames
        copy = copy_segments[index]
        scenes.append(
            {
                "id": f"scene-{index + 1:03d}",
                "title": clean_text(copy, 42),
                "purpose": "自动图文口播",
                "asset_ids": [text_asset["id"], image["id"]],
                "onscreen_text": copy,
                "narration": copy,
                "subtitle": copy,
                "duration_frames": frames,
                "duration_sec": round(frames / fps, 6),
                "renderer": "auto",
                "template": "image_narration",
                "status": "approved",
            }
        )
    apply_scene_routes(scenes)
    plan = {
        "schema_version": "scene_plan.v2",
        "project_id": project_id,
        "generated_by": "quick_compose_v1",
        "primary_text_asset_id": text_asset["id"],
        "primary_audio_asset_id": audio_asset["id"],
        "audio_duration_sec": round(float(duration), 6),
        "fps": fps,
        "total_frames": assigned_frames,
        "warnings": warnings,
        "created_at": now_iso(),
        "scenes": scenes,
    }
    write_json(scene_plan_path(project_id), plan)
    project["status"] = "scene_plan_ready"
    save_project(project)
    return plan


def build_scene_plan(project_id: str) -> dict[str, Any]:
    project = ensure_project(project_id)
    brief = read_json(brief_path(project_id), {})
    assets = list_assets(project_id)
    groups = _asset_groups(assets)
    texts = groups.get("text", [])
    images = groups.get("image", [])
    audios = groups.get("audio", [])
    target = float((brief or {}).get("target_duration_sec") or project.get("target_duration_sec") or 24)
    scene_count = max(1, min(5, len(texts) or len(images) or 3))
    per_scene = max(3.0, round(target / scene_count, 2))
    scenes = []
    for idx in range(scene_count):
        text_asset = texts[idx % len(texts)] if texts else None
        image_asset = images[idx % len(images)] if images else None
        audio_asset = audios[idx % len(audios)] if audios else None
        asset_ids = [a["id"] for a in [text_asset, image_asset, audio_asset] if a]
        seed = _scene_text_from(text_asset or image_asset, f"镜头 {idx + 1}")
        renderer = "auto"
        scenes.append(
            {
                "id": f"scene-{idx + 1:03d}",
                "title": clean_text(seed, 42),
                "purpose": "开场抓注意力" if idx == 0 else "展开核心信息",
                "asset_ids": asset_ids,
                "onscreen_text": clean_text(seed, 80),
                "narration": clean_text(seed, 180),
                "subtitle": clean_text(seed, 120),
                "duration_sec": per_scene,
                "renderer": renderer,
                "template": "kinetic_title_card" if renderer == "hyperframes" else "image_narration",
                "status": "draft",
            }
        )
    apply_scene_routes(scenes)
    plan = {
        "schema_version": "scene_plan.v2",
        "project_id": project_id,
        "generated_by": "heuristic_v1",
        "created_at": now_iso(),
        "scenes": scenes,
    }
    write_json(scene_plan_path(project_id), plan)
    project["status"] = "scene_plan_ready"
    save_project(project)
    return plan


def update_scene(project_id: str, scene_id: str, body: SceneUpdateBody) -> dict[str, Any]:
    project = ensure_project(project_id)
    plan = read_json(scene_plan_path(project_id), {"schema_version": "scene_plan.v1", "scenes": []})
    scenes = plan.get("scenes")
    if not isinstance(scenes, list):
        scenes = []
    scene = None
    for item in scenes:
        if isinstance(item, dict) and item.get("id") == scene_id:
            scene = item
            break
    if scene is None:
        scene = {
            "id": scene_id,
            "title": "新镜头",
            "purpose": "",
            "asset_ids": [],
            "onscreen_text": "",
            "narration": "",
            "subtitle": "",
            "duration_sec": 4,
            "renderer": "auto",
            "template": "image_narration",
            "status": "draft",
        }
        scenes.append(scene)
    updates = body.model_dump(exclude_unset=True)
    requested_renderer = updates.get("renderer")
    if requested_renderer is not None and str(requested_renderer).strip().lower() not in VALID_ENGINES:
        raise HTTPException(status_code=400, detail="renderer 仅支持 auto / remotion / hyperframes / hybrid")
    for key, value in updates.items():
        if value is not None:
            scene[key] = value
    if "duration_sec" in updates and updates["duration_sec"] is not None:
        fps = int(plan.get("fps") or DEFAULT_FPS)
        scene["duration_frames"] = max(1, round(float(scene["duration_sec"]) * fps))
    if set(updates).intersection({"title", "purpose", "asset_ids", "onscreen_text", "duration_sec", "renderer", "template"}):
        scene.pop("creative_asset", None)
        scene.pop("engine", None)
    apply_scene_routes(scenes)
    plan["schema_version"] = "scene_plan.v2"
    plan["scenes"] = scenes
    plan["updated_at"] = now_iso()
    write_json(scene_plan_path(project_id), plan)
    project["status"] = "scene_plan_ready"
    save_project(project)
    return scene


def _new_scene_id(existing: list[dict[str, Any]]) -> str:
    used = {str(item.get("id") or "") for item in existing}
    while True:
        candidate = f"scene-{uuid4().hex[:8]}"
        if candidate not in used:
            return candidate


def _default_scene(project_id: str, scenes: list[dict[str, Any]]) -> dict[str, Any]:
    groups = _asset_groups(list_assets(project_id))
    image = _latest_asset(groups.get("image", []))
    text = _latest_asset(groups.get("text", []))
    asset_ids = [item["id"] for item in (text, image) if item]
    title = f"镜头 {len(scenes) + 1}"
    return {
        "id": _new_scene_id(scenes),
        "title": title,
        "purpose": "补充画面",
        "asset_ids": asset_ids,
        "onscreen_text": title,
        "narration": "",
        "subtitle": "",
        "duration_sec": DEFAULT_NO_AUDIO_SECONDS,
        "renderer": "auto",
        "template": "image_narration",
        "status": "draft",
    }


def create_scene(project_id: str, body: SceneCreateBody) -> dict[str, Any]:
    project = ensure_project(project_id)
    plan = read_json(scene_plan_path(project_id), {"schema_version": "scene_plan.v2", "scenes": []})
    scenes = plan.get("scenes") if isinstance(plan, dict) else []
    if not isinstance(scenes, list):
        scenes = []
    scene = _default_scene(project_id, scenes)
    updates = body.model_dump(exclude_unset=True, exclude={"after_scene_id"})
    for key, value in updates.items():
        if value is not None:
            scene[key] = value
    insert_at = len(scenes)
    if body.after_scene_id:
        for index, item in enumerate(scenes):
            if isinstance(item, dict) and item.get("id") == body.after_scene_id:
                insert_at = index + 1
                break
    scenes.insert(insert_at, scene)
    apply_scene_routes(scenes)
    plan["schema_version"] = "scene_plan.v2"
    plan["scenes"] = scenes
    plan["updated_at"] = now_iso()
    write_json(scene_plan_path(project_id), plan)
    project["status"] = "scene_plan_ready"
    save_project(project)
    return scene


def duplicate_scene(project_id: str, scene_id: str) -> dict[str, Any]:
    project = ensure_project(project_id)
    plan = read_json(scene_plan_path(project_id), {"schema_version": "scene_plan.v2", "scenes": []})
    scenes = plan.get("scenes") if isinstance(plan, dict) else []
    if not isinstance(scenes, list):
        scenes = []
    for index, item in enumerate(scenes):
        if isinstance(item, dict) and item.get("id") == scene_id:
            duplicate = dict(item)
            duplicate["id"] = _new_scene_id(scenes)
            duplicate["title"] = clean_text(f"{item.get('title') or '镜头'} 副本", 80)
            duplicate["status"] = "draft"
            duplicate.pop("creative_asset", None)
            duplicate.pop("engine", None)
            scenes.insert(index + 1, duplicate)
            apply_scene_routes(scenes)
            plan["schema_version"] = "scene_plan.v2"
            plan["scenes"] = scenes
            plan["updated_at"] = now_iso()
            write_json(scene_plan_path(project_id), plan)
            project["status"] = "scene_plan_ready"
            save_project(project)
            return duplicate
    raise HTTPException(status_code=404, detail="镜头不存在")


def delete_scene(project_id: str, scene_id: str) -> dict[str, Any]:
    project = ensure_project(project_id)
    plan = read_json(scene_plan_path(project_id), {"schema_version": "scene_plan.v2", "scenes": []})
    scenes = plan.get("scenes") if isinstance(plan, dict) else []
    if not isinstance(scenes, list):
        scenes = []
    remaining = [item for item in scenes if not isinstance(item, dict) or item.get("id") != scene_id]
    if len(remaining) == len(scenes):
        raise HTTPException(status_code=404, detail="镜头不存在")
    plan["schema_version"] = "scene_plan.v2"
    apply_scene_routes(remaining)
    plan["scenes"] = remaining
    plan["updated_at"] = now_iso()
    write_json(scene_plan_path(project_id), plan)
    project["status"] = "scene_plan_ready" if remaining else "materials_ready"
    save_project(project)
    return {"deleted_scene_id": scene_id, "scene_count": len(remaining)}


def reorder_scenes(project_id: str, body: SceneOrderBody) -> list[dict[str, Any]]:
    project = ensure_project(project_id)
    plan = read_json(scene_plan_path(project_id), {"schema_version": "scene_plan.v2", "scenes": []})
    scenes = plan.get("scenes") if isinstance(plan, dict) else []
    if not isinstance(scenes, list):
        scenes = []
    if len(body.scene_ids) != len(set(body.scene_ids)):
        raise HTTPException(status_code=400, detail="镜头顺序包含重复 ID")
    by_id = {str(item.get("id") or ""): item for item in scenes if isinstance(item, dict)}
    if set(body.scene_ids) != set(by_id):
        raise HTTPException(status_code=400, detail="镜头顺序必须包含全部且仅包含现有镜头")
    ordered = [by_id[scene_id] for scene_id in body.scene_ids]
    plan["schema_version"] = "scene_plan.v2"
    apply_scene_routes(ordered)
    plan["scenes"] = ordered
    plan["updated_at"] = now_iso()
    write_json(scene_plan_path(project_id), plan)
    project["status"] = "scene_plan_ready"
    save_project(project)
    return ordered


def prepare_creative_assets(
    project_id: str,
    body: PrepareScenesBody,
    *,
    scene_ids: Optional[list[str]] = None,
    run: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    project = ensure_project(project_id)
    plan = read_json(scene_plan_path(project_id), {"schema_version": "scene_plan.v2", "scenes": []})
    scenes = plan.get("scenes") if isinstance(plan, dict) else []
    if not isinstance(scenes, list) or not scenes:
        raise HTTPException(status_code=400, detail="请先生成镜头")
    apply_scene_routes(scenes)
    selected = {
        str(scene.get("id") or "")
        for scene in scenes
        if isinstance(scene, dict)
        and (not scene_ids or str(scene.get("id") or "") in scene_ids)
        and str((scene.get("engine") or {}).get("resolved") or "")
        in {ENGINE_HYPERFRAMES, ENGINE_HYBRID}
    }
    own_run = run is None
    if run is None:
        run = create_run(
            project_dir(project_id),
            project_id,
            "prepare_creative_scenes",
            ["route:scenes", *[f"creative:{scene_id}" for scene_id in sorted(selected)]],
            {"execute": body.execute, "allow_on_demand": body.allow_on_demand},
        )
    update_run_step(
        project_dir(project_id),
        run,
        "route:scenes",
        "ready",
        detail=f"已解析 {len(scenes)} 个镜头，其中 {len(selected)} 个需要创意执行器",
    )
    registry = discover_capabilities(renderer_root(), workspace_root())
    capability = capability_by_id(registry, "hyperframes.render_scene")
    command = hyperframes_command(registry, allow_on_demand=body.allow_on_demand)
    assets = {asset["id"]: asset for asset in list_assets(project_id)}
    width, height = (1920, 1080) if str(project.get("aspect_ratio") or "") == "16:9" else (1080, 1920)
    tasks: list[dict[str, Any]] = []
    for scene in scenes:
        if not isinstance(scene, dict) or str(scene.get("id") or "") not in selected:
            continue
        scene_id = str(scene["id"])
        step_id = f"creative:{scene_id}"
        update_run_step(project_dir(project_id), run, step_id, "running", detail="正在准备 HyperFrames 场景")
        image = _scene_primary_asset(scene, assets, "image")
        image_path = Path(str(image.get("path") or "")) if image else None
        target_dir = creative_assets_dir(project_id) / scene_id
        try:
            manifest = write_hyperframes_scene(
                target_dir,
                project,
                scene,
                image_path,
                width=width,
                height=height,
                fps=int(plan.get("fps") or DEFAULT_FPS),
            )
            task = {
                "scene_id": scene_id,
                "requested": (scene.get("engine") or {}).get("requested"),
                "resolved": (scene.get("engine") or {}).get("resolved"),
                "status": "prepared",
                "source_html": manifest["source_html"],
                "clip_path": manifest["clip_path"],
                "capability_status": capability.get("status") or "unavailable",
            }
            engine = scene.get("engine") if isinstance(scene.get("engine"), dict) else {}
            engine["last_run_id"] = run["id"]
            engine["artifact"] = manifest
            existing_creative = scene.get("creative_asset") if isinstance(scene.get("creative_asset"), dict) else {}
            existing_clip = Path(str(existing_creative.get("path") or "")) if existing_creative else None
            if existing_clip and existing_clip.is_file() and existing_clip.stat().st_size > 0:
                engine["status"] = "ready"
                engine["error"] = ""
                task["status"] = "ready"
                task["reused"] = True
                task["clip_relative"] = existing_creative.get("relative")
                update_run_step(
                    project_dir(project_id),
                    run,
                    step_id,
                    "ready",
                    detail="复用已生成的 HyperFrames 创意镜头",
                    artifact={"kind": "hyperframes_clip", "path": str(existing_clip), "scene_id": scene_id, "reused": True},
                )
            elif not body.execute:
                engine["status"] = "prepared"
                update_run_step(
                    project_dir(project_id),
                    run,
                    step_id,
                    "ready",
                    detail="创意源码与 brief 已准备，尚未执行 HyperFrames",
                    artifact={"kind": "hyperframes_source", "path": manifest["source_html"], "scene_id": scene_id},
                )
            elif not command:
                engine["status"] = "fallback"
                engine["error"] = "HyperFrames CLI 未就绪"
                task["status"] = "fallback"
                task["fallback"] = ENGINE_REMOTION
                update_run_step(
                    project_dir(project_id),
                    run,
                    step_id,
                    "fallback",
                    detail="HyperFrames CLI 未就绪，最终成片使用 Remotion fallback",
                    artifact={"kind": "hyperframes_source", "path": manifest["source_html"], "scene_id": scene_id},
                )
            else:
                clip_path = Path(manifest["clip_path"])
                process_env = os.environ.copy()
                system_chrome = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
                if "HYPERFRAMES_BROWSER_PATH" not in process_env and system_chrome.is_file():
                    process_env["HYPERFRAMES_BROWSER_PATH"] = str(system_chrome)
                result = subprocess.run(
                    [*command, "render", "--output", str(clip_path), "--quality", "draft"],
                    cwd=target_dir,
                    env=process_env,
                    capture_output=True,
                    text=True,
                    timeout=body.timeout_sec,
                    check=False,
                )
                if result.returncode == 0 and clip_path.is_file() and clip_path.stat().st_size > 0:
                    public_dir = creative_public_dir(project_id) / scene_id
                    public_dir.mkdir(parents=True, exist_ok=True)
                    public_clip = public_dir / "clip.mp4"
                    shutil.copy2(clip_path, public_clip)
                    relative = public_clip.relative_to(renderer_root() / "public").as_posix()
                    creative_asset = {
                        "id": f"creative-{scene_id}",
                        "type": "recording",
                        "relative": relative,
                        "path": str(public_clip),
                        "label": f"HyperFrames · {scene.get('title') or scene_id}",
                        "exists": True,
                    }
                    scene["creative_asset"] = creative_asset
                    engine["status"] = "ready"
                    engine["error"] = ""
                    engine["artifact"] = {**manifest, "clip_relative": relative}
                    task["status"] = "ready"
                    task["clip_relative"] = relative
                    update_run_step(
                        project_dir(project_id),
                        run,
                        step_id,
                        "ready",
                        detail="HyperFrames 创意镜头已生成",
                        artifact={"kind": "hyperframes_clip", "path": str(public_clip), "scene_id": scene_id},
                    )
                else:
                    error = clean_text((result.stderr or result.stdout or "HyperFrames 执行失败")[-1600:], 1600)
                    engine["status"] = "fallback"
                    engine["error"] = error
                    task["status"] = "fallback"
                    task["fallback"] = ENGINE_REMOTION
                    task["error"] = error
                    update_run_step(
                        project_dir(project_id),
                        run,
                        step_id,
                        "fallback",
                        detail="HyperFrames 执行失败，最终成片使用 Remotion fallback",
                    )
            scene["engine"] = engine
            tasks.append(task)
        except (OSError, subprocess.SubprocessError) as exc:
            engine = scene.get("engine") if isinstance(scene.get("engine"), dict) else {}
            engine["status"] = "fallback"
            engine["error"] = str(exc)
            engine["last_run_id"] = run["id"]
            scene["engine"] = engine
            tasks.append({"scene_id": scene_id, "status": "fallback", "fallback": ENGINE_REMOTION, "error": str(exc)})
            update_run_step(
                project_dir(project_id),
                run,
                step_id,
                "fallback",
                detail=f"创意执行异常，使用 Remotion fallback：{exc}",
            )
    plan["schema_version"] = "scene_plan.v2"
    plan["scenes"] = scenes
    plan["routing_updated_at"] = now_iso()
    write_json(scene_plan_path(project_id), plan)
    if own_run:
        finish_run(project_dir(project_id), run, "ready")
    return {"tasks": tasks, "run": run, "capabilities": registry, "scene_plan": plan}


def aspect_format(aspect_ratio: str) -> str:
    key = (aspect_ratio or "").replace(" ", "")
    if key in {"16:9", "horizontal", "landscape"}:
        return "horizontal_1920x1080"
    if key in {"1:1", "square"}:
        return "square_1080"
    return "vertical_1080x1920"


def _scene_primary_asset(
    scene: dict[str, Any], assets: dict[str, dict[str, Any]], kind: str
) -> Optional[dict[str, Any]]:
    for asset_id in scene.get("asset_ids") or []:
        asset = assets.get(str(asset_id))
        if asset and asset.get("type") == kind:
            return asset
    return None


def build_video_project(project_id: str, fps: int, no_audio_seconds: float) -> dict[str, Any]:
    project = ensure_project(project_id)
    plan = read_json(scene_plan_path(project_id), {"scenes": []})
    scenes = plan.get("scenes") if isinstance(plan, dict) else []
    if not isinstance(scenes, list) or not scenes:
        raise HTTPException(status_code=400, detail="请先生成或创建 Scene")
    apply_scene_routes(scenes)
    assets = {asset["id"]: asset for asset in list_assets(project_id)}
    materials = []
    converted_scenes = []
    for asset in assets.values():
        if asset.get("type") not in {"image", "audio"}:
            continue
        rel = sync_asset_to_renderer(project_id, asset)
        if rel:
            materials.append(
                {
                    "id": asset["id"],
                    "type": "image" if asset.get("type") == "image" else "audio",
                    "relative": rel,
                    "label": asset.get("title") or asset["id"],
                    "alt": asset.get("summary") or asset.get("title") or "",
                }
            )
    warnings = list(plan.get("warnings") or []) if isinstance(plan, dict) else []
    for idx, raw in enumerate(scenes):
        if not isinstance(raw, dict):
            continue
        image = _scene_primary_asset(raw, assets, "image")
        audio = _scene_primary_asset(raw, assets, "audio")
        engine = raw.get("engine") if isinstance(raw.get("engine"), dict) else {}
        creative = raw.get("creative_asset") if isinstance(raw.get("creative_asset"), dict) else {}
        creative_id = ""
        if creative.get("exists") and creative.get("relative"):
            creative_id = str(creative.get("id") or f"creative-{raw.get('id') or idx + 1}")
            materials.append(
                {
                    "id": creative_id,
                    "type": "recording",
                    "relative": str(creative["relative"]),
                    "label": str(creative.get("label") or "HyperFrames 创意镜头"),
                    "alt": str(raw.get("onscreen_text") or raw.get("title") or ""),
                }
            )
        duration = raw.get("duration_sec")
        if not isinstance(duration, (int, float)) or duration <= 0:
            duration = audio.get("duration_sec") if audio else no_audio_seconds
        if not audio:
            warnings.append(f"{raw.get('id') or idx + 1} 缺少音频，使用占位时长")
        converted_scenes.append(
            {
                "id": raw.get("id") or f"scene-{idx + 1:03d}",
                "title": raw.get("title") or f"Scene {idx + 1}",
                "asset_id": image.get("id") if image else "",
                "audio_asset_id": audio.get("id") if audio else "",
                "creative_asset_id": creative_id,
                "renderer_requested": engine.get("requested") or raw.get("renderer") or "auto",
                "renderer_resolved": engine.get("resolved") or ENGINE_REMOTION,
                "renderer_status": engine.get("status") or "ready",
                "renderer_reason": engine.get("reason") or "",
                "duration_frames": raw.get("duration_frames"),
                "duration_sec": float(duration or no_audio_seconds),
                "shot_type": "hero" if engine.get("resolved") == ENGINE_HYPERFRAMES else "screen_focus",
                "onscreen_text": raw.get("onscreen_text") or raw.get("subtitle") or raw.get("title") or "",
                "narration": raw.get("narration") or raw.get("subtitle") or "",
                "renderer": engine.get("resolved") or ENGINE_REMOTION,
                "template": raw.get("template") or "image_narration",
                "callouts": [{"label": raw.get("purpose") or "镜头目的"}] if raw.get("purpose") else [],
                "creative_asset_needed": engine.get("resolved") in {ENGINE_HYPERFRAMES, ENGINE_HYBRID},
            }
        )
        if engine.get("status") == "fallback":
            warnings.append(f"{raw.get('id') or idx + 1} 的 HyperFrames 创意镜头未就绪，使用 Remotion fallback")
    video_project = {
        "schema_version": "video_project.v2",
        "title": project.get("title") or "未命名视频",
        "intent": "personal_ai_video",
        "format": aspect_format(str(project.get("aspect_ratio") or "9:16")),
        "materials": materials,
        "primary_audio_asset_id": plan.get("primary_audio_asset_id") if isinstance(plan, dict) else "",
        "scenes": converted_scenes,
        "variants": [
            {
                "id": "primary",
                "title": project.get("title") or "未命名视频",
                "scene_ids": [scene["id"] for scene in converted_scenes],
                "template_package": "ProductExperience",
                "pace": "balanced",
            }
        ],
        "render_notes": {
            "fps": fps,
            "warnings": warnings,
            "hyperframes_policy": "Creative scenes use prepared HyperFrames clips when ready and fall back to Remotion safely.",
        },
    }
    write_json(video_project_path(project_id), video_project)
    return video_project


def build_render_plan(
    project_id: str,
    body: RenderPlanBody,
    *,
    output_video_path: Optional[Path] = None,
) -> dict[str, Any]:
    video_project = build_video_project(project_id, body.fps, body.no_audio_seconds)
    task_dir = renderer_root() / "render_tasks" / f"v2-{project_id}"
    input_props_path = task_dir / "input-props.json"
    output_video_path = output_video_path or (task_dir / "out" / "preview-video.mp4")
    props = write_video_project_props(
        video_project_path(project_id),
        input_props_path,
        variant_id="primary",
        fps=body.fps,
        workspace_root=ROOT,
    )
    command = [
        "npx",
        "remotion",
        "render",
        "src/index.ts",
        "ProductExperienceVideo",
        str(output_video_path),
        "--props",
        str(input_props_path),
    ]
    render_command = f"cd {shlex.quote(str(renderer_root()))} && {shlex.join(command)}"
    total_frames = sum(int(scene.get("durationInFrames") or 0) for scene in props.get("scenes", []))
    render_plan = {
        "schema_version": "render_plan.v2",
        "project_id": project_id,
        "source": "video_project.v2",
        "video_project_path": str(video_project_path(project_id)),
        "input_props_path": str(input_props_path),
        "output_video_path": str(output_video_path),
        "render_command": render_command,
        "fps": body.fps,
        "total_frames": total_frames,
        "duration_sec": round(total_frames / body.fps, 3) if body.fps else 0,
        "warnings": video_project.get("render_notes", {}).get("warnings", []),
        "props": props,
        "created_at": now_iso(),
    }
    write_json(render_plan_path(project_id), render_plan)
    return render_plan


def list_outputs(project_id: str) -> list[dict[str, Any]]:
    root = outputs_dir(project_id)
    if not root.is_dir():
        return []
    outputs = []
    for path in sorted(root.glob("*.json")):
        if path.name == ".keep.json":
            continue
        data = read_json(path, None)
        if isinstance(data, dict):
            if data.get("id"):
                data["file_url"] = f"/api/v2/projects/{project_id}/outputs/{data['id']}/file"
            outputs.append(data)
    return sorted(
        outputs,
        key=lambda item: (str(item.get("created_at") or ""), int(item.get("created_at_ns") or 0), str(item.get("id") or "")),
        reverse=True,
    )


def load_output(project_id: str, output_id: str) -> dict[str, Any]:
    output = read_json(output_meta_path(project_id, output_id), None)
    if not isinstance(output, dict):
        raise HTTPException(status_code=404, detail="输出版本不存在")
    if str(output.get("project_id") or "") != project_id:
        raise HTTPException(status_code=404, detail="输出版本不存在")
    return output


def create_render_output(project_id: str, body: RenderBody) -> dict[str, Any]:
    project = ensure_project(project_id)
    output_id = str(uuid4())
    output_video_path = renderer_root() / "render_tasks" / f"v2-{project_id}" / "out" / f"{output_id}.mp4"
    current_plan = read_json(scene_plan_path(project_id), {"scenes": []})
    current_scenes = current_plan.get("scenes") if isinstance(current_plan, dict) else []
    if not isinstance(current_scenes, list) or not current_scenes:
        build_quick_scene_plan(project_id, DEFAULT_FPS)
        current_plan = read_json(scene_plan_path(project_id), {"scenes": []})
        current_scenes = current_plan.get("scenes") if isinstance(current_plan, dict) else []
    if isinstance(current_scenes, list):
        apply_scene_routes(current_scenes)
    creative_scene_ids = [
        str(scene.get("id") or "")
        for scene in current_scenes
        if isinstance(scene, dict)
        and str((scene.get("engine") or {}).get("resolved") or "") in {ENGINE_HYPERFRAMES, ENGINE_HYBRID}
    ]
    run = create_run(
        project_dir(project_id),
        project_id,
        "render_project" if body.execute else "plan_project",
        [
            "route:scenes",
            *[f"creative:{scene_id}" for scene_id in creative_scene_ids],
            "build:render-plan",
            "render:remotion",
            "verify:output",
        ],
        {"output_id": output_id, "execute": body.execute},
    )
    try:
        prepare_creative_assets(
            project_id,
            PrepareScenesBody(
                execute=body.execute,
                allow_on_demand=str(os.environ.get("ANY2VIDEO_HYPERFRAMES_ON_DEMAND") or "").lower() in {"1", "true", "yes"},
                timeout_sec=min(body.timeout_sec, 60 * 20),
            ),
            run=run,
        )
        update_run_step(project_dir(project_id), run, "build:render-plan", "running", detail="正在生成统一渲染计划")
        plan = build_render_plan(
            project_id,
            RenderPlanBody(fps=DEFAULT_FPS, no_audio_seconds=DEFAULT_NO_AUDIO_SECONDS),
            output_video_path=output_video_path,
        )
        update_run_step(
            project_dir(project_id),
            run,
            "build:render-plan",
            "ready",
            detail=f"渲染计划共 {len(plan.get('props', {}).get('scenes') or [])} 个镜头",
            artifact={"kind": "render_plan", "path": str(render_plan_path(project_id))},
        )
        output = {
            "schema_version": "output_version.v2",
            "id": output_id,
            "project_id": project_id,
            "run_id": run["id"],
            "status": "rendering" if body.execute else "planned",
            "video_path": str(output_video_path),
            "render_command": plan.get("render_command"),
            "duration_sec": plan.get("duration_sec"),
            "log": "Remotion rendering" if body.execute else "render not executed",
            "created_at": now_iso(),
            "created_at_ns": time.time_ns(),
        }
        write_json(output_meta_path(project_id, output_id), output)
        if body.execute:
            update_run_step(project_dir(project_id), run, "render:remotion", "running", detail="Remotion 正在组装最终时间线")
            output_video_path.parent.mkdir(parents=True, exist_ok=True)
            started = time.time()
            result = subprocess.run(
                [
                    "npx",
                    "remotion",
                    "render",
                    "src/index.ts",
                    "ProductExperienceVideo",
                    str(output_video_path),
                    "--props",
                    str(plan["input_props_path"]),
                ],
                cwd=renderer_root(),
                text=True,
                capture_output=True,
                timeout=body.timeout_sec,
                check=False,
            )
            ready = result.returncode == 0 and output_video_path.is_file() and output_video_path.stat().st_size > 0
            output["status"] = "ready" if ready else "failed"
            output["log"] = (result.stdout + "\n" + result.stderr).strip() or (
                "Render completed" if ready else f"Remotion exited with code {result.returncode}"
            )
            update_run_step(
                project_dir(project_id),
                run,
                "render:remotion",
                "ready" if ready else "failed",
                detail="最终 MP4 已生成" if ready else f"Remotion 退出码 {result.returncode}",
                artifact={"kind": "video", "path": str(output_video_path), "output_id": output_id} if ready else None,
            )
            update_run_step(
                project_dir(project_id),
                run,
                "verify:output",
                "ready" if ready else "failed",
                detail=f"文件大小 {output_video_path.stat().st_size} 字节" if ready else "未得到有效 MP4",
            )
            output["elapsed_sec"] = round(time.time() - started, 3)
            project["status"] = "render_ready" if ready else "render_failed"
            save_project(project)
            finish_run(project_dir(project_id), run, "ready" if ready else "failed", "" if ready else output["log"][-1600:])
        else:
            update_run_step(project_dir(project_id), run, "render:remotion", "skipped", detail="仅生成计划")
            update_run_step(project_dir(project_id), run, "verify:output", "skipped", detail="尚未执行渲染")
            finish_run(project_dir(project_id), run, "ready")
        write_json(output_meta_path(project_id, output_id), output)
        output["file_url"] = f"/api/v2/projects/{project_id}/outputs/{output_id}/file"
        return output
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        message = f"渲染超时（{body.timeout_sec}s）\n{stdout}\n{stderr}".strip()
        update_run_step(project_dir(project_id), run, "render:remotion", "failed", detail=message[-1600:])
        update_run_step(project_dir(project_id), run, "verify:output", "failed", detail="渲染超时")
        finish_run(project_dir(project_id), run, "failed", message[-1600:])
        project["status"] = "render_failed"
        save_project(project)
        output = {
            "schema_version": "output_version.v2",
            "id": output_id,
            "project_id": project_id,
            "run_id": run["id"],
            "status": "failed",
            "video_path": str(output_video_path),
            "duration_sec": None,
            "log": message,
            "created_at": now_iso(),
            "created_at_ns": time.time_ns(),
        }
        write_json(output_meta_path(project_id, output_id), output)
        output["file_url"] = f"/api/v2/projects/{project_id}/outputs/{output_id}/file"
        return output
    except HTTPException as exc:
        finish_run(project_dir(project_id), run, "failed", str(exc.detail))
        raise
    except Exception as exc:
        finish_run(project_dir(project_id), run, "failed", str(exc))
        raise HTTPException(status_code=500, detail=f"本地执行失败：{exc}") from exc


def v2_router(max_upload_mb: int) -> APIRouter:
    router = APIRouter(prefix="/api/v2", tags=["v2-video-workbench"])
    max_bytes = max_upload_mb * 1024 * 1024

    @router.post("/projects")
    def post_project(body: ProjectCreateBody) -> dict[str, Any]:
        return create_project(body)

    @router.get("/projects")
    def get_projects() -> dict[str, Any]:
        return {"projects": list_projects(), "workspace_root": str(workspace_root())}

    @router.get("/capabilities")
    def get_capabilities() -> dict[str, Any]:
        return discover_capabilities(renderer_root(), workspace_root())

    @router.get("/projects/{project_id}")
    def get_project(project_id: str) -> dict[str, Any]:
        return detail_project(project_id)

    @router.get("/projects/{project_id}/runs")
    def get_project_runs(project_id: str) -> dict[str, Any]:
        ensure_project(project_id)
        return {"runs": list_runs(project_dir(project_id), limit=50)}

    @router.post("/projects/{project_id}/assets")
    async def post_asset(
        project_id: str,
        file: Optional[UploadFile] = File(default=None),
        content: str = Form(default=""),
        asset_type: Optional[str] = Form(default=None),
        title: str = Form(default=""),
        role: str = Form(default=""),
        tags: str = Form(default=""),
    ) -> dict[str, Any]:
        asset = await add_asset(
            project_id,
            upload=file,
            content=content,
            asset_type=asset_type,
            title=title,
            role=role,
            tags=tags,
            max_bytes=max_bytes,
        )
        return {"asset": asset, "project": detail_project(project_id)}

    @router.get("/projects/{project_id}/assets")
    def get_assets(project_id: str) -> dict[str, Any]:
        ensure_project(project_id)
        return {"assets": list_assets(project_id)}

    @router.get("/projects/{project_id}/assets/{asset_id}/file")
    def get_asset_file(project_id: str, asset_id: str) -> FileResponse:
        asset = load_asset(project_id, asset_id)
        path = Path(str(asset.get("path") or ""))
        if not path.is_file():
            raise HTTPException(status_code=404, detail="素材文件不存在")
        return FileResponse(path, media_type=asset.get("mime_type") or None)

    @router.post("/projects/{project_id}/brief")
    def post_brief(project_id: str, body: BriefBody) -> dict[str, Any]:
        return {"brief": save_brief(project_id, body), "project": detail_project(project_id)}

    @router.post("/projects/{project_id}/scene-plan")
    def post_scene_plan(project_id: str) -> dict[str, Any]:
        return {"scene_plan": build_scene_plan(project_id), "project": detail_project(project_id)}

    @router.post("/projects/{project_id}/scene-plan/quick")
    def post_quick_scene_plan(project_id: str) -> dict[str, Any]:
        return {"scene_plan": build_quick_scene_plan(project_id), "project": detail_project(project_id)}

    @router.post("/projects/{project_id}/scenes")
    def post_scene(project_id: str, body: SceneCreateBody) -> dict[str, Any]:
        return {"scene": create_scene(project_id, body), "project": detail_project(project_id)}

    @router.put("/projects/{project_id}/scenes/{scene_id}")
    def put_scene(project_id: str, scene_id: str, body: SceneUpdateBody) -> dict[str, Any]:
        return {"scene": update_scene(project_id, scene_id, body), "project": detail_project(project_id)}

    @router.post("/projects/{project_id}/scenes/{scene_id}/duplicate")
    def post_duplicate_scene(project_id: str, scene_id: str) -> dict[str, Any]:
        return {"scene": duplicate_scene(project_id, scene_id), "project": detail_project(project_id)}

    @router.delete("/projects/{project_id}/scenes/{scene_id}")
    def remove_scene(project_id: str, scene_id: str) -> dict[str, Any]:
        result = delete_scene(project_id, scene_id)
        return {**result, "project": detail_project(project_id)}

    @router.put("/projects/{project_id}/scene-order")
    def put_scene_order(project_id: str, body: SceneOrderBody) -> dict[str, Any]:
        return {"scenes": reorder_scenes(project_id, body), "project": detail_project(project_id)}

    @router.post("/projects/{project_id}/creative-scenes/prepare")
    def post_prepare_creative_scenes(project_id: str, body: PrepareScenesBody) -> dict[str, Any]:
        result = prepare_creative_assets(project_id, body)
        return {**result, "project": detail_project(project_id)}

    @router.post("/projects/{project_id}/scenes/{scene_id}/prepare")
    def post_prepare_scene(project_id: str, scene_id: str, body: PrepareScenesBody) -> dict[str, Any]:
        plan = read_json(scene_plan_path(project_id), {"scenes": []})
        scenes = plan.get("scenes") if isinstance(plan, dict) else []
        if not any(isinstance(scene, dict) and scene.get("id") == scene_id for scene in scenes or []):
            raise HTTPException(status_code=404, detail="镜头不存在")
        result = prepare_creative_assets(project_id, body, scene_ids=[scene_id])
        return {**result, "project": detail_project(project_id)}

    @router.post("/projects/{project_id}/render-plan")
    def post_render_plan(project_id: str, body: RenderPlanBody) -> dict[str, Any]:
        return {"render_plan": build_render_plan(project_id, body), "project": detail_project(project_id)}

    @router.post("/projects/{project_id}/render")
    def post_render(project_id: str, body: RenderBody) -> dict[str, Any]:
        return {"output": create_render_output(project_id, body), "project": detail_project(project_id)}

    @router.get("/projects/{project_id}/outputs")
    def get_outputs(project_id: str) -> dict[str, Any]:
        ensure_project(project_id)
        return {"outputs": list_outputs(project_id)}

    @router.get("/projects/{project_id}/outputs/{output_id}/file")
    def get_output_file(project_id: str, output_id: str) -> FileResponse:
        ensure_project(project_id)
        output = load_output(project_id, output_id)
        if output.get("status") != "ready":
            raise HTTPException(status_code=409, detail="成片尚未生成成功")
        path = Path(str(output.get("video_path") or ""))
        if not path.is_file():
            raise HTTPException(status_code=404, detail="成片文件不存在")
        return FileResponse(path, media_type="video/mp4")

    return router
