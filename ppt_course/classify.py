from __future__ import annotations

import re
from typing import Iterable

from ppt_course.models import BlockKind, ContentBlock

# 启发式关键词（可后续替换为 LLM / Skill）
_KEYWORDS: dict[BlockKind, tuple[str, ...]] = {
    BlockKind.RULE: (
        "规则",
        "要点",
        "条款",
        "禁止",
        "应当",
        "必须",
        "不得",
        "注意",
        "规定",
        "依据",
        "法律",
        "制度",
        "规范",
        "要求",
    ),
    BlockKind.CASE: (
        "案例",
        "举例",
        "场景",
        "假设",
        "例如",
        "譬如",
        "比如",
        "从前",
        "某单位",
        "某公司",
    ),
    BlockKind.PENALTY: (
        "处罚",
        "罚款",
        "违规",
        "违纪",
        "后果",
        "责任",
        "吊销",
        "拘留",
        "处分",
        "警告",
    ),
    BlockKind.INTERACTION: (
        "互动",
        "练习",
        "判断",
        "选择",
        "问答",
        "讨论",
        "想一想",
        "测试",
        "填空",
        "投票",
        "问卷",
    ),
    BlockKind.SUMMARY: (
        "总结",
        "小结",
        "本章",
        "回顾",
        "核心",
        "归纳",
        "收尾",
        "综上所述",
    ),
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", "", text)


def _score_line(kind: BlockKind, line: str) -> int:
    n = _normalize(line)
    score = 0
    for kw in _KEYWORDS.get(kind, ()):
        if kw in line or kw in n:
            score += 2
    if kind == BlockKind.RULE and re.search(r"^[一二三四五六七八九十]+[、．.]", line.strip()):
        score += 1
    if kind == BlockKind.INTERACTION and re.search(r"[?？]$", line.strip()):
        score += 1
    return score


def _best_kind(line: str) -> BlockKind:
    stripped = line.strip()
    if len(stripped) <= 18 and not stripped.endswith(("。", "；", "）")):
        # 短行更像标题，但仍可能是列表项，保守当作叙述
        pass

    scores: list[tuple[int, BlockKind]] = []
    for kind in (
        BlockKind.SUMMARY,
        BlockKind.INTERACTION,
        BlockKind.PENALTY,
        BlockKind.CASE,
        BlockKind.RULE,
    ):
        s = _score_line(kind, line)
        if s > 0:
            scores.append((s, kind))
    if scores:
        scores.sort(key=lambda x: (-x[0], x[1].value))
        return scores[0][1]
    return BlockKind.NARRATION


def split_paragraphs(text: str) -> list[str]:
    """按空行分段；若无空行则按句号粗分长段。"""
    text = text.strip()
    if not text:
        return []
    parts = re.split(r"\n\s*\n+", text)
    out: list[str] = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if len(p) > 400 and "\n" not in p:
            # 单段过长：按中文句号切分
            subs = re.split(r"(?<=[。！？])", p)
            buf = ""
            for s in subs:
                s = s.strip()
                if not s:
                    continue
                buf += s
                if len(buf) >= 120:
                    out.append(buf)
                    buf = ""
            if buf:
                out.append(buf)
        else:
            out.append(p)
    return out


def classify_paragraphs(paragraphs: Iterable[str]) -> list[ContentBlock]:
    blocks: list[ContentBlock] = []
    for para in paragraphs:
        lines = [ln.strip() for ln in para.split("\n") if ln.strip()]
        if not lines:
            continue
        # 段内逐行分类并合并同类
        current_kind = _best_kind(lines[0])
        buf = [lines[0]]
        for ln in lines[1:]:
            k = _best_kind(ln)
            if k == current_kind:
                buf.append(ln)
            else:
                blocks.append(ContentBlock(kind=current_kind, text="\n".join(buf)))
                current_kind = k
                buf = [ln]
        blocks.append(ContentBlock(kind=current_kind, text="\n".join(buf)))
    return _merge_adjacent(blocks)


def _merge_adjacent(blocks: list[ContentBlock]) -> list[ContentBlock]:
    if not blocks:
        return []
    merged: list[ContentBlock] = []
    for b in blocks:
        if merged and merged[-1].kind == b.kind:
            merged[-1] = ContentBlock(
                kind=b.kind, text=merged[-1].text + "\n" + b.text
            )
        else:
            merged.append(b)
    return merged


def classify_slide_text(raw_text: str) -> list[ContentBlock]:
    return classify_paragraphs(split_paragraphs(raw_text))
