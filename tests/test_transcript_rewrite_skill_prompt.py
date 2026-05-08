"""transcript_rewrite/minimax_skill.md 与 user 提示拼装。"""

from ppt_course_deal.transcript_rewrite import (
    build_user_prompt_with_skill,
    load_transcript_rewrite_minimax_skill_text,
)


def test_skill_text_starts_with_scene_section() -> None:
    t = load_transcript_rewrite_minimax_skill_text()
    assert t.startswith("【场景与语气】")
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
