from __future__ import annotations

import json
import logging
import mimetypes
from contextlib import asynccontextmanager
import os
import shutil
import sys
import tempfile
from pathlib import Path


def _ensure_repo_root_for_rebuilder() -> None:
    """
    ``pip install -e .`` 若在 pyproject 加入 ``ppt_course_rebuilder`` 之前完成，
    虚拟环境里可能没有注册该包。若在源码树内运行，将仓库根目录加入 ``sys.path`` 兜底。
    """
    try:
        import ppt_course_rebuilder  # noqa: F401

        return
    except ModuleNotFoundError:
        pass
    here = Path(__file__).resolve()
    repo_root = here.parents[2]
    pkg = repo_root / "ppt_course_rebuilder" / "__init__.py"
    if pkg.is_file():
        rs = str(repo_root)
        if rs not in sys.path:
            sys.path.insert(0, rs)


_ensure_repo_root_for_rebuilder()
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote
from uuid import UUID, uuid4

from fastapi import Body, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.background import BackgroundTask

from ppt_course_deal.audio_duration import probe_audio_duration_seconds
from ppt_course_deal.audio_workspace_store import (
    append_segment_generation,
    delete_segment_generation,
    ensure_segment_versions_migrated,
    infer_slide_count,
    load_meta,
    normalize_transcript_segments,
    resolve_workspace_audio_path,
    resolve_workspace_audio_version_path,
    save_meta_for_workspace,
    slide_count_for_task,
    slide_duration_seconds_list,
    workspace_relative_segment_path_unique,
    workspace_root,
)
from ppt_course_deal.deck_sessions import create_session, get_session
from ppt_course_deal.extract import parse_pptx_bytes
from ppt_course_deal.external_settings import (
    DEFAULT_TRANSCRIPT_REWRITE_EXTRA_INSTRUCTIONS,
    get_director_llm_for_server_call,
    get_minimax_for_server_call,
    get_tts_for_server_call,
    get_transcript_rewrite_for_server_call,
    load_raw,
    merge_agent_update,
    merge_director_llm_update,
    merge_minimax_update,
    merge_tts_update,
    merge_transcript_rewrite_update,
    public_director_llm,
    public_minimax,
    public_tts,
    public_transcript_rewrite,
    save_raw,
)
from ppt_course_deal.fallback_preview import write_fallback_pngs
from ppt_course_deal.minimax_connect_archive import (
    redact_minimax,
    write_connect_test_record,
)
from ppt_course_deal.minimax_client import (
    MiniMaxTTSError,
    synthesize_to_mp3_bytes_traced,
)
from ppt_course_deal.pipeline import transform_pptx
from ppt_course_deal.raw_material_manifest import build_raw_material_manifest
from ppt_course_deal.remotion_input_props import create_render_task, render_task_status
from ppt_course_deal.slide_render import describe_preview_render_env, render_pptx_to_pngs
from ppt_course_deal.shape_image_export import list_slide_shape_files
from ppt_course_deal.slide_visual_generation import (
    build_slide_visual_prompt,
    generated_visual_coverage,
    generate_slide_visual_png,
    latest_generated_visual_path,
    save_generated_visual,
)
from ppt_course_deal.speech_synthesis import SpeechSynthesisError, synthesize_speech
from ppt_course_deal.task_storage import (
    delete_task,
    get_data_root,
    list_task_summaries,
    load_task,
    preview_png_path,
    save_task_from_parse,
    slide_shape_file_path,
    tasks_dir,
    update_task_display_name,
)
from ppt_course_deal.transcript_import import (
    MAX_SCRIPT_CHARS as TRANSCRIPT_IMPORT_MAX_CHARS,
    merge_with_resolutions,
    prepare_import,
)
from ppt_course_rebuilder.director import rebuild_course_from_raw_manifest
from ppt_course_rebuilder.director_validator import validate_director_manifest
from ppt_course_rebuilder.llm_client import DirectorLLMClient
from ppt_course_rebuilder.material_normalizer import build_course_material
from ppt_course_rebuilder.render_adapter import write_render_plan_from_task
from ppt_course_rebuilder.review import (
    approve_scene as rebuilder_approve_scene,
    export_approved_manifest as rebuilder_export_approved_manifest,
    reject_scene as rebuilder_reject_scene,
)

from ppt_course_deal.transcript_rewrite import (
    REWRITE_MINIMAL_SYSTEM,
    build_user_prompt_with_skill,
    chat_rewrite,
    normalize_minimax_rewrite_hints,
    sanitize_for_minimax_t2a,
    split_rewrite_output,
)

logger = logging.getLogger(__name__)

STATIC_ROOT = Path(__file__).resolve().parent.parent / "static"

_DEFAULT_MAX_UPLOAD_MB = 50
# 允许提高到数 GB；极大文件仍会整份载入内存做解析 / 转换，请保证机器内存与磁盘充足。
_MAX_UPLOAD_MB_CEILING = 4096


def get_max_upload_mb() -> int:
    """上传体积上限（兆字节）。环境变量 ``PPT_COURSE_MAX_UPLOAD_MB``，默认 50。"""
    raw = os.environ.get("PPT_COURSE_MAX_UPLOAD_MB", "").strip()
    if not raw:
        return _DEFAULT_MAX_UPLOAD_MB
    try:
        mb = int(raw)
    except ValueError:
        logger.warning(
            "无效 PPT_COURSE_MAX_UPLOAD_MB=%r，使用默认 %s MB",
            raw,
            _DEFAULT_MAX_UPLOAD_MB,
        )
        return _DEFAULT_MAX_UPLOAD_MB
    mb = max(1, min(mb, _MAX_UPLOAD_MB_CEILING))
    return mb


def get_max_upload_bytes() -> int:
    return get_max_upload_mb() * 1024 * 1024


class TaskRenameBody(BaseModel):
    filename: str = Field(min_length=1, max_length=200)


class SceneRejectBody(BaseModel):
    reason: Optional[str] = Field(default="", max_length=4000)


class RebuildCourseBody(BaseModel):
    use_llm: bool = True
    llm_max_slides: Optional[int] = Field(default=None, ge=1)


class RemotionRenderTaskBody(BaseModel):
    fps: int = Field(default=30, ge=1, le=120)
    max_slides: Optional[int] = Field(default=None, ge=1)
    no_audio_frames: int = Field(default=90, ge=1, le=60 * 60 * 120)
    bundle_audio: bool = False


class PipelineRunStepBody(BaseModel):
    step: str = Field(
        min_length=1,
        max_length=32,
        description="raw_material | course_material | director | audio | render_plan",
    )
    fps: int = Field(default=30, ge=1, le=120)
    max_slides: Optional[int] = Field(default=None, ge=1)
    no_audio_frames: int = Field(default=90, ge=1, le=60 * 60 * 120)
    use_llm: bool = True
    llm_max_slides: Optional[int] = Field(default=None, ge=1)


class GenerateSlideVisualBody(BaseModel):
    """文生图请求体；使用与口播稿优化相同的 ``transcript_rewrite`` API Base / Key。"""

    prompt: Optional[str] = Field(default=None, max_length=4000)
    size: str = Field(default="1792x1024", max_length=32)
    model: str = Field(default="gpt-image-2", max_length=128)


class ExternalPutBody(BaseModel):
    minimax: Optional[Dict[str, Any]] = None
    tts: Optional[Dict[str, Any]] = None
    agent: Optional[Dict[str, Any]] = None
    transcript_rewrite: Optional[Dict[str, Any]] = None
    director_llm: Optional[Dict[str, Any]] = None


