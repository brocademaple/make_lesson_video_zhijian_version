"""口播稿 / TTS / 字幕文案（启发式）；保留金额与关键事实片段。"""

from __future__ import annotations

import re
from typing import Iterable


_FACT_NUMBER_RE = re.compile(
    r"(?:\d[\d,]*\.?\d*\s*(?:元|万块|万|块|%))|"
    r"(?:扣除|罚款|处罚)[^。；;!?？\n]{0,40}",
)
_KEY_PHRASES = (
    "扣除全部绩效",
    "解除劳动合同",
    "解除劳动",
    "全额",
    "全部绩效",
)


def _extract_fact_snippets(raw_text: str) -> list[str]:
    if not (raw_text or "").strip():
        return []
    seen: set[str] = set()
    out: list[str] = []
    for m in _FACT_NUMBER_RE.finditer(raw_text):
        s = m.group(0).strip()
        if len(s) >= 2 and s not in seen:
            seen.add(s)
            out.append(s)
    for kp in _KEY_PHRASES:
        if kp in raw_text and kp not in seen:
            seen.add(kp)
            out.append(kp)
    return out[:12]


def _merge_preserved(raw_text: str, body: str) -> str:
    """确保金额 / 处罚片段出现在输出中。"""
    snippets = _extract_fact_snippets(raw_text)
    if not snippets:
        return body
    merged = body
    missing = [s for s in snippets if s and s not in merged]
    if missing:
        merged = merged.rstrip()
        if merged and not merged.endswith(("。", "！", "？", ".", "!", "?")):
            merged += "。"
        merged += "".join(missing)
    return merged


def _scene_intro(scene_type: str) -> str:
    return {
        "title": "这一页是开场或章节标题，我们先对齐本节要讲什么。",
        "agenda": "这一页是目录或章节结构，帮助大家建立整体脉络。",
        "rule_explanation": "这一页涉及规则边界与后果，请重点关注表述与适用场景。",
        "rule_card": "这一页把规则要点做成卡片化呈现，便于记忆和对照执行。",
        "case_dialogue": "这一页用案例或对话呈现情境，方便理解口径与应对方式。",
        "explanation": "这一页进行要点讲解，把关键信息与上下文串起来。",
    }.get(scene_type, "下面结合本页内容进行讲解。")


def build_narration(raw_text: str, scene_type: str) -> dict[str, str]:
    """
    返回 narration（审核稿）、tts_text（口语化合成）、subtitle_text（字幕精简）。
    """
    raw = (raw_text or "").strip()
    intro = _scene_intro(scene_type)

    if not raw:
        narration = (
            f"{intro}当前页未抽取到正文，建议核对课件或补充备注后再录制。"
        )
        tts = (
            "这一页暂时没有可用的正文内容。"
            "建议你核对原始课件，或者补充演讲者备注之后，再来生成口播。"
        )
        sub = "本页暂无正文，请核对课件或备注。"
        return {"narration": narration, "tts_text": tts, "subtitle_text": sub}

    narration = (
        f"{intro}\n\n"
        f"【页内要点】\n{raw}\n\n"
        "以上为从课件抽取的原文要点，录制时请口语化表达并保持事实一致。"
    )

    # TTS：短句、停顿感（…… / 逗号）
    lines = [ln.strip() for ln in raw.replace("\r", "").split("\n") if ln.strip()]
    if len(lines) <= 1:
        chunks = re.split(r"(?<=[。；;!?？])", raw)
        parts = [c.strip() for c in chunks if c and c.strip()]
    else:
        parts = lines

    spoken_parts: list[str] = []
    for i, p in enumerate(parts[:24]):
        if i == 0:
            spoken_parts.append(f"先看这一段：{p}")
        else:
            spoken_parts.append(p)

    tts_core = "……".join(spoken_parts) if spoken_parts else raw
    if len(tts_core) > 480:
        tts_core = tts_core[:477] + "……"

    tts_text = _merge_preserved(raw, tts_core)

    # subtitle：tts 精简版（取前两句或截断）
    sub_src = tts_text.replace("……", " ").strip()
    if len(sub_src) > 120:
        cut = sub_src[:117].rsplit("，", 1)[0]
        subtitle_text = (cut or sub_src[:117]) + "……"
    else:
        subtitle_text = sub_src

    subtitle_text = _merge_preserved(raw, subtitle_text)

    narration = _merge_preserved(raw, narration)

    return {
        "narration": narration,
        "tts_text": tts_text,
        "subtitle_text": subtitle_text,
    }


def iter_scene_types() -> Iterable[str]:
    return (
        "title",
        "agenda",
        "rule_explanation",
        "rule_card",
        "case_dialogue",
        "explanation",
    )
