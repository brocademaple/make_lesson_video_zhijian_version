"""整稿逐字稿解析：按「### 第 N 页」分页，第 1 页对应幻灯片 index 0。"""

from __future__ import annotations

import re
from typing import Any

# 约 2.5M 字符上限（与 Web 上传体量区分，避免单次超大 JSON）
MAX_SCRIPT_CHARS = 2_500_000

# 行首 ### / ## / # 或全角 ＃；兼容「### 第:28页」笔误
HEADER_LINE_RE = re.compile(
    r"^\s*(?:#{1,3}|＃{1,3})\s*第\s*:?\s*(\d+)\s*页\s*$",
    re.MULTILINE,
)


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def parse_slide_blocks(text: str) -> tuple[dict[int, str], list[str]]:
    """
    解析全文，得到 slide_index -> 该页正文（不含标题行）。
    同一页出现多次时保留最后一次。
    """
    warnings: list[str] = []
    raw = normalize_newlines(text)
    if len(raw) > MAX_SCRIPT_CHARS:
        raise ValueError(
            f"文稿过长（上限 {MAX_SCRIPT_CHARS // 1_000_000}M 字符量级），请删减后重试",
        )

    matches = list(HEADER_LINE_RE.finditer(raw))
    if not matches:
        raise ValueError(
            "未识别到分页标题。请在每页开头使用「### 第 N 页」（N 为正整数），"
            "例如「### 第 1 页」对应左侧第 1 张幻灯片。",
        )

    slide_to_body: dict[int, str] = {}
    for i, m in enumerate(matches):
        page_one = int(m.group(1))
        slide_idx = page_one - 1
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        body = raw[start:end].strip()
        if slide_idx in slide_to_body:
            warnings.append(f"文稿中「第 {page_one} 页」出现多次，已保留最后一次内容")
        slide_to_body[slide_idx] = body

    return slide_to_body, warnings


def filter_blocks_for_slide_count(
    slide_to_body: dict[int, str],
    slide_count: int,
) -> tuple[dict[int, str], list[str]]:
    warnings: list[str] = []
    out: dict[int, str] = {}
    for idx, body in slide_to_body.items():
        if idx < 0:
            warnings.append(f"已忽略无效页码（第 {idx + 1} 页）")
            continue
        if idx >= slide_count:
            warnings.append(
                f"已忽略超出课件页数的「第 {idx + 1} 页」（当前课件共 {slide_count} 页）",
            )
            continue
        out[idx] = body
    return out, warnings


def build_proposed_segments(
    slide_count: int,
    slide_to_body: dict[int, str],
) -> list[list[str]]:
    """每页默认单段；文稿未给出的页为空字符串。"""
    segs: list[list[str]] = []
    for i in range(slide_count):
        if i not in slide_to_body:
            segs.append([""])
            continue
        body = slide_to_body[i].strip()
        segs.append([body] if body else [""])
    return segs


def merged_text_per_slide(transcript_segments: list[list[str]]) -> list[str]:
    out: list[str] = []
    for row in transcript_segments:
        if not row:
            out.append("")
            continue
        out.append("\n\n".join(str(x) if x is not None else "" for x in row).strip())
    return out


def find_conflicts(
    existing_merged: list[str],
    proposed_merged: list[str],
    slide_count: int,
) -> list[dict[str, Any]]:
    """已有非空且与导入稿不一致（含导入为空将清空）时视为冲突。"""
    conflicts: list[dict[str, Any]] = []
    for i in range(slide_count):
        ex = existing_merged[i] if i < len(existing_merged) else ""
        pr = proposed_merged[i] if i < len(proposed_merged) else ""
        if ex and pr != ex:
            conflicts.append(
                {
                    "slide_index": i,
                    "slide_page_number": i + 1,
                    "existing_preview": ex[:900],
                    "imported_preview": pr[:900],
                },
            )
    return conflicts


def merge_with_resolutions(
    existing_segments: list[list[str]],
    proposed_segments: list[list[str]],
    conflict_indices: set[int],
    resolutions: dict[str, str],
    slide_count: int,
) -> list[list[str]]:
    """对冲突页按 resolutions（\"import\" | \"keep\"）合并；非冲突页一律采用导入稿。"""
    out: list[list[str]] = []
    for i in range(slide_count):
        pr_rows = proposed_segments[i] if i < len(proposed_segments) else [""]
        ex_rows = existing_segments[i] if i < len(existing_segments) else [""]

        if i not in conflict_indices:
            out.append([str(x) for x in pr_rows] if pr_rows else [""])
            continue

        choice = resolutions.get(str(i))
        if choice == "keep":
            row = [str(x) if x is not None else "" for x in ex_rows] if ex_rows else [""]
            if not row:
                row = [""]
            out.append(row)
        elif choice == "import":
            out.append([str(x) for x in pr_rows] if pr_rows else [""])
        else:
            raise ValueError(f"第 {i + 1} 页缺少有效的覆盖选择（import / keep）")
    return out


def prepare_import(
    text: str,
    slide_count: int,
    existing_segments: list[list[str]],
) -> dict[str, Any]:
    """
    解析文稿并计算建议稿与冲突列表（不写盘）。
    """
    slide_to_body, w1 = parse_slide_blocks(text)
    filtered, w2 = filter_blocks_for_slide_count(slide_to_body, slide_count)
    warnings = w1 + w2

    proposed = build_proposed_segments(slide_count, filtered)
    ex_merged = merged_text_per_slide(existing_segments)
    pr_merged = merged_text_per_slide(proposed)
    while len(ex_merged) < slide_count:
        ex_merged.append("")
    while len(pr_merged) < slide_count:
        pr_merged.append("")

    conflicts = find_conflicts(ex_merged, pr_merged, slide_count)
    filled_slides = sum(1 for i in range(slide_count) if pr_merged[i].strip())

    return {
        "warnings": warnings,
        "slide_count": slide_count,
        "filled_slides": filled_slides,
        "conflicts": conflicts,
        "proposed_transcript_segments": proposed,
    }
