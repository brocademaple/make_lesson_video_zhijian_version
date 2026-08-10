"""Generic creator video project model and Remotion props adapter."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


DEFAULT_FPS = 30
DEFAULT_FORMAT = "vertical_1080x1920"
SUPPORTED_FORMATS = {
    "vertical_1080x1920": {"width": 1080, "height": 1920},
    "horizontal_1920x1080": {"width": 1920, "height": 1080},
    "square_1080": {"width": 1080, "height": 1080},
}
DEFAULT_VARIANT_ID = "primary"
DEFAULT_TEMPLATE_PACKAGE = "ProductExperience"


def read_video_project(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"无法读取 video_project.json：{path}") from exc
    if not isinstance(data, dict):
        raise ValueError("video_project.json 顶层必须是对象")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def clean_text(value: Any, *, limit: int = 200) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def format_dimensions(format_id: Any) -> dict[str, int]:
    key = str(format_id or DEFAULT_FORMAT)
    return dict(SUPPORTED_FORMATS.get(key) or SUPPORTED_FORMATS[DEFAULT_FORMAT])


def _project_root_for(project_path: Path, workspace_root: Path | None) -> Path:
    if workspace_root is not None:
        return workspace_root.resolve()
    return project_path.resolve().parent


def _rel_asset_path(raw: Any, *, project_path: Path, workspace_root: Path | None) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    path = Path(text)
    if path.is_absolute():
        root = _project_root_for(project_path, workspace_root)
        try:
            return path.resolve().relative_to(root).as_posix()
        except ValueError:
            return path.as_posix()
    return text.replace("\\", "/")


def _material_index(
    materials: list[Any],
    *,
    project_path: Path,
    workspace_root: Path | None,
) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for idx, raw in enumerate(materials):
        if not isinstance(raw, dict):
            continue
        material_id = clean_text(raw.get("id") or f"asset-{idx + 1}", limit=80)
        rel = _rel_asset_path(
            raw.get("relative") or raw.get("path") or raw.get("src"),
            project_path=project_path,
            workspace_root=workspace_root,
        )
        out[material_id] = {
            "id": material_id,
            "type": clean_text(raw.get("type") or "image", limit=32),
            "relative": rel,
            "label": clean_text(raw.get("label") or material_id, limit=80),
            "alt": clean_text(raw.get("alt") or raw.get("label") or "", limit=160),
        }
    return out


def _variant(project: dict[str, Any], variant_id: str) -> dict[str, Any]:
    variants = project.get("variants")
    if isinstance(variants, list):
        for item in variants:
            if isinstance(item, dict) and str(item.get("id") or "") == variant_id:
                return item
    return {
        "id": DEFAULT_VARIANT_ID,
        "title": project.get("title") or "未命名视频",
        "scene_ids": [],
        "template_package": project.get("template_package") or DEFAULT_TEMPLATE_PACKAGE,
    }


def _scene_ids_for_variant(project: dict[str, Any], selected_variant: dict[str, Any]) -> list[str]:
    raw_scene_ids = selected_variant.get("scene_ids")
    if isinstance(raw_scene_ids, list) and raw_scene_ids:
        return [str(v) for v in raw_scene_ids]
    scenes = project.get("scenes")
    if isinstance(scenes, list):
        return [str(scene.get("id") or f"scene-{idx + 1}") for idx, scene in enumerate(scenes) if isinstance(scene, dict)]
    return []


def _subtitle_segments(scene: dict[str, Any], duration_sec: float) -> list[dict[str, Any]]:
    explicit = scene.get("subtitle_segments")
    if isinstance(explicit, list) and explicit:
        out = []
        for item in explicit:
            if not isinstance(item, dict):
                continue
            text = clean_text(item.get("text"), limit=120)
            if text:
                out.append(
                    {
                        "start_sec": item.get("start_sec", 0),
                        "end_sec": item.get("end_sec", duration_sec),
                        "text": text,
                    }
                )
        if out:
            return out
    text = clean_text(scene.get("narration") or scene.get("onscreen_text"), limit=120)
    return [{"start_sec": 0, "end_sec": duration_sec, "text": text}] if text else []


def _scene_to_props(
    scene: dict[str, Any],
    *,
    index: int,
    total: int,
    fps: int,
    materials: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    scene_id = clean_text(scene.get("id") or f"scene-{index + 1}", limit=80)
    duration_sec = scene.get("duration_sec")
    if not isinstance(duration_sec, (int, float)) or duration_sec <= 0:
        duration_sec = 4.0
    explicit_frames = scene.get("duration_frames") or scene.get("durationInFrames")
    duration_frames = (
        max(1, int(explicit_frames))
        if isinstance(explicit_frames, (int, float)) and explicit_frames > 0
        else max(1, math.ceil(float(duration_sec) * fps))
    )
    material_id = clean_text(scene.get("asset_id") or scene.get("material_id"), limit=80)
    material = materials.get(material_id, {}) if material_id else {}
    audio_id = clean_text(scene.get("audio_asset_id") or scene.get("audio_id"), limit=80)
    audio = materials.get(audio_id, {}) if audio_id else {}
    effects = scene.get("effects") if isinstance(scene.get("effects"), list) else []
    callouts = scene.get("callouts") if isinstance(scene.get("callouts"), list) else []
    return {
        "id": scene_id,
        "title": clean_text(scene.get("title") or scene.get("onscreen_text") or f"镜头 {index + 1}", limit=80),
        "narration": clean_text(scene.get("narration"), limit=500),
        "onscreenText": clean_text(scene.get("onscreen_text") or scene.get("onscreenText"), limit=220),
        "shotType": clean_text(scene.get("shot_type") or scene.get("shotType") or "screen_focus", limit=48),
        "durationInFrames": duration_frames,
        "durationSec": round(float(duration_sec), 3),
        "asset": material,
        "audio": audio,
        "motion": scene.get("motion") if isinstance(scene.get("motion"), dict) else {},
        "focusRect": scene.get("focus_rect") if isinstance(scene.get("focus_rect"), dict) else {},
        "effects": effects,
        "callouts": callouts,
        "subtitleSegments": _subtitle_segments(scene, float(duration_sec)),
        "creativeAssetNeeded": bool(scene.get("creative_asset_needed")),
        "progress": {"index": index + 1, "total": total},
    }


def validate_video_project(project: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not clean_text(project.get("title"), limit=120):
        errors.append("缺少 title")
    scenes = project.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        errors.append("缺少 scenes")
    materials = project.get("materials")
    if materials is not None and not isinstance(materials, list):
        errors.append("materials 必须是数组")
    format_id = str(project.get("format") or DEFAULT_FORMAT)
    if format_id not in SUPPORTED_FORMATS:
        errors.append(f"不支持的 format：{format_id}")
    return errors


def video_project_to_props(
    project: dict[str, Any],
    *,
    project_path: Path,
    variant_id: str = DEFAULT_VARIANT_ID,
    fps: int = DEFAULT_FPS,
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    errors = validate_video_project(project)
    if errors:
        raise ValueError("；".join(errors))

    selected_variant = _variant(project, variant_id)
    scene_ids = _scene_ids_for_variant(project, selected_variant)
    scene_by_id: dict[str, dict[str, Any]] = {}
    for idx, scene in enumerate(project.get("scenes") or []):
        if isinstance(scene, dict):
            scene_by_id[str(scene.get("id") or f"scene-{idx + 1}")] = scene
    selected_scenes = [scene_by_id[sid] for sid in scene_ids if sid in scene_by_id]
    if not selected_scenes:
        raise ValueError(f"variant {variant_id} 没有可用 scenes")

    materials = _material_index(
        project.get("materials") if isinstance(project.get("materials"), list) else [],
        project_path=project_path,
        workspace_root=workspace_root,
    )
    dimensions = format_dimensions(project.get("format"))
    project_audio_id = clean_text(project.get("primary_audio_asset_id"), limit=80)
    project_audio = materials.get(project_audio_id, {}) if project_audio_id else {}
    scenes = [
        _scene_to_props(scene, index=idx, total=len(selected_scenes), fps=fps, materials=materials)
        for idx, scene in enumerate(selected_scenes)
    ]
    return {
        "schemaVersion": "visual_project_props.v1",
        "fps": fps,
        "width": dimensions["width"],
        "height": dimensions["height"],
        "format": project.get("format") or DEFAULT_FORMAT,
        "intent": clean_text(project.get("intent") or "product_experience", limit=80),
        "title": clean_text(selected_variant.get("title") or project.get("title"), limit=120),
        "templatePackage": clean_text(
            selected_variant.get("template_package")
            or project.get("template_package")
            or DEFAULT_TEMPLATE_PACKAGE,
            limit=80,
        ),
        "style": project.get("style") if isinstance(project.get("style"), dict) else {},
        "storyline": project.get("storyline") if isinstance(project.get("storyline"), list) else [],
        "audio": project_audio,
        "variant": {
            "id": clean_text(selected_variant.get("id") or variant_id, limit=80),
            "angle": clean_text(selected_variant.get("angle"), limit=160),
            "pace": clean_text(selected_variant.get("pace") or "balanced", limit=40),
        },
        "variants": project.get("variants") if isinstance(project.get("variants"), list) else [],
        "scenes": scenes,
    }


def write_video_project_props(
    project_json: Path,
    output: Path,
    *,
    variant_id: str = DEFAULT_VARIANT_ID,
    fps: int = DEFAULT_FPS,
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    project = read_video_project(project_json)
    props = video_project_to_props(
        project,
        project_path=project_json,
        variant_id=variant_id,
        fps=fps,
        workspace_root=workspace_root,
    )
    write_json(output, props)
    return props
