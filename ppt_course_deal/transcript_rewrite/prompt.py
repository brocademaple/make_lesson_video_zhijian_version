"""口播稿改写：极简 system + user 消息（内置 minimax_skill.md 与可选课程追加）。"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

_SKILL_FILE = Path(__file__).resolve().parent / "minimax_skill.md"

# 仅占位满足 Chat API 的 system 槽位；全部约束见 user 消息内的 skill。
REWRITE_MINIMAL_SYSTEM = (
    "你是中文录课口播编辑。"
    "用户消息已含完整规范与待优化原文：先按规范改口播正文，再按其中「输出格式」在文末给出 MiniMax 合成参数 JSON；"
    "不要复述规范条文，不要在正文外加与 JSON 无关的说明段落。"
)


@lru_cache
def load_transcript_rewrite_minimax_skill_text() -> str:
    """内置 Markdown 技能正文（打包随附）；作为改写请求的 user 前置段。"""
    raw = _SKILL_FILE.read_text(encoding="utf-8").strip()
    idx = raw.find("【")
    return raw[idx:].strip() if idx >= 0 else raw


def build_user_prompt_with_skill(
    original_text: str,
    extra_instructions: str | None = None,
    *,
    course_transcript_context: str | None = None,
    context_slide_index: int | None = None,
    context_segment_index: int | None = None,
) -> str:
    """user 消息：skill 全文 + 可选「课程追加规则」+ 可选全课语境 + 待优化原文。"""
    skill = load_transcript_rewrite_minimax_skill_text()
    body = (original_text or "").strip()
    extra = (extra_instructions or "").strip()
    ctx = (course_transcript_context or "").strip()

    chunks: list[str] = [
        "下列内容由内置文档 ppt_course_deal/transcript_rewrite/minimax_skill.md 提供。"
        "请按其改写文末「待优化原文」，不要复述规范条文。\n\n",
        skill,
    ]
    if extra:
        chunks.append("\n\n---\n\n【课程追加规则】\n\n")
        chunks.append(extra)
    if ctx:
        chunks.append("\n\n---\n\n【全课逐字稿语境（只读，请勿改写本块）】\n\n")
        if context_slide_index is not None and context_segment_index is not None:
            chunks.append(
                "当前待优化的段落位置：**第 "
                f"{int(context_slide_index) + 1} 页 · 第 {int(context_segment_index) + 1} 段**。"
                "你只能改写下方「【待优化原文】」中的那一段；上文仅为把握全课基调与章节衔接。\n\n"
            )
        chunks.append(ctx)
    chunks.append("\n\n---\n\n【待优化原文】\n\n")
    chunks.append(body)
    return "".join(chunks)


def build_user_prompt(original_text: str) -> str:
    """兼容旧调用；不推荐用于 MiniMax 口播链路。"""
    return (
        "请优化下列口播稿（保持知识点准确）：\n\n"
        + (original_text or "").strip()
    )
