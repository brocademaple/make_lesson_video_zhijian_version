"""transcript_rewrite.sanitize：MiniMax T2A 白名单清理。"""

from ppt_course_deal.transcript_rewrite import sanitize_for_minimax_t2a


def test_removes_unknown_paren_tags():
    text = "你好(foo)，停顿<#1.5#>结束(bad)"
    out, w = sanitize_for_minimax_t2a(text)
    assert "(bad)" not in out
    assert "(foo)" not in out
    assert "<#1.5#>" in out
    assert len(w) >= 2


def test_keeps_whitelisted_interjection():
    text = "好吧(sighs)，我们继续。"
    out, w = sanitize_for_minimax_t2a(text)
    assert "(sighs)" in out
    assert not w


def test_pause_range():
    text = "a<#0.005#>b<#50#>c"
    out, w = sanitize_for_minimax_t2a(text)
    assert "<#0.005#>" not in out
    assert "<#50#>" in out
    assert len(w) >= 1
