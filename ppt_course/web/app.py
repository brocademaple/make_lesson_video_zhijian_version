from __future__ import annotations

import logging
import shutil
import tempfile
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.background import BackgroundTask

from ppt_course.deck_sessions import create_session, get_session
from ppt_course.extract import parse_pptx_bytes
from ppt_course.fallback_preview import write_fallback_pngs
from ppt_course.pipeline import transform_pptx
from ppt_course.slide_render import render_pptx_to_pngs
from ppt_course.task_storage import (
    delete_task,
    list_task_summaries,
    load_task,
    preview_png_path,
    save_task_from_parse,
)

logger = logging.getLogger(__name__)

STATIC_ROOT = Path(__file__).resolve().parent.parent / "static"

MAX_UPLOAD_BYTES = 50 * 1024 * 1024


def create_app() -> FastAPI:
    application = FastAPI(
        title="PPT 课程化重构",
        description="上传原始培训 PPTX，解析预览后生成适合录课的结构化 PPTX（MVP）",
        version="0.1.0",
    )

    @application.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.post("/api/parse")
    async def parse_api(file: UploadFile = File(...)) -> dict:
        """解析整份 PPTX；若本机具备 LibreOffice + Poppler，则生成逐页 PNG 供预览。"""
        if not file.filename or not file.filename.lower().endswith(".pptx"):
            raise HTTPException(status_code=400, detail="请上传 .pptx 文件")
        raw = await file.read()
        if len(raw) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"文件过大（上限 {MAX_UPLOAD_BYTES // (1024 * 1024)} MB）",
            )
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

        session_id: str | None = None
        images_available = False
        images_error: str | None = None
        preview_count = 0
        preview_source: str = "libreoffice"
        task_persisted: str | None = None

        work = Path(tempfile.mkdtemp(prefix="deck_preview_"))
        pngs: list[Path] = []
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
    def list_tasks_api() -> dict[str, list[dict[str, object]]]:
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
    def delete_task_api(task_id: str) -> dict[str, bool]:
        ok = delete_task(task_id)
        if not ok:
            raise HTTPException(status_code=404, detail="任务不存在")
        return {"ok": True}

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

        raw = await file.read()
        if len(raw) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"文件过大（上限 {MAX_UPLOAD_BYTES // (1024 * 1024)} MB）",
            )

        stem = Path(file.filename).stem
        tmpdir = tempfile.mkdtemp(prefix="ppt_course_")
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