def _read_json_file(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def build_task_workspace_status(task_id: str, task: dict[str, Any]) -> dict[str, Any]:
    """聚合 Deal / Rebuilder / Remotion 的任务级状态，供工作台流程条使用。"""
    task_root = tasks_dir() / task_id
    raw_path = task_root / "raw_material_manifest.json"
    material_path = task_root / "course_material.json"
    director_path = task_root / "director_manifest.json"
    approved_path = task_root / "approved_director_manifest.json"
    raw = _read_json_file(raw_path)
    material = _read_json_file(material_path)
    director = _read_json_file(director_path)
    approved = _read_json_file(approved_path)

    slide_count = int(task.get("slide_count") or len(task.get("slides") or []) or 0)
    audio_meta = load_meta("task", task_id)
    transcript_segments = audio_meta.get("transcript_segments")
    generated_files = audio_meta.get("generated_files")
    if not isinstance(transcript_segments, list):
        transcript_segments = []
    if not isinstance(generated_files, dict):
        generated_files = {}
    slide_durations = slide_duration_seconds_list(audio_meta, slide_count) if slide_count else []
    slides_with_audio = sum(1 for value in slide_durations if isinstance(value, (int, float)))
    scenes = director.get("scenes") if isinstance(director.get("scenes"), list) else []
    assets = director.get("assets") if isinstance(director.get("assets"), list) else []
    review = director.get("review") if isinstance(director.get("review"), dict) else {}
    generation = director.get("generation") if isinstance(director.get("generation"), dict) else {}
    approved_scenes = approved.get("scenes") if isinstance(approved.get("scenes"), list) else []
    remotion = render_task_status(task_id)
    render_plan_path = Path(remotion.get("task_dir") or "") / "render_plan.json"
    render_plan = _read_json_file(render_plan_path)

    return {
        "task_id": task_id,
        "filename": task.get("filename") or "",
        "slide_count": slide_count,
        "deal": {
            "ready": True,
            "images_available": bool(task.get("images_available")),
            "preview_count": int(task.get("preview_count") or 0),
            "preview_source": task.get("preview_source") or "",
            "images_error": task.get("images_error") or "",
        },
        "audio": {
            "ready": slides_with_audio > 0,
            "transcript_slide_count": len(transcript_segments),
            "generated_segment_count": len(generated_files),
            "slides_with_audio": slides_with_audio,
            "slide_duration_sec": slide_durations,
        },
        "rebuilder": {
            "raw_manifest_exists": raw_path.is_file(),
            "raw_slide_count": len(raw.get("slides") or []),
            "course_material_exists": material_path.is_file(),
            "course_material_slide_count": len(material.get("slides") or []),
            "director_manifest_exists": director_path.is_file(),
            "approved_manifest_exists": approved_path.is_file(),
            "scene_count": len(scenes),
            "asset_count": len(assets),
            "approved_scene_count": len(approved_scenes),
            "review": review,
            "planning_mode": generation.get("planning_mode") or "",
            "llm_error": generation.get("llm_error") or "",
            "quality_checks": director.get("quality_checks") or {},
        },
        "remotion": {
            **remotion,
            "render_plan_exists": render_plan_path.is_file(),
            "render_plan_path": str(render_plan_path),
            "render_plan_source": render_plan.get("source") or "",
        },
    }


PIPELINE_STEP_LABELS = {
    "raw_material": "原始素材清单",
    "course_material": "素材理解",
    "director": "导演脚本",
    "audio": "音频工坊",
    "render_plan": "成片计划",
}


def _pipeline_stage(
    key: str,
    label: str,
    *,
    ready: bool,
    detail: str,
    action: str,
    artifacts: Optional[List[Dict[str, Any]]] = None,
    missing_artifacts: Optional[List[str]] = None,
    warnings: Optional[List[str]] = None,
) -> Dict[str, Any]:
    missing = missing_artifacts or []
    warn = warnings or []
    if ready:
        state = "ready"
    elif missing or warn:
        state = "warn"
    else:
        state = "todo"
    return {
        "key": key,
        "label": label,
        "state": state,
        "ready": ready,
        "detail": detail,
        "next_action": action,
        "artifacts": artifacts or [],
        "missing_artifacts": missing,
        "warnings": warn,
    }


def _artifact(label: str, path: str, exists: bool) -> Dict[str, Any]:
    return {"label": label, "path": path, "exists": exists}


def build_task_pipeline_state(task_id: str, task: dict[str, Any]) -> dict[str, Any]:
    """中台级流水线状态：面向前端驾驶舱，而不是单个子系统。"""
    status = build_task_workspace_status(task_id, task)
    task_root = tasks_dir() / task_id
    raw_path = task_root / "raw_material_manifest.json"
    material_path = task_root / "course_material.json"
    director_path = task_root / "director_manifest.json"
    approved_path = task_root / "approved_director_manifest.json"
    remotion = status.get("remotion") or {}
    audio = status.get("audio") or {}
    rebuilder = status.get("rebuilder") or {}
    deal = status.get("deal") or {}

    preview_count = int(deal.get("preview_count") or 0)
    slide_count = int(status.get("slide_count") or 0)
    raw_exists = bool(rebuilder.get("raw_manifest_exists"))
    material_exists = bool(rebuilder.get("course_material_exists"))
    director_exists = bool(rebuilder.get("director_manifest_exists"))
    approved_exists = bool(rebuilder.get("approved_manifest_exists"))
    input_props_exists = bool(remotion.get("input_props_exists"))
    render_plan_exists = bool(remotion.get("render_plan_exists"))
    mp4_exists = bool(remotion.get("output_video_exists"))
    slides_with_audio = int(audio.get("slides_with_audio") or 0)

    stages = [
        _pipeline_stage(
            "deal",
            "PPT 输入 / DL 解析",
            ready=slide_count > 0,
            detail=f"{slide_count} 页 · 预览 {preview_count} 页",
            action="查看素材输入",
            artifacts=[],
            missing_artifacts=[] if slide_count else ["parsed_task"],
            warnings=[] if preview_count else ["未检测到整页预览图"],
        ),
        _pipeline_stage(
            "raw_material",
            "素材拆解清单",
            ready=raw_exists,
            detail=f"{rebuilder.get('raw_slide_count') or 0} 页 raw material",
            action="生成原始素材 Manifest",
            artifacts=[_artifact("raw_material_manifest.json", str(raw_path), raw_exists)],
            missing_artifacts=[] if raw_exists else ["raw_material_manifest.json"],
        ),
        _pipeline_stage(
            "course_material",
            "素材理解 / 标记",
            ready=material_exists,
            detail=f"{rebuilder.get('course_material_slide_count') or 0} 页素材已标记",
            action="生成素材标记",
            artifacts=[_artifact("course_material.json", str(material_path), material_exists)],
            missing_artifacts=[] if material_exists else ["course_material.json"],
            warnings=[] if raw_exists else ["需要先生成 raw_material_manifest.json"],
        ),
        _pipeline_stage(
            "director",
            "导演中枢",
            ready=director_exists,
            detail=(
                f"{rebuilder.get('scene_count') or 0} 个镜头"
                + (f" · {rebuilder.get('planning_mode')}" if rebuilder.get("planning_mode") else "")
            ),
            action="生成课程化导演脚本",
            artifacts=[
                _artifact("director_manifest.json", str(director_path), director_exists),
                _artifact("approved_director_manifest.json", str(approved_path), approved_exists),
            ],
            missing_artifacts=[] if director_exists else ["director_manifest.json"],
            warnings=[rebuilder.get("llm_error")] if rebuilder.get("llm_error") else [],
        ),
        _pipeline_stage(
            "audio",
            "音频工坊",
            ready=slides_with_audio > 0,
            detail=f"{slides_with_audio} 页已有音频 · {audio.get('generated_segment_count') or 0} 段",
            action="打开逐字稿与音频",
            artifacts=[],
            missing_artifacts=[] if slides_with_audio else ["audio_workspace/generated_files"],
            warnings=[] if slides_with_audio else ["可先使用 Edge TTS 生成口播音频"],
        ),
        _pipeline_stage(
            "render_plan",
            "成片工厂",
            ready=render_plan_exists or input_props_exists,
            detail=remotion.get("render_plan_source") or ("input-props 已生成" if input_props_exists else "待生成"),
            action="生成 RenderPlan / input-props",
            artifacts=[
                _artifact("render_plan.json", str(remotion.get("render_plan_path") or ""), render_plan_exists),
                _artifact("input-props.json", str(remotion.get("input_props_path") or ""), input_props_exists),
            ],
            missing_artifacts=[] if (render_plan_exists or input_props_exists) else ["render_plan.json", "input-props.json"],
        ),
        _pipeline_stage(
            "output",
            "成片展示",
            ready=mp4_exists,
            detail="已检测到 MP4" if mp4_exists else "待执行 Remotion render",
            action="查看成片产物",
            artifacts=[
                _artifact("video.mp4", str(remotion.get("output_video_path") or ""), mp4_exists),
            ],
            missing_artifacts=[] if mp4_exists else ["out/video.mp4"],
        ),
    ]
    ready_count = sum(1 for stage in stages if stage["ready"])
    return {
        "ok": True,
        **status,
        "pipeline": {
            "ready_count": ready_count,
            "stage_count": len(stages),
            "percent": round((ready_count / len(stages)) * 100) if stages else 0,
            "stages": stages,
        },
    }


def _pipeline_http_error(
    status_code: int,
    *,
    stage: str,
    message: str,
    missing_artifacts: Optional[List[str]] = None,
    next_action: str = "",
) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={
            "stage": stage,
            "message": message,
            "missing_artifacts": missing_artifacts or [],
            "next_action": next_action,
        },
    )


