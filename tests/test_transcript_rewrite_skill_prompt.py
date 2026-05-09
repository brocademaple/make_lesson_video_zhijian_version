"""transcript_rewrite/minimax_skill.md 与 user 提示拼装。"""

from ppt_course_deal.transcript_rewrite import (
    build_user_prompt_with_skill,
    load_transcript_rewrite_minimax_skill_text,
)


def test_skill_text_starts_with_output_section() -> None:
    t = load_transcript_rewrite_minimax_skill_text()
    assert t.startswith("【输出格式")
    assert "【场景与语气】" in t
    assert "(laughs)" in t
    assert "<#x#>" in t


def test_user_prompt_wraps_original() -> None:
    u = build_user_prompt_with_skill("  你好  ")
    assert "【待优化原文】" in u
    assert u.endswith("你好")


def test_user_prompt_includes_extra_block() -> None:
    u = build_user_prompt_with_skill("x", extra_instructions="仅本课：少说冷笑话。")
    assert "【课程追加规则】" in u
    assert "少说冷笑话" in u
    assert "【待优化原文】" in u


def test_user_prompt_includes_course_context_and_position() -> None:
    u = build_user_prompt_with_skill(
        "本段待改",
        course_transcript_context="【第 1 页】\n段 1：严肃开场",
        context_slide_index=2,
        context_segment_index=0,
    )
    assert "【全课逐字稿语境（只读，请勿改写本块）】" in u
    assert "第 3 页 · 第 1 段" in u
    assert "严肃开场" in u
    assert "【待优化原文】" in u
    assert u.endswith("本段待改")
