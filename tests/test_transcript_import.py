"""逐字稿整稿解析单元测试（unittest，无需 pytest）。"""

import unittest

from ppt_course_deal.transcript_import import (
    build_proposed_segments,
    filter_blocks_for_slide_count,
    find_conflicts,
    merge_with_resolutions,
    merged_text_per_slide,
    parse_slide_blocks,
    prepare_import,
)


class TestParseSlideBlocks(unittest.TestCase):
    def test_basic_pages(self) -> None:
        text = """### 第1页
甲
### 第2页
乙
"""
        d, w = parse_slide_blocks(text)
        self.assertEqual(d[0], "甲")
        self.assertEqual(d[1], "乙")
        self.assertEqual(w, [])

    def test_typo_colon_page(self) -> None:
        text = "### 第:28页\n正文28\n"
        d, _ = parse_slide_blocks(text)
        self.assertEqual(d[27], "正文28")

    def test_duplicate_page_last_wins(self) -> None:
        text = """### 第1页
first
### 第1页
second
"""
        d, w = parse_slide_blocks(text)
        self.assertEqual(d[0], "second")
        self.assertTrue(any("多次" in x for x in w))


class TestPrepareImport(unittest.TestCase):
    def test_conflict_when_existing_differs(self) -> None:
        existing = [["旧内容"], [""]]
        text = "### 第1页\n新内容\n"
        r = prepare_import(text, 2, existing)
        self.assertEqual(len(r["conflicts"]), 1)
        self.assertEqual(r["conflicts"][0]["slide_index"], 0)

    def test_no_conflict_when_empty_existing(self) -> None:
        existing = [[""], [""]]
        text = "### 第1页\n新\n"
        r = prepare_import(text, 2, existing)
        self.assertEqual(r["conflicts"], [])

    def test_merge_keep(self) -> None:
        existing = [["保留"], [""]]
        text = "### 第1页\n覆盖\n"
        prep = prepare_import(text, 2, existing)
        proposed = prep["proposed_transcript_segments"]
        ci = {c["slide_index"] for c in prep["conflicts"]}
        res = {"0": "keep"}
        out = merge_with_resolutions(existing, proposed, ci, res, 2)
        self.assertEqual(out[0], ["保留"])
        self.assertEqual(out[1], [""])


if __name__ == "__main__":
    unittest.main()
