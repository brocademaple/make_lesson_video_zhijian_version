from __future__ import annotations

import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote
from uuid import UUID

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.background import BackgroundTask

from ppt_course_deal.audio_workspace_store import (
    load_meta,
    record_generated,
    save_meta,
    slide_audio_path,
    slide_count_for_task,
)
from ppt_course_deal.deck_sessions import create_session, get_session
from ppt_course_deal.extract import parse_pptx_bytes
from ppt_course_deal.external_settings import (
    get_minimax_for_server_call,
    load_raw,
    merge_agent_update,
    merge_minimax_update,
    public_minimax,
    save_raw,
)
from ppt_course_deal.fallback_preview import write_fallback_pngs
from ppt_course_deal.minimax_client import MiniMaxTTSError, synthesize_to_mp3_bytes
from ppt_course_deal.pipeline import transform_pptx
from ppt_course_deal.slide_render import describe_preview_render_env, render_pptx_to_pngs
from ppt_course_deal.task_storage import (
    delete_task,
    list_task_summaries,
    load_task,
    preview_png_path,
    save_task_from_parse,
    update_task_display_name,
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


def create_app() -> FastAPI:
    application = FastAPI(
        title="PPT 课程化重构",
        description="上传原始培训 PPTX，解析预览后生成适合录课的结构化 PPTX（MVP）",
        version="0.1.0",
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

    @application.delete("/api/tasks/{task_id}")
    def delete_task_api(task_id: str) -> Dict[str, bool]:
        ok = delete_task(task_id)
        if not ok:
            raise HTTPException(status_code=404, detail="任务不存在")
        return {"ok": True}

    class TaskRenameBody(BaseModel):
        filename: str = Field(min_length=1, max_length=200)

    @application.patch("/api/tasks/{task_id}")
    def rename_task_api(task_id: str, body: TaskRenameBody) -> Dict[str, Any]:
        name = body.filename.strip()
        if not name:
            raise HTTPException(status_code=400, detail="名称不能为空")
        ok = update_task_display_name(task_id, name)
        if not ok:
            raise HTTPException(
                status_code=400,
                detail="无法更新名称（任务不存在或名称无效）",
            )
        return {"ok": True, "filename": name}

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

    class ExternalPutBody(BaseModel):
        # Python 3.9 + Pydantic：避免 dict[...] | None 在类内求值失败
        minimax: Optional[Dict[str, Any]] = None
        agent: Optional[Dict[str, Any]] = None

    class AudioWorkspacePutBody(BaseModel):
        task_id: Optional[str] = None
        session_id: Optional[str] = None
        slide_count: int = Field(ge=0, le=500)
        transcripts: List[str] = Field(default_factory=list)

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
            elif k == "stream":
                out[k] = bool(v)
            elif k == "group_id":
                out[k] = str(v).strip()
            else:
                out[k] = v
        return out

    class AudioGenerateBody(BaseModel):
        task_id: Optional[str] = None
        session_id: Optional[str] = None
        slide_index: int = Field(ge=0, le=499)
        minimax_overrides: Optional[Dict[str, Any]] = None

    @application.get("/api/settings/external")
    def get_external_settings() -> Dict[str, Any]:
        raw = load_raw()
        return {
            "minimax": public_minimax(raw.get("minimax") or {}),
            "agent": raw.get("agent") or {},
        }

    @application.put("/api/settings/external")
    def put_external_settings(body: ExternalPutBody) -> Dict[str, Any]:
        raw = load_raw()
        if body.minimax is not None:
            raw["minimax"] = merge_minimax_update(
                raw.get("minimax") or {},
                dict(body.minimax),
            )
        if body.agent is not None:
            raw["agent"] = merge_agent_update(
                raw.get("agent") or {},
                dict(body.agent),
            )
        save_raw(raw)
        return get_external_settings()

    @application.post("/api/settings/external/minimax/test")
    def test_minimax_connection() -> Dict[str, Any]:
        mm = get_minimax_for_server_call()
        probe = "连通测试：MiniMax 语音合成接口工作正常。"
        try:
            synthesize_to_mp3_bytes(mm, probe)
        except MiniMaxTTSError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except Exception:
            logger.exception("MiniMax 连通测试异常")
            raise HTTPException(status_code=500, detail="连通测试失败") from None
        return {"ok": True, "detail": "请求成功，已收到音频数据"}

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
        meta = load_meta(kind, key)
        transcripts = list(meta.get("transcripts") or [])
        while len(transcripts) < sc:
            transcripts.append("")
        transcripts = transcripts[:sc]
        return {
            "kind": kind,
            "key": key,
            "slide_count": sc,
            "transcripts": transcripts,
            "generated_files": meta.get("generated_files") or {},
        }

    @application.put("/api/audio/workspace")
    def put_audio_workspace(body: AudioWorkspacePutBody) -> Dict[str, Any]:
        kind, key = _workspace_scope(body.task_id, body.session_id)
        save_meta(kind, key, body.transcripts, body.slide_count)
        meta = load_meta(kind, key)
        return {
            "ok": True,
            "slide_count": body.slide_count,
            "transcripts": meta.get("transcripts") or [],
        }

    @application.post("/api/audio/workspace/generate")
    def generate_slide_audio(body: AudioGenerateBody) -> Dict[str, Any]:
        kind, key = _workspace_scope(body.task_id, body.session_id)
        meta = load_meta(kind, key)
        transcripts = list(meta.get("transcripts") or [])
        if body.slide_index >= len(transcripts):
            raise HTTPException(status_code=400, detail="逐字稿尚未初始化该页")
        text = (transcripts[body.slide_index] or "").strip()
        if not text:
            raise HTTPException(status_code=400, detail="本页逐字稿为空，请先填写并保存")

        mm = _apply_minimax_generation_overrides(
            get_minimax_for_server_call(),
            body.minimax_overrides,
        )
        try:
            audio_bytes = synthesize_to_mp3_bytes(mm, text)
        except MiniMaxTTSError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        fmt = (mm.get("audio_format") or "mp3").lower()
        if fmt not in ("mp3", "pcm", "flac"):
            fmt = "mp3"
        path = slide_audio_path(kind, key, body.slide_index, fmt)
        path.write_bytes(audio_bytes)
        record_generated(kind, key, body.slide_index, path.name)
        return {
            "ok": True,
            "slide_index": body.slide_index,
            "filename": path.name,
            "url": (
                f"/api/audio/workspace/file?kind={kind}&key={quote(key, safe='')}"
                f"&slide_index={body.slide_index}"
            ),
        }

    @application.get("/api/audio/workspace/file")
    def get_workspace_audio_file(
        kind: str = Query(...),
        key: str = Query(...),
        slide_index: int = Query(ge=0, le=499),
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
        path = slide_audio_path(kind, key, slide_index, fmt)
        if not path.is_file():
            raise HTTPException(status_code=404, detail="音频不存在，请先生成")
        media = {
            "mp3": "audio/mpeg",
            "pcm": "audio/pcm",
            "flac": "audio/flac",
        }.get(fmt, "application/octet-stream")
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
