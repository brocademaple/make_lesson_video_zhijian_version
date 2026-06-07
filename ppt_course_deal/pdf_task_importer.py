"""Import a PDF as a stored course task with rendered page previews."""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from ppt_course_deal.raw_material_manifest import build_raw_material_manifest
from ppt_course_deal.task_storage import tasks_dir
from ppt_course_rebuilder.director import rebuild_course_from_raw_manifest
from ppt_course_rebuilder.material_normalizer import build_course_material
from ppt_course_rebuilder.render_adapter import write_render_plan_from_task


def import_pdf_task(
    pdf_path: str | Path,
    *,
    display_name: str | None = None,
    max_pages: int | None = 16,
    video_profile_id: str = "onboarding",
    build_director: bool = True,
    build_render_plan: bool = True,
) -> dict[str, Any]:
    src = Path(pdf_path).expanduser().resolve()
    if not src.is_file():
        raise FileNotFoundError(f"PDF 不存在：{src}")
    if src.suffix.lower() != ".pdf":
        raise ValueError("仅支持 .pdf 文件")

    pdftoppm = shutil.which("pdftoppm")
    pdftotext = shutil.which("pdftotext")
    if not pdftoppm:
        raise RuntimeError("缺少 pdftoppm，无法把 PDF 渲染为整页预览图")
    if not pdftotext:
        raise RuntimeError("缺少 pdftotext，无法抽取 PDF 文本")

    task_id = str(uuid4())
    root = tasks_dir() / task_id
    root.mkdir(parents=True, exist_ok=False)
    try:
        source_name = src.name
        shutil.copy2(src, root / "source.pdf")
        pages = _render_pdf_pages(src, root, pdftoppm=pdftoppm, max_pages=max_pages)
        slides = [
            _slide_meta_from_pdf_page(
                src,
                page_number=i + 1,
                slide_index=i,
                pdftotext=pdftotext,
            )
            for i in range(len(pages))
        ]
        created = datetime.now(timezone.utc).isoformat()
        meta = {
            "id": task_id,
            "filename": display_name or source_name,
            "source_filename": source_name,
            "source_type": "pdf",
            "created_at": created,
            "slide_count": len(slides),
            "slides": slides,
            "preview_source": "pdf",
            "images_error": "",
            "images_available": bool(pages),
            "preview_count": len(pages),
            "shape_image_manifest": [],
            "video_profile": {"id": video_profile_id, "source": "pdf_import"},
        }
        (root / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

        raw = build_raw_material_manifest(task_id)
        raw["source_pptx"] = "source.pdf"
        raw["source_type"] = "pdf"
        raw["video_profile"] = meta["video_profile"]
        (root / "raw_material_manifest.json").write_text(
            json.dumps(raw, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        build_course_material(root / "raw_material_manifest.json", root / "course_material.json", use_llm=False)
        if build_director:
            rebuild_course_from_raw_manifest(
                str(root / "raw_material_manifest.json"),
                str(root / "director_manifest.json"),
                options={"use_llm": False},
            )
        render_plan = None
        if build_render_plan and build_director:
            render_plan = write_render_plan_from_task(task_id, fps=30, no_audio_frames=120)
        return {
            "ok": True,
            "task_id": task_id,
            "task_root": str(root),
            "filename": meta["filename"],
            "slide_count": len(slides),
            "render_plan_path": render_plan.get("render_plan_path") if isinstance(render_plan, dict) else "",
        }
    except Exception:
        shutil.rmtree(root, ignore_errors=True)
        raise


def _render_pdf_pages(src: Path, root: Path, *, pdftoppm: str, max_pages: int | None) -> list[Path]:
    previews = root / "previews"
    previews.mkdir(parents=True, exist_ok=True)
    out_prefix = root / "_pdf_page"
    cmd = [pdftoppm, "-png", "-r", "144"]
    if max_pages and max_pages > 0:
        cmd.extend(["-f", "1", "-l", str(max_pages)])
    cmd.extend([str(src), str(out_prefix)])
    subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=180)
    pages = sorted(root.glob("_pdf_page-*.png"))
    out: list[Path] = []
    for i, page in enumerate(pages):
        dest_dir = previews / f"slide-{i:04d}"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / "full.png"
        shutil.move(str(page), dest)
        out.append(dest)
    return out


def _slide_meta_from_pdf_page(src: Path, *, page_number: int, slide_index: int, pdftotext: str) -> dict[str, Any]:
    text = ""
    try:
        proc = subprocess.run(
            [pdftotext, "-f", str(page_number), "-l", str(page_number), "-layout", str(src), "-"],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        text = _clean_pdf_text(proc.stdout)
    except Exception:
        text = ""
    title = _first_nonempty_line(text) or f"PDF 第 {page_number} 页"
    return {
        "index": slide_index,
        "slide_index": slide_index,
        "slide_id": f"slide-{slide_index:04d}",
        "title": title[:120],
        "text": text,
        "text_blocks": [line for line in text.splitlines() if line.strip()],
        "speaker_notes": "",
    }


def _clean_pdf_text(raw: str) -> str:
    lines = [line.rstrip() for line in (raw or "").splitlines()]
    compact: list[str] = []
    blank = False
    for line in lines:
        if not line.strip():
            if not blank:
                compact.append("")
            blank = True
            continue
        compact.append(line)
        blank = False
    return "\n".join(compact).strip()


def _first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        s = " ".join(line.split())
        if s:
            return s
    return ""