def run_pipeline_step(task_id: str, task: dict[str, Any], payload: PipelineRunStepBody) -> Dict[str, Any]:
    step = payload.step.strip()
    if step not in PIPELINE_STEP_LABELS:
        raise _pipeline_http_error(
            400,
            stage=step or "unknown",
            message="未知流水线步骤",
            missing_artifacts=[],
            next_action="请选择 raw_material / course_material / director / audio / render_plan",
        )
    task_root = tasks_dir() / task_id
    raw_path = task_root / "raw_material_manifest.json"
    material_path = task_root / "course_material.json"

    if step == "raw_material":
        manifest = build_raw_material_manifest(task_id)
        return {
            "ok": True,
            "stage": step,
            "message": "已生成 raw_material_manifest.json",
            "path": str(raw_path),
            "slide_count": len(manifest.get("slides") or []),
        }

    if step == "course_material":
        if not raw_path.is_file():
            build_raw_material_manifest(task_id)
        material = build_course_material(raw_path, material_path)
        return {
            "ok": True,
            "stage": step,
            "message": "已生成 course_material.json",
            "path": str(material_path),
            "slide_count": len(material.get("slides") or []),
            "asset_count": len(material.get("assets") or []),
        }

    if step == "director":
        if not raw_path.is_file():
            build_raw_material_manifest(task_id)
        if not material_path.is_file():
            build_course_material(raw_path, material_path)
        dm_path = task_root / "director_manifest.json"
        opts: dict[str, Any] = {"use_llm": payload.use_llm}
        if payload.llm_max_slides is not None:
            opts["llm_max_slides"] = payload.llm_max_slides
        dm = rebuild_course_from_raw_manifest(str(raw_path), str(dm_path), opts)
        generation = dm.get("generation") or {}
        return {
            "ok": True,
            "stage": step,
            "message": "已生成 director_manifest.json",
            "path": str(dm_path),
            "scene_count": len(dm.get("scenes") or []),
            "planning_mode": generation.get("planning_mode") or "",
            "llm_error": generation.get("llm_error") or "",
            "quality_checks": dm.get("quality_checks") or {},
        }

    if step == "audio":
        status = build_task_workspace_status(task_id, task)
        audio = status.get("audio") or {}
        if int(audio.get("slides_with_audio") or 0) > 0:
            return {
                "ok": True,
                "stage": step,
                "message": "已检测到可用于渲染的音频",
                "slides_with_audio": audio.get("slides_with_audio") or 0,
                "generated_segment_count": audio.get("generated_segment_count") or 0,
            }
        raise _pipeline_http_error(
            400,
            stage=step,
            message="尚未生成口播音频；请在音频工坊中按页生成。Edge TTS 已作为默认兜底 provider。",
            missing_artifacts=["audio_workspace/generated_files"],
            next_action="打开音频工坊，使用 Edge TTS 生成至少一页口播音频",
        )

    try:
        data = write_render_plan_from_task(
            task_id,
            fps=payload.fps,
            no_audio_frames=payload.no_audio_frames,
            max_scenes=payload.max_slides,
        )
    except ValueError as err:
        raise _pipeline_http_error(
            400,
            stage=step,
            message=str(err),
            missing_artifacts=["director_manifest.json"],
            next_action="先在导演中枢生成或审核导演脚本",
        ) from err
    return {
        "ok": True,
        "stage": step,
        "message": "已生成 RenderPlan / input-props",
        **data,
    }


class MiniMaxTestBody(BaseModel):
    """连通测试可选携带当前表单中的 MiniMax 字段（与 PUT 合并规则一致）。"""

    minimax: Optional[Dict[str, Any]] = None
    persist: bool = Field(
        default=True,
        description="为 True 且携带 minimax 时，在连通测试成功后将合并结果写入 external_apis.json。",
    )


class AudioWorkspacePutBody(BaseModel):
    task_id: Optional[str] = None
    session_id: Optional[str] = None
    slide_count: int = Field(ge=0, le=500)
    transcripts: List[str] = Field(default_factory=list)
    transcript_segments: Optional[List[List[str]]] = None


class AudioGenerateBody(BaseModel):
    task_id: Optional[str] = None
    session_id: Optional[str] = None
    slide_index: int = Field(ge=0, le=499)
    segment_index: int = Field(default=0, ge=0, le=99)
    minimax_overrides: Optional[Dict[str, Any]] = None


class AudioSegmentVersionDeleteBody(BaseModel):
    task_id: Optional[str] = None
    session_id: Optional[str] = None
    slide_index: int = Field(ge=0, le=499)
    segment_index: int = Field(default=0, ge=0, le=99)
    version_id: str = Field(min_length=1, max_length=80)


class TranscriptImportPreviewBody(BaseModel):
    task_id: str = Field(min_length=1, max_length=64)
    text: str = Field(min_length=1, max_length=TRANSCRIPT_IMPORT_MAX_CHARS)


class TranscriptImportApplyBody(BaseModel):
    task_id: str = Field(min_length=1, max_length=64)
    text: str = Field(min_length=1, max_length=TRANSCRIPT_IMPORT_MAX_CHARS)
    resolutions: Optional[Dict[str, str]] = None


class TranscriptRewriteBody(BaseModel):
    text: str = Field(min_length=1, max_length=9999)
    transcript_rewrite: Optional[Dict[str, Any]] = None
    #: 各页逐字稿拼接（只读语境）；用于统筹全课语气与衔接，模型仅改写 text 对应段
    course_transcript_context: Optional[str] = Field(default=None, max_length=48000)
    context_slide_index: Optional[int] = Field(default=None, ge=0)
    context_segment_index: Optional[int] = Field(default=None, ge=0)


class TranscriptRewriteTestBody(BaseModel):
    transcript_rewrite: Optional[Dict[str, Any]] = None


class DirectorLLMTestBody(BaseModel):
    director_llm: Optional[Dict[str, Any]] = None


_AUDIO_GEN_OVERRIDE_KEYS = frozenset(
    {
        "model",
        "voice_id",
        "language_boost",
        "output_format",
        "audio_format",
        "sample_rate",
        "bitrate",
        "speed",
        "vol",
        "pitch",
        "emotion",
        "stream",
        "group_id",
        "pronunciation_dict",
        "subtitle_enable",
    }
)


def _apply_minimax_generation_overrides(
    base: Dict[str, Any],
    raw: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """单次合成请求允许的字段覆盖（不含 api_key / api_base）。对应 MiniMax T2A OpenAPI。"""
    if not raw:
        return base
    out = dict(base)
    for k, v in raw.items():
        if k not in _AUDIO_GEN_OVERRIDE_KEYS:
            continue
        if v is None:
            continue
        if k == "emotion" and (
            v == "" or (isinstance(v, str) and not str(v).strip())
        ):
            out.pop("emotion", None)
            continue
        if k in ("sample_rate", "bitrate", "pitch"):
            try:
                out[k] = int(v)
            except (TypeError, ValueError):
                continue
        elif k in ("speed", "vol"):
            try:
                out[k] = float(v)
            except (TypeError, ValueError):
                continue
        elif k in ("stream", "subtitle_enable"):
            out[k] = bool(v)
        elif k == "group_id":
            out[k] = str(v).strip()
        else:
            out[k] = v
    return out


async def read_upload_body_capped(upload: UploadFile) -> bytes:
    """分块读取 multipart 正文，超过上限则拒绝，避免依赖单次 ``read()`` 的隐式上限。"""
    max_bytes = get_max_upload_bytes()
    out = bytearray()
    chunk_size = 1024 * 1024
    while True:
        part = await upload.read(chunk_size)
        if not part:
            break
        if len(out) + len(part) > max_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"文件过大（上限 {get_max_upload_mb()} MB）",
            )
        out.extend(part)
    return bytes(out)


