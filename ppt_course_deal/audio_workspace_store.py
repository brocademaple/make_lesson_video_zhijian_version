"""逐字稿与生成音频的磁盘存储（按会话 task_id 或临时 session_id）。"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from ppt_course_deal.task_storage import get_data_root, load_task

logger = logging.getLogger(__name__)


def workspace_root(kind: str, key: str) -> Path:
    root = get_data_root() / "audio_workspace" / kind / key
    root.mkdir(parents=True, exist_ok=True)
    return root


def meta_path(kind: str, key: str) -> Path:
    return workspace_root(kind, key) / "meta.json"


def slide_audio_path(kind: str, key: str, slide_index: int, ext: str) -> Path:
    """旧版单文件命名（每页一条音频）；兼容读取。"""
    safe_ext = re.sub(r"[^a-z0-9]", "", ext.lower()) or "mp3"
    return workspace_root(kind, key) / f"slide-{slide_index:04d}.{safe_ext}"


def segment_storage_key(slide_index: int, segment_index: int) -> str:
    return f"{slide_index}-{segment_index}"


def safe_stub(text: str, max_chars: int = 10) -> str:
    """从文案首部生成文件名安全片段（中英混合）。"""
    if not text or not str(text).strip():
        return "segment"
    s = str(text).strip().replace("\n", " ")
    s = s[:max_chars]
    stub = re.sub(r"\s+", "_", s)
    stub = re.sub(r"[^\w\u4e00-\u9fff_-]", "", stub, flags=re.UNICODE)
    stub = stub.strip("_") or "segment"
    return stub[:40]


def slide_segment_filename(slide_index: int, segment_index: int, text: str, ext: str) -> str:
    safe_ext = re.sub(r"[^a-z0-9]", "", ext.lower()) or "mp3"
    stub = safe_stub(text, 10)
    return (
        f"slide-{slide_index:04d}-seg-{segment_index:03d}-"
        f"Slide{slide_index + 1}_{stub}.{safe_ext}"
    )


def load_meta(kind: str, key: str) -> dict[str, Any]:
    p = meta_path(kind, key)
    if not p.is_file():
        return {"transcripts": [], "audio_format": "mp3"}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        logger.warning("音频工作台 meta 损坏 %s", p)
        return {"transcripts": [], "audio_format": "mp3"}


def infer_slide_count(meta: dict[str, Any], kind: str, key: str) -> int:
    if kind == "task":
        tsc = slide_count_for_task(key)
        if tsc is not None and tsc > 0:
            return int(tsc)
    ts = meta.get("transcripts") or []
    segs = meta.get("transcript_segments") or []
    ts_l = len(ts) if isinstance(ts, list) else 0
    seg_l = len(segs) if isinstance(segs, list) else 0
    return max(ts_l, seg_l, 1)


def normalize_transcript_segments(meta: dict[str, Any], slide_count: int) -> list[list[str]]:
    raw = meta.get("transcript_segments")
    if isinstance(raw, list) and raw:
        out: list[list[str]] = []
        for i in range(slide_count):
            if i < len(raw) and isinstance(raw[i], list):
                segs = [str(x) if x is not None else "" for x in raw[i]]
                out.append(segs if segs else [""])
            else:
                out.append([""])
        return out
    transcripts = list(meta.get("transcripts") or [])
    out = []
    for i in range(slide_count):
        t = transcripts[i] if i < len(transcripts) else ""
        out.append([str(t) if t is not None else ""])
    return out


def save_meta_for_workspace(
    kind: str,
    key: str,
    slide_count: int,
    *,
    transcript_segments: list[list[str]] | None,
    transcripts_flat: list[str] | None,
) -> None:
    """保存逐字稿；可从多段或扁平列表之一推断。"""
    if slide_count < 0:
        slide_count = 0

    if transcript_segments is not None:
        segs: list[list[str]] = [list(row) for row in transcript_segments[:slide_count]]
    elif transcripts_flat is not None:
        tf = list(transcripts_flat)[:slide_count]
        while len(tf) < slide_count:
            tf.append("")
        segs = [[str(x) if x is not None else ""] for x in tf]
    else:
        segs = []

    while len(segs) < slide_count:
        segs.append([""])
    segs = segs[:slide_count]
    for i in range(len(segs)):
        if not segs[i]:
            segs[i] = [""]

    merged_transcripts = ["\n\n".join(s).strip() for s in segs]

    meta = load_meta(kind, key)
    meta["transcript_segments"] = segs
    meta["transcripts"] = merged_transcripts
    p = meta_path(kind, key)
    p.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def save_meta(kind: str, key: str, transcripts: list[str], slide_count: int) -> None:
    """兼容旧调用：每页单段。"""
    save_meta_for_workspace(
        kind,
        key,
        slide_count,
        transcript_segments=None,
        transcripts_flat=transcripts,
    )


def slide_count_for_task(task_id: str) -> int | None:
    data = load_task(task_id)
    if not data:
        return None
    return int(data.get("slide_count") or len(data.get("slides") or []))


def record_generated_segment(
    kind: str,
    key: str,
    slide_index: int,
    segment_index: int,
    filename: str,
) -> None:
    meta = load_meta(kind, key)
    gen = meta.get("generated_files") or {}
    gen[segment_storage_key(slide_index, segment_index)] = filename
    meta["generated_files"] = gen
    meta_path(kind, key).write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def record_generated(kind: str, key: str, slide_index: int, filename: str) -> None:
    """兼容：视为第 0 段。"""
    record_generated_segment(kind, key, slide_index, 0, filename)


def resolve_workspace_audio_path(
    kind: str,
    key: str,
    slide_index: int,
    segment_index: int,
    fmt: str,
) -> Path | None:
    """按 meta.generated_files 或旧版 slide-NNNN.ext 解析已生成文件路径。"""
    meta = load_meta(kind, key)
    gen = meta.get("generated_files") or {}
    if not isinstance(gen, dict):
        gen = {}
    root = workspace_root(kind, key)

    k = segment_storage_key(slide_index, segment_index)
    fn = gen.get(k)
    if isinstance(fn, str) and fn.strip():
        p = root / fn
        if p.is_file():
            return p

    if segment_index == 0:
        sk = str(slide_index)
        fn = gen.get(sk)
        if isinstance(fn, str) and fn.strip():
            p = root / fn
            if p.is_file():
                return p
        legacy = slide_audio_path(kind, key, slide_index, fmt)
        if legacy.is_file():
            return legacy

    return None
