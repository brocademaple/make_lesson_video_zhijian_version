from __future__ import annotations

from ppt_course_deal.models import BlockKind, CourseSlidePlan, SourceSlide

_SECTION_LABELS: dict[BlockKind, str] = {
    BlockKind.RULE: "规则要点",
    BlockKind.CASE: "案例研讨",
    BlockKind.PENALTY: "处罚与后果",
    BlockKind.INTERACTION: "课堂互动",
    BlockKind.SUMMARY: "本节小结",
    BlockKind.NARRATION: "讲解提要",
    BlockKind.TITLE: "标题",
}

_ORDER: tuple[BlockKind, ...] = (
    BlockKind.RULE,
    BlockKind.CASE,
    BlockKind.PENALTY,
    BlockKind.INTERACTION,
    BlockKind.SUMMARY,
    BlockKind.NARRATION,
)

# 单页字符上限（含标点）；超出则拆页
_MAX_CHARS_PER_SLIDE = 2200


def _aggregate_sections(blocks: list[ContentBlock]) -> dict[BlockKind, str]:
    agg: dict[BlockKind, list[str]] = {k: [] for k in BlockKind if k != BlockKind.TITLE}
    for b in blocks:
        if b.kind == BlockKind.TITLE:
            continue
        agg.setdefault(b.kind, []).append(b.text.strip())
    out: dict[BlockKind, str] = {}
    for k, parts in agg.items():
        text = "\n".join(p for p in parts if p).strip()
        if text:
            out[k] = text
    return out


def _split_text_chunk(text: str, limit: int) -> tuple[str, str]:
    if len(text) <= limit:
        return text, ""
    # 按换行优先截断
    head = text[:limit]
    nl = head.rfind("\n")
    if nl > limit * 0.6:
        head = head[:nl].rstrip()
        rest = text[len(head) :].lstrip()
        return head, rest
    return head.rstrip(), text[len(head) :].lstrip()


def plan_course_slides(src: SourceSlide) -> list[CourseSlidePlan]:
    """将单页源幻灯片规划为 1..n 页课程幻灯片。"""
    agg = _aggregate_sections(src.blocks)
    base_title = src.title.strip() or "本节内容"

    # 展平为有序片段列表：(label_key, text)
    pieces: list[tuple[str, str]] = []
    for kind in _ORDER:
        if kind not in agg:
            continue
        label = _SECTION_LABELS[kind]
        pieces.append((label, agg[kind]))

    if not pieces:
        # 全是空白时仍输出一页承载原始摘要
        body = src.raw_text.strip()[:_MAX_CHARS_PER_SLIDE]
        plan = CourseSlidePlan(
            source_slide_index=src.index,
            segment_label=None,
            slide_title=base_title,
            sections={"讲解提要": body or "（本页无正文）"},
            notes=src.raw_text[:8000] if src.raw_text else None,
        )
        return [plan]

    slides: list[CourseSlidePlan] = []
    buf_sections: dict[str, str] = {}

    def body_chars() -> int:
        return sum(len(t) for t in buf_sections.values())

    def flush() -> None:
        nonlocal buf_sections
        if not buf_sections:
            return
        slides.append(
            CourseSlidePlan(
                source_slide_index=src.index,
                segment_label=None,
                slide_title=base_title,
                sections=dict(buf_sections),
                notes=src.raw_text[:8000] if src.raw_text else None,
            )
        )
        buf_sections = {}

    for sec_label, text in pieces:
        remaining = text
        while remaining:
            room = _MAX_CHARS_PER_SLIDE - body_chars()
            if room < 180 and buf_sections:
                flush()
                room = _MAX_CHARS_PER_SLIDE - body_chars()
            chunk, remaining = _split_text_chunk(remaining, max(200, room))
            if len(chunk) > _MAX_CHARS_PER_SLIDE:
                chunk, remaining = _split_text_chunk(chunk, _MAX_CHARS_PER_SLIDE)

            if sec_label in buf_sections:
                buf_sections[sec_label] = buf_sections[sec_label] + "\n" + chunk
            else:
                buf_sections[sec_label] = chunk

            if body_chars() >= _MAX_CHARS_PER_SLIDE:
                flush()

    flush()

    # 续页标题标注
    if len(slides) > 1:
        for i, s in enumerate(slides):
            s.slide_title = (
                base_title if i == 0 else f"{base_title}（续 {i + 1}/{len(slides)}）"
            )
    return slides