@asynccontextmanager
async def _app_lifespan(app: FastAPI):
    """启动时预生成 OpenAPI；失败则 ``/docs``、``GET /openapi.json`` 不可用。"""
    try:
        app.openapi()
    except Exception:
        logger.exception(
            "OpenAPI schema 生成失败：Swagger UI（/docs）与 GET /openapi.json 将返回错误；"
            "常见原因包括路由请求体参数命名为保留名 ``body``、或 Pydantic 模型未完全解析。"
        )
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title="PPT 课程化重构",
        description="上传原始培训 PPTX，解析预览后生成适合录课的结构化 PPTX（MVP）",
        version="0.1.0",
        lifespan=_app_lifespan,
    )

    @application.get("/api/health")
    def health() -> Dict[str, Any]:
        return {
            "status": "ok",
            "max_upload_mb": get_max_upload_mb(),
            "preview_render": describe_preview_render_env(),
        }

    @application.post("/api/parse")
    async def parse_api(file: UploadFile = File(...)) -> dict:
        """解析整份 PPTX；若本机具备 LibreOffice + Poppler，则生成逐页 PNG 供预览。"""
        if not file.filename or not file.filename.lower().endswith(".pptx"):
            raise HTTPException(status_code=400, detail="请上传 .pptx 文件")
        raw = await read_upload_body_capped(file)
        if len(raw) == 0:
            raise HTTPException(status_code=400, detail="文件为空")
        try:
            slides = parse_pptx_bytes(raw)
        except Exception:
            logger.exception("parse failed")
            raise HTTPException(
                status_code=400,
                detail="无法解析该文件，请确认是有效的 PowerPoint .pptx（非 .ppt 老格式）",
            )

        session_id: Optional[str] = None
        images_available = False
        images_error: Optional[str] = None
        preview_count = 0
        preview_source: str = "libreoffice"
        task_persisted: Optional[str] = None

        work = Path(tempfile.mkdtemp(prefix="deck_preview_"))
        pngs: List[Path] = []
        try:
            inp = work / "input.pptx"
            inp.write_bytes(raw)
            try:
                pngs, images_error = render_pptx_to_pngs(inp, work)
            except Exception:
                logger.exception("LibreOffice / Poppler 渲染失败")
                pngs = []
                images_error = images_error or "渲染预览图失败（LibreOffice / Poppler）"

            if not pngs and slides:
                fb_dir = work / "fallback_png"
                pngs = write_fallback_pngs(slides, fb_dir)
                preview_source = "placeholder"
                hint = (
                    "已使用文字排版占位预览图（非像素级还原）；"
                    "在本机安装 LibreOffice 与 Poppler（pdftoppm）并重启服务后可显示真实幻灯片渲染图。"
                )
                if images_error and images_error.strip():
                    images_error = images_error.strip() + " " + hint
                else:
                    images_error = hint

            preview_count = len(pngs) if pngs else 0
            images_available = bool(pngs)

            if (
                pngs
                and preview_source == "libreoffice"
                and len(pngs) != len(slides)
            ):
                logger.warning(
                    "预览图数量 %s 与幻灯片页数 %s 不一致，预览图仅覆盖前 %s 页",
                    len(pngs),
                    len(slides),
                    preview_count,
                )

            # 先持久化（复制 PNG / 写 meta），再注册内存会话；避免 create_session 抛错导致从未写入「已存任务」
            task_persisted = save_task_from_parse(
                raw,
                file.filename or "uploaded.pptx",
                slides,
                pngs if pngs else None,
                preview_source,
                images_error,
                images_available,
                preview_count,
            )

            if pngs:
                session_id = create_session(work, pngs)
            else:
                shutil.rmtree(work, ignore_errors=True)

        except Exception:
            logger.exception("预览管线异常")
            shutil.rmtree(work, ignore_errors=True)
            images_error = images_error or "无法生成预览图"
            if not task_persisted and slides:
                task_persisted = save_task_from_parse(
                    raw,
                    file.filename or "uploaded.pptx",
                    slides,
                    None,
                    preview_source,
                    images_error,
                    False,
                    0,
                )

        return {
            "filename": file.filename or "uploaded.pptx",
            "slide_count": len(slides),
            "slides": slides,
            "session_id": session_id,
            "images_available": images_available,
            "preview_count": preview_count,
            "images_error": images_error,
            "preview_source": preview_source,
            "task_id": task_persisted,
        }

    @application.get("/api/tasks")
    def list_tasks_api() -> Dict[str, List[Dict[str, Any]]]:
        """已持久化的解析任务摘要列表；完整正文见 GET /api/tasks/{id}。"""
        return {"tasks": list_task_summaries()}

    @application.get("/api/tasks/{task_id}")
    def get_task_api(task_id: str) -> dict:
        """单任务完整解析 JSON（与解析接口正文结构一致）。"""
        data = load_task(task_id)
        if data is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        return data

    @application.get("/api/tasks/{task_id}/workspace-status")
    def get_task_workspace_status(task_id: str) -> Dict[str, Any]:
        """统一任务状态：Deal / Rebuilder / Remotion / Audio 子系统就绪情况。"""
        data = load_task(task_id)
        if data is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        return {"ok": True, **build_task_workspace_status(task_id, data)}

    @application.get("/api/tasks/{task_id}/pipeline-state")
    def get_task_pipeline_state(task_id: str) -> Dict[str, Any]:
        """中台流水线状态：聚合每个阶段的就绪情况、缺失产物和下一步动作。"""
        data = load_task(task_id)
        if data is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        return build_task_pipeline_state(task_id, data)

    @application.post("/api/tasks/{task_id}/pipeline/run-step")
    def post_task_pipeline_run_step(
        task_id: str,
        payload: PipelineRunStepBody,
    ) -> Dict[str, Any]:
        """按中台步骤触发已有底层能力，避免前端散落调用各子系统接口。"""
        data = load_task(task_id)
        if data is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        return run_pipeline_step(task_id, data, payload)

    @application.delete("/api/tasks/{task_id}")
    def delete_task_api(task_id: str) -> Dict[str, bool]:
        ok = delete_task(task_id)
        if not ok:
            raise HTTPException(status_code=404, detail="任务不存在")
        return {"ok": True}

    @application.patch("/api/tasks/{task_id}")
    def rename_task_api(
        task_id: str,
        payload: TaskRenameBody,
    ) -> Dict[str, Any]:
        name = payload.filename.strip()
        if not name:
            raise HTTPException(status_code=400, detail="名称不能为空")
        ok = update_task_display_name(task_id, name)
        if not ok:
            raise HTTPException(
                status_code=400,
                detail="无法更新名称（任务不存在或名称无效）",
            )
        return {"ok": True, "filename": name}

    @application.post("/api/tasks/{task_id}/raw-material-manifest")
    def post_raw_material_manifest(task_id: str) -> Dict[str, Any]:
        """生成并写入 raw_material_manifest.json。"""
        try:
            manifest = build_raw_material_manifest(task_id)
        except FileNotFoundError as err:
            raise HTTPException(status_code=404, detail=str(err)) from err
        slides = manifest.get("slides") or []
        out_path = tasks_dir() / task_id / "raw_material_manifest.json"
        return {
            "ok": True,
            "task_id": task_id,
            "path": str(out_path),
            "slide_count": len(slides),
            "shapes_total": sum(len(s.get("shapes") or []) for s in slides),
        }

    @application.post("/api/tasks/{task_id}/course-material")
    def post_course_material(task_id: str) -> Dict[str, Any]:
        """生成 Rebuilder 的 course_material.json 中间层。"""
        if load_task(task_id) is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        raw_path = tasks_dir() / task_id / "raw_material_manifest.json"
        if not raw_path.is_file():
            build_raw_material_manifest(task_id)
        out_path = tasks_dir() / task_id / "course_material.json"
        material = build_course_material(raw_path, out_path)
        return {
            "ok": True,
            "task_id": task_id,
            "path": str(out_path),
            "slide_count": len(material.get("slides") or []),
            "asset_count": len(material.get("assets") or []),
            "generated_segment_count": (
                (material.get("audio") or {}).get("generated_segment_count") or 0
            ),
        }

    @application.get("/api/tasks/{task_id}/course-material")
    def get_course_material(task_id: str) -> Dict[str, Any]:
        if load_task(task_id) is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        path = tasks_dir() / task_id / "course_material.json"
        if not path.is_file():
            raise HTTPException(status_code=404, detail="尚未生成 course_material.json")
        return _read_json_file(path)

    @application.post("/api/tasks/{task_id}/rebuild-course")
    def post_rebuild_course(
        task_id: str,
        payload: Optional[RebuildCourseBody] = Body(default=None),
    ) -> Dict[str, Any]:
        """生成 director_manifest.json（必要时先生成 raw manifest）。"""
        if load_task(task_id) is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        raw_path = tasks_dir() / task_id / "raw_material_manifest.json"
        if not raw_path.is_file():
            build_raw_material_manifest(task_id)
        material_path = tasks_dir() / task_id / "course_material.json"
        if not material_path.is_file():
            build_course_material(raw_path, material_path)
        dm_path = tasks_dir() / task_id / "director_manifest.json"
        opts: dict[str, Any] = {
            "use_llm": True if payload is None else payload.use_llm,
        }
        if payload is not None and payload.llm_max_slides is not None:
            opts["llm_max_slides"] = payload.llm_max_slides
        dm = rebuild_course_from_raw_manifest(
            str(raw_path),
            str(dm_path),
            opts,
        )
        assets = dm.get("assets") or []
        scenes = dm.get("scenes") or []
        generation = dm.get("generation") or {}
        return {
            "ok": True,
            "task_id": task_id,
            "director_manifest_path": str(dm_path),
            "raw_material_manifest_path": str(raw_path),
            "course_material_path": str(material_path),
            "scene_count": len(scenes),
            "asset_count": len(assets),
            "quality_checks": dm.get("quality_checks") or {},
            "planning_mode": generation.get("planning_mode") or "",
            "llm_model": generation.get("llm_model") or "",
            "llm_error": generation.get("llm_error") or "",
        }

    @application.post("/api/tasks/{task_id}/director-validate")
    def post_director_validate(task_id: str) -> Dict[str, Any]:
        if load_task(task_id) is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        dm_path = tasks_dir() / task_id / "director_manifest.json"
        if not dm_path.is_file():
            raise HTTPException(status_code=404, detail="尚未生成导演脚本，请先生成")
        material_path = tasks_dir() / task_id / "course_material.json"
        raw_path = tasks_dir() / task_id / "raw_material_manifest.json"
        dm = _read_json_file(dm_path)
        material = _read_json_file(material_path) or _read_json_file(raw_path)
        checks = validate_director_manifest(dm, material)
        dm["quality_checks"] = checks
        dm_path.write_text(json.dumps(dm, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True, "task_id": task_id, "quality_checks": checks}

    @application.post("/api/tasks/{task_id}/remotion-render-plan")
    def post_remotion_render_plan(
        task_id: str,
        payload: Optional[RemotionRenderTaskBody] = Body(default=None),
    ) -> Dict[str, Any]:
        """按 approved/director manifest 生成 render_plan 与 input-props。"""
        if load_task(task_id) is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        body = payload or RemotionRenderTaskBody()
        try:
            data = write_render_plan_from_task(
                task_id,
                fps=body.fps,
                no_audio_frames=body.no_audio_frames,
                max_scenes=body.max_slides,
            )
        except ValueError as err:
            raise HTTPException(status_code=400, detail=str(err)) from err
        return {"ok": True, "task_id": task_id, **data}

    @application.get("/api/tasks/{task_id}/remotion-render-task")
    def get_remotion_render_task(task_id: str) -> Dict[str, Any]:
        """查看该任务对应的 Remotion 渲染任务文件与成片状态。"""
        if load_task(task_id) is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        status = render_task_status(task_id)
        render_plan_path = Path(status.get("task_dir") or "") / "render_plan.json"
        render_plan = _read_json_file(render_plan_path)
        return {
            "ok": True,
            "task_id": task_id,
            **status,
            "render_plan_exists": render_plan_path.is_file(),
            "render_plan_path": str(render_plan_path),
            "render_plan_source": render_plan.get("source") or "",
        }

    @application.get("/api/tasks/{task_id}/output-video")
    def get_output_video(task_id: str) -> FileResponse:
        """播放已渲染 MP4，供统一工作台的成片展示模块使用。"""
        if load_task(task_id) is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        status = render_task_status(task_id)
        path = Path(status.get("output_video_path") or "")
        if not path.is_file():
            raise HTTPException(status_code=404, detail="尚未检测到 Remotion 成片 MP4")
        return FileResponse(
            path,
            media_type="video/mp4",
            filename=f"{task_id}.mp4",
        )

    @application.post("/api/tasks/{task_id}/remotion-render-task")
    def post_remotion_render_task(
        task_id: str,
        payload: Optional[RemotionRenderTaskBody] = Body(default=None),
    ) -> Dict[str, Any]:
        """生成 Remotion render_tasks/<task>/input-props.json，并返回渲染命令。"""
        if load_task(task_id) is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        body = payload or RemotionRenderTaskBody()
        try:
            data = create_render_task(
                task_id,
                fps=body.fps,
                max_slides=body.max_slides,
                no_audio_frames=body.no_audio_frames,
                bundle_audio=body.bundle_audio,
            )
        except ValueError as err:
            raise HTTPException(status_code=400, detail=str(err)) from err
        return {"ok": True, "task_id": task_id, **data}

    @application.get("/api/tasks/{task_id}/director-manifest")
    def get_director_manifest(task_id: str) -> Dict[str, Any]:
        path = tasks_dir() / task_id / "director_manifest.json"
        if load_task(task_id) is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        if not path.is_file():
            raise HTTPException(status_code=404, detail="尚未生成导演脚本，请先「生成课程化导演脚本」")
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as err:
            raise HTTPException(status_code=500, detail="导演脚本文件损坏") from err

    @application.post("/api/tasks/{task_id}/approve-scene/{scene_id}")
    def post_approve_scene(task_id: str, scene_id: str) -> Dict[str, Any]:
        if load_task(task_id) is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        path = tasks_dir() / task_id / "director_manifest.json"
        if not path.is_file():
            raise HTTPException(status_code=404, detail="尚未生成导演脚本")
        try:
            return rebuilder_approve_scene(str(path), scene_id)
        except ValueError as err:
            raise HTTPException(status_code=404, detail=str(err)) from err

    @application.post("/api/tasks/{task_id}/reject-scene/{scene_id}")
    def post_reject_scene(
        task_id: str,
        scene_id: str,
        payload: Optional[SceneRejectBody] = Body(default=None),
    ) -> Dict[str, Any]:
        if load_task(task_id) is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        path = tasks_dir() / task_id / "director_manifest.json"
        if not path.is_file():
            raise HTTPException(status_code=404, detail="尚未生成导演脚本")
        reason = (payload.reason if payload else "") or ""
        try:
            return rebuilder_reject_scene(str(path), scene_id, reason)
        except ValueError as err:
            raise HTTPException(status_code=404, detail=str(err)) from err

    @application.post("/api/tasks/{task_id}/export-approved-director-manifest")
    def post_export_approved_director_manifest(task_id: str) -> Dict[str, Any]:
        if load_task(task_id) is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        src = tasks_dir() / task_id / "director_manifest.json"
        if not src.is_file():
            raise HTTPException(status_code=404, detail="尚未生成导演脚本")
        out = tasks_dir() / task_id / "approved_director_manifest.json"
        return rebuilder_export_approved_manifest(str(src), str(out))

    @application.get("/api/tasks/{task_id}/preview/{slide_index:int}")
    def task_preview_png(task_id: str, slide_index: int) -> FileResponse:
        path = preview_png_path(task_id, slide_index)
        if path is None:
            raise HTTPException(status_code=404, detail="预览不存在")
        return FileResponse(
            path,
            media_type="image/png",
            headers={"Cache-Control": "private, max-age=86400"},
        )

    @application.get("/api/tasks/{task_id}/slide/{slide_index:int}/full")
    def task_slide_full_png_alt(task_id: str, slide_index: int) -> FileResponse:
        """与 ``/preview/{slide_index}`` 相同数据源；显式指向 ``previews/slide-NNNN/full.png`` 语义。"""
        if load_task(task_id) is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        path = preview_png_path(task_id, slide_index)
        if path is None:
            raise HTTPException(status_code=404, detail="整页预览不存在")
        return FileResponse(
            path,
            media_type="image/png",
            headers={"Cache-Control": "private, max-age=86400"},
        )

    @application.get("/api/tasks/{task_id}/slide/{slide_index:int}/shapes")
    def task_slide_shapes_list(task_id: str, slide_index: int) -> Dict[str, Any]:
        """列出该页 ``previews/slide-NNNN/shapes/`` 下已导出的内嵌图文件名（按 shape 顺序）。"""
        if load_task(task_id) is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        prev = tasks_dir() / task_id / "previews"
        files = list_slide_shape_files(prev, slide_index)
        return {
            "slide_index": slide_index,
            "count": len(files),
            "filenames": [p.name for p in files],
        }

    @application.get("/api/tasks/{task_id}/slide/{slide_index:int}/shape/{shape_index:int}")
    def task_slide_shape_asset(task_id: str, slide_index: int, shape_index: int) -> FileResponse:
        """按索引返回该页第 ``shape_index`` 张图片形状导出文件（从 0 起）。"""
        if load_task(task_id) is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        path = slide_shape_file_path(task_id, slide_index, shape_index)
        if path is None:
            raise HTTPException(status_code=404, detail="形状图片不存在")
        mt = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        return FileResponse(
            path,
            media_type=mt,
            headers={"Cache-Control": "private, max-age=86400"},
        )

    @application.post("/api/tasks/{task_id}/slide/{slide_index:int}/generate-visual")
    def generate_slide_visual_api(
        task_id: str,
        slide_index: int,
        payload: Optional[GenerateSlideVisualBody] = Body(None),
    ) -> Dict[str, Any]:
        """使用口播稿优化同一套 OpenAI 兼容网关，调用 ``gpt-image-2``（可改）生成配图并落盘。"""
        meta = load_task(task_id)
        if meta is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        slides_list = meta.get("slides") or []
        if slide_index < 0 or slide_index >= len(slides_list):
            raise HTTPException(status_code=400, detail="页码超出范围")

        tr = get_transcript_rewrite_for_server_call()
        api_base = (tr.get("api_base") or "").strip()
        api_key = (tr.get("api_key") or "").strip()
        body = payload if payload is not None else GenerateSlideVisualBody()
        slide_obj = slides_list[slide_index]
        if not isinstance(slide_obj, dict):
            slide_obj = {}
        prompt = (body.prompt or "").strip()
        if not prompt:
            prompt = build_slide_visual_prompt(slide_obj)

        try:
            png_bytes = generate_slide_visual_png(
                api_base=api_base,
                api_key=api_key,
                model=body.model.strip(),
                prompt=prompt,
                size=(body.size or "1792x1024").strip(),
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        task_dir = tasks_dir() / task_id
        path = save_generated_visual(
            task_dir,
            slide_index,
            png_bytes,
            model_slug=body.model.strip() or "gpt-image-2",
        )
        try:
            rel = path.resolve().relative_to(get_data_root())
            rel_str = rel.as_posix()
        except ValueError:
            rel_str = path.name

        return {
            "ok": True,
            "path_under_course_data": rel_str,
            "slide_index": slide_index,
            "model": body.model.strip(),
            "preview_url": f"/api/tasks/{task_id}/slide/{slide_index}/generated-visual",
        }

    @application.get("/api/tasks/{task_id}/slide/{slide_index:int}/generated-visual")
    def task_slide_generated_visual_png(task_id: str, slide_index: int) -> FileResponse:
        """返回该页最近一次「生成全新画面」的 PNG（若无则 404）。"""
        if load_task(task_id) is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        task_dir = tasks_dir() / task_id
        path = latest_generated_visual_path(task_dir, slide_index)
        if path is None or not path.is_file():
            raise HTTPException(status_code=404, detail="暂无 AI 生成画面")
        return FileResponse(
            path,
            media_type="image/png",
            headers={"Cache-Control": "private, no-store"},
        )

    @application.get("/api/tasks/{task_id}/generated-visual-coverage")
    def generated_visual_coverage_api(task_id: str) -> Dict[str, Any]:
        """各页是否已有 AI 生成图；**all_slides_complete** 为真时可启用「原版 / AI 重制版」分段主预览。"""
        meta = load_task(task_id)
        if meta is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        slides_list = meta.get("slides") or []
        sc = len(slides_list)
        task_dir = tasks_dir() / task_id
        return generated_visual_coverage(task_dir, sc)

    @application.get("/api/preview/{session_id}/{slide_index:int}")
    def preview_slide_png(session_id: str, slide_index: int) -> FileResponse:
        """按会话拉取某一页的 PNG（等同本地临时图床 URL）。"""
        sess = get_session(session_id)
        if sess is None:
            raise HTTPException(status_code=404, detail="预览已过期或不存在")
        paths = sess.png_paths
        if slide_index < 0 or slide_index >= len(paths):
            raise HTTPException(status_code=404, detail="页码超出范围")
        path = paths[slide_index]
        if not path.is_file():
            raise HTTPException(status_code=404, detail="预览文件缺失")
        return FileResponse(
            path,
            media_type="image/png",
            headers={"Cache-Control": "private, max-age=600"},
        )

    @application.post("/api/transform")
    async def transform_api(file: UploadFile = File(...)) -> Response:
        """生成课程化 PPTX。响应体为完整文件字节，避免临时目录过早删除导致文件损坏。"""
        if not file.filename or not file.filename.lower().endswith(".pptx"):
            raise HTTPException(status_code=400, detail="请上传 .pptx 文件")

        raw = await read_upload_body_capped(file)

        stem = Path(file.filename).stem
        tmpdir = tempfile.mkdtemp(prefix="ppt_course_deal_")
        in_path = Path(tmpdir) / "input.pptx"
        out_path = Path(tmpdir) / "output.pptx"

        try:
            in_path.write_bytes(raw)
            result = transform_pptx(in_path, out_path)
            payload = out_path.read_bytes()
        except HTTPException:
            raise
        except Exception:
            logger.exception("transform failed")
            shutil.rmtree(tmpdir, ignore_errors=True)
            raise HTTPException(
                status_code=500,
                detail="转换失败：请确认文件为有效的 PowerPoint 文稿（.pptx）",
            )

        download_name = f"{stem}_course.pptx"

        def cleanup() -> None:
            shutil.rmtree(tmpdir, ignore_errors=True)

        cd = "attachment; filename*=UTF-8''" + quote(download_name)

        return Response(
            content=payload,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "presentationml.presentation"
            ),
            headers={
                "Content-Disposition": cd,
                "X-Source-Slides": str(result.source_slide_count),
                "X-Output-Slides": str(result.output_slide_count),
            },
            background=BackgroundTask(cleanup),
        )

    def _parse_uuid_param(s: Optional[str]) -> Optional[str]:
        if not s or not str(s).strip():
            return None
        try:
            return str(UUID(str(s).strip()))
        except ValueError:
            return None

    def _workspace_scope(
        task_id: Optional[str],
        session_id: Optional[str],
    ) -> Tuple[str, str]:
        tid = _parse_uuid_param(task_id)
        sid = _parse_uuid_param(session_id)
        if tid and load_task(tid):
            return ("task", tid)
        if sid:
            return ("session", sid)
        raise HTTPException(
            status_code=400,
            detail="请提供有效的 task_id（已存任务）或 session_id（当前预览会话）",
        )

    @application.get("/api/settings/external")
    def get_external_settings() -> Dict[str, Any]:
        raw = load_raw()
        return {
            "minimax": public_minimax(raw.get("minimax") or {}),
            "tts": public_tts(raw.get("tts") or {}),
            "agent": raw.get("agent") or {},
            "transcript_rewrite": public_transcript_rewrite(
                raw.get("transcript_rewrite") or {}
            ),
            "director_llm": public_director_llm(raw.get("director_llm") or {}),
            "transcript_rewrite_defaults": {
                "extra_instructions": DEFAULT_TRANSCRIPT_REWRITE_EXTRA_INSTRUCTIONS,
            },
        }

    @application.put("/api/settings/external")
    def put_external_settings(
        payload: ExternalPutBody,
    ) -> Dict[str, Any]:
        raw = load_raw()
        if payload.minimax is not None:
            raw["minimax"] = merge_minimax_update(
                raw.get("minimax") or {},
                dict(payload.minimax),
            )
        if payload.tts is not None:
            raw["tts"] = merge_tts_update(
                raw.get("tts") or {},
                dict(payload.tts),
            )
        if payload.agent is not None:
            raw["agent"] = merge_agent_update(
                raw.get("agent") or {},
                dict(payload.agent),
            )
        if payload.transcript_rewrite is not None:
            raw["transcript_rewrite"] = merge_transcript_rewrite_update(
                raw.get("transcript_rewrite") or {},
                dict(payload.transcript_rewrite),
            )
        if payload.director_llm is not None:
            raw["director_llm"] = merge_director_llm_update(
                raw.get("director_llm") or {},
                dict(payload.director_llm),
            )
        save_raw(raw)
        return get_external_settings()

    @application.post("/api/settings/external/director-llm/test")
    def test_director_llm_connection(
        body: Optional[DirectorLLMTestBody] = Body(default=None),
    ) -> Dict[str, Any]:
        cfg = dict(get_director_llm_for_server_call())
        if body is not None and body.director_llm:
            cfg = merge_director_llm_update(cfg, dict(body.director_llm))
        if not cfg.get("enabled"):
            raise HTTPException(status_code=400, detail="请先启用「导演模型」")
        if not str(cfg.get("api_key") or "").strip():
            raise HTTPException(status_code=400, detail="请先填写 Director LLM API Key")
        try:
            client = DirectorLLMClient(
                api_key=str(cfg.get("api_key") or ""),
                base_url=str(cfg.get("api_base") or ""),
                model=str(cfg.get("model") or ""),
            )
            data = client.call_json(
                system="你是连通测试助手，只输出 JSON object。",
                user='请输出 {"ok": true, "role": "director_llm"}',
                temperature=0,
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"导演模型连通失败：{e}") from e
        return {
            "ok": True,
            "detail": "导演模型 API 可连通",
            "model": str(cfg.get("model") or ""),
            "echo": data,
        }

    @application.post("/api/settings/external/transcript-rewrite/test")
    def test_transcript_rewrite_connection(
        body: Optional[TranscriptRewriteTestBody] = Body(default=None),
    ) -> Dict[str, Any]:
        cfg = dict(get_transcript_rewrite_for_server_call())
        if body is not None and body.transcript_rewrite:
            cfg = merge_transcript_rewrite_update(
                cfg,
                dict(body.transcript_rewrite),
            )
        prov = (cfg.get("provider") or "none").strip().lower()
        if prov != "openai_compatible":
            raise HTTPException(
                status_code=400,
                detail="请先将「接入方式」设为 OpenAI 兼容 API",
            )
        try:
            _ = chat_rewrite(
                api_base=str(cfg.get("api_base") or "").strip(),
                api_key=str(cfg.get("api_key") or ""),
                model=str(cfg.get("model") or "").strip(),
                system=REWRITE_MINIMAL_SYSTEM,
                user="只输出一个字：好",
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        return {"ok": True, "detail": "口播稿优化 API 可连通"}

    @application.post("/api/transcript/rewrite")
    def api_transcript_rewrite(body: TranscriptRewriteBody) -> Dict[str, Any]:
        cfg = dict(get_transcript_rewrite_for_server_call())
        if body.transcript_rewrite is not None:
            cfg = merge_transcript_rewrite_update(
                cfg,
                dict(body.transcript_rewrite),
            )
        prov = (cfg.get("provider") or "none").strip().lower()
        if prov != "openai_compatible":
            raise HTTPException(
                status_code=400,
                detail="请先在「外部 API 配置 → 口播稿优化」中选择 OpenAI 兼容并保存 API Key",
            )
        extra = (cfg.get("extra_instructions") or "").strip()
        user_msg = build_user_prompt_with_skill(
            body.text,
            extra_instructions=extra,
            course_transcript_context=body.course_transcript_context,
            context_slide_index=body.context_slide_index,
            context_segment_index=body.context_segment_index,
        )
        try:
            raw_out = chat_rewrite(
                api_base=str(cfg.get("api_base") or "").strip(),
                api_key=str(cfg.get("api_key") or ""),
                model=str(cfg.get("model") or "").strip(),
                system=REWRITE_MINIMAL_SYSTEM,
                user=user_msg,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        transcript_part, raw_hints = split_rewrite_output(raw_out)
        cleaned, warnings = sanitize_for_minimax_t2a(transcript_part)
        hints_payload, delivery_notes, hint_warns = normalize_minimax_rewrite_hints(
            raw_hints
        )
        warnings = list(warnings) + list(hint_warns)
        out: Dict[str, Any] = {
            "ok": True,
            "rewritten_text": cleaned,
            "sanitize_warnings": warnings,
        }
        if hints_payload:
            out["minimax_hints"] = hints_payload
        if delivery_notes:
            out["delivery_notes"] = delivery_notes
        return out

    @application.post("/api/settings/external/minimax/test")
    def test_minimax_connection(
        body: Optional[MiniMaxTestBody] = Body(default=None),
    ) -> Dict[str, Any]:
        mm = dict(get_minimax_for_server_call())
        if body is not None and body.minimax:
            mm = merge_minimax_update(mm, dict(body.minimax))

        probe = "连通测试：MiniMax 语音合成接口工作正常。"
        record: dict[str, Any] = {
            "kind": "minimax_connect_test",
            "probe_text": probe,
            "minimax_settings_redacted": redact_minimax(mm),
            "persisted_to_external_apis": False,
        }
        try:
            audio_bytes, trace = synthesize_to_mp3_bytes_traced(mm, probe)
            persisted = False
            if body is not None and body.minimax and body.persist:
                raw_cfg = load_raw()
                raw_cfg["minimax"] = merge_minimax_update(
                    raw_cfg.get("minimax") or {},
                    dict(body.minimax),
                )
                save_raw(raw_cfg)
                persisted = True
            record["persisted_to_external_apis"] = persisted
            record["ok"] = True
            record["synthesis_trace"] = trace
            record["result_audio_bytes"] = len(audio_bytes)
            archive_rel = write_connect_test_record(record)
            out: Dict[str, Any] = {
                "ok": True,
                "detail": "请求成功，已收到音频数据",
                "persisted": persisted,
                "audio_bytes": len(audio_bytes),
            }
            if archive_rel:
                out["archive_path"] = archive_rel
            return out
        except MiniMaxTTSError as e:
            record["ok"] = False
            record["error"] = str(e)
            archive_rel = write_connect_test_record(record)
            detail = str(e)
            if archive_rel:
                detail = f"{detail}（已存档：{archive_rel}）"
            raise HTTPException(status_code=400, detail=detail) from e
        except Exception:
            logger.exception("MiniMax 连通测试异常")
            raise HTTPException(status_code=500, detail="连通测试失败") from None

    @application.get("/api/audio/workspace")
    def get_audio_workspace(
        task_id: Optional[str] = None,
        session_id: Optional[str] = None,
        slide_count: Optional[int] = Query(default=None, ge=1, le=500),
    ) -> Dict[str, Any]:
        kind, key = _workspace_scope(task_id, session_id)
        sc: Optional[int] = None
        if kind == "task":
            sc = slide_count_for_task(key)
        if sc is None:
            if slide_count is None:
                raise HTTPException(
                    status_code=400,
                    detail="非已存任务时请传入 slide_count",
                )
            sc = slide_count
        ensure_segment_versions_migrated(kind, key)
        meta = load_meta(kind, key)
        transcripts = list(meta.get("transcripts") or [])
        while len(transcripts) < sc:
            transcripts.append("")
        transcripts = transcripts[:sc]
        transcript_segments = normalize_transcript_segments(meta, sc)
        seg_dur = meta.get("segment_duration_sec") or {}
        if not isinstance(seg_dur, dict):
            seg_dur = {}
        sv = meta.get("segment_versions")
        if not isinstance(sv, dict):
            sv = {}
        return {
            "kind": kind,
            "key": key,
            "slide_count": sc,
            "transcripts": transcripts,
            "transcript_segments": transcript_segments,
            "generated_files": meta.get("generated_files") or {},
            "segment_versions": sv,
            "segment_duration_sec": seg_dur,
            "slide_duration_sec": slide_duration_seconds_list(meta, sc),
        }

    @application.put("/api/audio/workspace")
    def put_audio_workspace(
        payload: AudioWorkspacePutBody,
    ) -> Dict[str, Any]:
        kind, key = _workspace_scope(payload.task_id, payload.session_id)
        save_meta_for_workspace(
            kind,
            key,
            payload.slide_count,
            transcript_segments=payload.transcript_segments,
            transcripts_flat=payload.transcripts,
        )
        meta = load_meta(kind, key)
        sc = payload.slide_count
        return {
            "ok": True,
            "slide_count": payload.slide_count,
            "transcripts": meta.get("transcripts") or [],
            "transcript_segments": normalize_transcript_segments(meta, sc),
        }

    @application.post("/api/audio/workspace/generate")
    def generate_slide_audio(
        payload: AudioGenerateBody,
    ) -> Dict[str, Any]:
        kind, key = _workspace_scope(payload.task_id, payload.session_id)
        meta = load_meta(kind, key)
        sc = max(
            infer_slide_count(meta, kind, key),
            payload.slide_index + 1,
        )
        segs = normalize_transcript_segments(meta, sc)
        if payload.slide_index >= len(segs):
            raise HTTPException(status_code=400, detail="逐字稿尚未初始化该页")
        rows = segs[payload.slide_index]
        if payload.segment_index >= len(rows):
            raise HTTPException(
                status_code=400,
                detail="该段逐字稿不存在，请在弹窗中添加段落并保存",
            )
        text = (rows[payload.segment_index] or "").strip()
        if not text:
            raise HTTPException(status_code=400, detail="该段逐字稿为空，请先填写并保存")

        mm = _apply_minimax_generation_overrides(
            get_minimax_for_server_call(),
            payload.minimax_overrides,
        )
        tts = get_tts_for_server_call()
        try:
            synth = synthesize_speech(minimax=mm, tts=tts, text=text)
        except SpeechSynthesisError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        audio_bytes = synth.audio_bytes
        fmt = (synth.audio_format or "mp3").lower()
        if fmt not in ("mp3", "pcm", "flac"):
            fmt = "mp3"
        uniq = uuid4().hex[:12]
        rel_path = workspace_relative_segment_path_unique(
            payload.slide_index,
            payload.segment_index,
            text,
            fmt,
            uniq,
        )
        path = workspace_root(kind, key) / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(audio_bytes)
        duration_sec = probe_audio_duration_seconds(path)
        version_id = append_segment_generation(
            kind,
            key,
            payload.slide_index,
            payload.segment_index,
            rel_path,
            duration_sec=duration_sec,
        )
        meta_after = load_meta(kind, key)
        slide_durs = slide_duration_seconds_list(meta_after, sc)
        return {
            "ok": True,
            "slide_index": payload.slide_index,
            "segment_index": payload.segment_index,
            "filename": rel_path,
            "version_id": version_id,
            "duration_sec": duration_sec,
            "slide_duration_sec": slide_durs,
            "tts_provider": synth.provider,
            "tts_fallback_used": synth.fallback_used,
            "tts_primary_error": synth.primary_error,
            "url": (
                f"/api/audio/workspace/file?kind={kind}&key={quote(key, safe='')}"
                f"&slide_index={payload.slide_index}"
                f"&segment_index={payload.segment_index}"
                f"&version_id={quote(version_id, safe='')}"
            ),
        }

    @application.post("/api/audio/workspace/import-transcript/preview")
    def import_transcript_preview(
        payload: TranscriptImportPreviewBody,
    ) -> Dict[str, Any]:
        """解析整稿逐字稿，返回冲突列表与警告（不写盘）。"""
        tid = _parse_uuid_param(payload.task_id)
        if not tid:
            raise HTTPException(
                status_code=400,
                detail="task_id 无效：须为有效 UUID（已存任务 ID）",
            )
        if load_task(tid) is None:
            raise HTTPException(status_code=404, detail="任务不存在或已删除")
        sc = slide_count_for_task(tid)
        if sc is None or sc < 1:
            raise HTTPException(status_code=400, detail="无法取得课件页数")
        meta = load_meta("task", tid)
        existing_segs = normalize_transcript_segments(meta, sc)
        try:
            result = prepare_import(payload.text.strip(), sc, existing_segs)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        out = {
            "ok": True,
            "slide_count": result["slide_count"],
            "filled_slides": result["filled_slides"],
            "warnings": result["warnings"],
            "conflicts": result["conflicts"],
            "conflict_count": len(result["conflicts"]),
        }
        return out

    @application.post("/api/audio/workspace/import-transcript/apply")
    def import_transcript_apply(
        payload: TranscriptImportApplyBody,
    ) -> Dict[str, Any]:
        """将整稿逐字稿写入任务音频工作区；有冲突时需传入 resolutions（每页 import / keep）。"""
        tid = _parse_uuid_param(payload.task_id)
        if not tid:
            raise HTTPException(
                status_code=400,
                detail="task_id 无效：须为有效 UUID（已存任务 ID）",
            )
        if load_task(tid) is None:
            raise HTTPException(status_code=404, detail="任务不存在或已删除")
        sc = slide_count_for_task(tid)
        if sc is None or sc < 1:
            raise HTTPException(status_code=400, detail="无法取得课件页数")
        meta = load_meta("task", tid)
        existing_segs = normalize_transcript_segments(meta, sc)
        try:
            prep = prepare_import(payload.text.strip(), sc, existing_segs)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        conflicts = prep["conflicts"]
        proposed = prep["proposed_transcript_segments"]
        conflict_indices = {c["slide_index"] for c in conflicts}

        if conflicts:
            res = payload.resolutions or {}
            needed = {str(c["slide_index"]) for c in conflicts}
            if set(res.keys()) != needed:
                raise HTTPException(
                    status_code=400,
                    detail="部分页面已有逐字稿且与导入稿不一致，请在 resolutions 中为每个冲突页选择 "
                    "import（采用导入）或 keep（保留已有）。",
                )
            for k, v in res.items():
                if v not in ("import", "keep"):
                    raise HTTPException(
                        status_code=400,
                        detail=f"无效的覆盖选择：{k}={v}（仅允许 import 或 keep）",
                    )
            final_segs = merge_with_resolutions(
                existing_segs,
                proposed,
                conflict_indices,
                res,
                sc,
            )
        else:
            final_segs = proposed

        save_meta_for_workspace(
            "task",
            tid,
            sc,
            transcript_segments=final_segs,
            transcripts_flat=None,
        )
        return {
            "ok": True,
            "slide_count": sc,
            "warnings": prep["warnings"],
            "conflict_count": len(conflicts),
        }

    @application.delete("/api/audio/workspace/segment-version")
    def delete_workspace_segment_version(
        payload: AudioSegmentVersionDeleteBody = Body(...),
    ) -> Dict[str, Any]:
        kind, key = _workspace_scope(payload.task_id, payload.session_id)
        try:
            UUID(key)
        except ValueError as err:
            raise HTTPException(status_code=400, detail="key 无效") from err
        if kind == "task" and load_task(key) is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        ok = delete_segment_generation(
            kind,
            key,
            payload.slide_index,
            payload.segment_index,
            payload.version_id,
        )
        if not ok:
            raise HTTPException(status_code=404, detail="未找到该生成记录")
        meta = load_meta(kind, key)
        sc = infer_slide_count(meta, kind, key)
        return {
            "ok": True,
            "generated_files": meta.get("generated_files") or {},
            "segment_versions": meta.get("segment_versions") or {},
            "segment_duration_sec": meta.get("segment_duration_sec") or {},
            "slide_duration_sec": slide_duration_seconds_list(meta, sc),
        }

    @application.get("/api/audio/workspace/file")
    def get_workspace_audio_file(
        kind: str = Query(...),
        key: str = Query(...),
        slide_index: int = Query(ge=0, le=499),
        segment_index: int = Query(default=0, ge=0, le=99),
        version_id: Optional[str] = Query(default=None, max_length=80),
    ) -> FileResponse:
        if kind not in ("task", "session"):
            raise HTTPException(status_code=400, detail="kind 无效")
        try:
            UUID(key)
        except ValueError as err:
            raise HTTPException(status_code=400, detail="key 无效") from err
        if kind == "task" and load_task(key) is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        mm = get_minimax_for_server_call()
        fmt = (mm.get("audio_format") or "mp3").lower()
        if fmt not in ("mp3", "pcm", "flac"):
            fmt = "mp3"
        path: Path | None = None
        vid = (version_id or "").strip()
        if vid:
            path = resolve_workspace_audio_version_path(
                kind, key, slide_index, segment_index, vid
            )
        else:
            path = resolve_workspace_audio_path(kind, key, slide_index, segment_index, fmt)
        if path is None:
            raise HTTPException(status_code=404, detail="音频不存在，请先生成")
        ext = path.suffix.lower().lstrip(".") or fmt
        media = {
            "mp3": "audio/mpeg",
            "pcm": "audio/pcm",
            "flac": "audio/flac",
        }.get(ext, "application/octet-stream")
        return FileResponse(
            path,
            media_type=media,
            headers={"Cache-Control": "private, max-age=3600"},
        )

    index_path = STATIC_ROOT / "index.html"

    @application.get("/")
    def serve_index() -> FileResponse:
        if not index_path.is_file():
            raise HTTPException(status_code=404, detail="前端资源未找到")
        return FileResponse(index_path)

    if STATIC_ROOT.is_dir():
        application.mount(
            "/assets",
            StaticFiles(directory=str(STATIC_ROOT)),
            name="assets",
        )

    return application


app = create_app()
