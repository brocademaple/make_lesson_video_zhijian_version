"""deal ↔ rebuilder：原始素材清单与导演脚本流水线最小验收。"""

from __future__ import annotations

import json
from pathlib import Path

from ppt_course_rebuilder.asset_tagger import tag_assets
from ppt_course_rebuilder.director import rebuild_course_from_raw_manifest
from ppt_course_rebuilder.narration import build_narration
from ppt_course_rebuilder.review import export_approved_manifest, reject_scene
from ppt_course_rebuilder.subtitle import split_subtitle_segments


class _FakeDirectorLLM:
    available = True

    def call_json(self, **_kwargs):
        return {
            "course": {
                "title": "质检规则训练",
                "audience": "电销新人",
                "goal": "理解红线规则并能准确执行",
            },
            "scenes": [
                {
                    "source_slide_ids": ["slide-0000"],
                    "scene_type": "rule_explanation",
                    "title": "信息安全红线",
                    "learning_goal": "理解信息安全违规边界",
                    "onscreen_text": "用户信息不得用于非工作目的",
                    "bullets": ["不得获利", "不得私下交易", "不得走非官方渠道"],
                    "tts_text": "这一页重点讲信息安全红线。用户信息不得用于非工作目的，违规会触发处罚。",
                    "subtitle_text": "信息安全红线：用户信息不得用于非工作目的。",
                    "screen_design": {
                        "layout": "rule_card",
                        "visual_strategy": "整页图作背景，叠加三条规则卡片",
                        "emphasis": ["信息安全", "红线"],
                    },
                    "risk_flags": ["compliance_sensitive"],
                }
            ],
        }


class _UnavailableDirectorLLM:
    available = False


class _EmptyDirectorLLM:
    available = True

    def call_json(self, **_kwargs):
        return {"course": {"title": "空结果"}, "scenes": []}


def test_tag_assets_unknown_safe(tmp_path: Path) -> None:
    raw = {
        "task_id": "x",
        "task_root": str(tmp_path),
        "slides": [
            {
                "slide_id": "slide-0000",
                "full_page_png": "previews/slide-0000/full.png",
                "shapes": [{"shape_id": "a", "image_path": "previews/slide-0000/shapes/shape-0000.bin"}],
            }
        ],
    }
    assets = tag_assets(raw)
    assert len(assets) >= 1
    types = {a["asset_type"] for a in assets}
    assert "unknown" in types or "decoration" in types or "full_slide" in types


def test_rebuild_produces_scenes_with_narration_and_subtitles(tmp_path: Path) -> None:
    raw_path = tmp_path / "raw_material_manifest.json"
    raw_path.write_text(
        json.dumps(
            {
                "task_id": "test-task",
                "source_pptx": "source.pptx",
                "task_root": str(tmp_path),
                "slides": [
                    {
                        "slide_id": "slide-0000",
                        "slide_index": 0,
                        "full_page_png": None,
                        "raw_text": "第一章\n总则",
                        "speaker_notes": None,
                        "shapes": [],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    out_path = tmp_path / "director_manifest.json"
    dm = rebuild_course_from_raw_manifest(
        str(raw_path), str(out_path), options={"use_llm": False}
    )
    assert dm["task_id"] == "test-task"
    scenes = dm["scenes"]
    assert len(scenes) == 1
    sc = scenes[0]
    assert sc.get("narration")
    assert sc.get("tts_text")
    segs = (sc.get("subtitle") or {}).get("segments") or []
    assert len(segs) >= 1
    assert all("start_sec" in s and "end_sec" in s and "text" in s for s in segs)
    assert sc["scene_role"] == "intro"
    assert sc["render_engine"] in {"hyperframes_creative", "remotion_stable"}
    assert sc["creative_brief"]["title"] == sc["title"]
    assert sc["fallback_engine"] in {"", "remotion_stable"}


def test_rebuild_can_use_llm_director_output(tmp_path: Path) -> None:
    raw_path = tmp_path / "raw_material_manifest.json"
    raw_path.write_text(
        json.dumps(
            {
                "task_id": "test-task",
                "source_pptx": "source.pptx",
                "task_root": str(tmp_path),
                "slides": [
                    {
                        "slide_id": "slide-0000",
                        "slide_index": 0,
                        "full_page_png": "previews/slide-0000/full.png",
                        "raw_text": "信息安全\n用户信息不得用于非工作目的，违规将处罚。",
                        "speaker_notes": None,
                        "shapes": [],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    out_path = tmp_path / "director_manifest.json"
    dm = rebuild_course_from_raw_manifest(
        str(raw_path),
        str(out_path),
        options={"use_llm": True, "llm_client": _FakeDirectorLLM()},
    )

    assert dm["generation"]["planning_mode"] == "llm_director_v0"
    assert dm["course"]["title"] == "质检规则训练"
    scene = dm["scenes"][0]
    assert scene["scene_type"] == "rule_explanation"
    assert scene["content"]["bullets"] == ["不得获利", "不得私下交易", "不得走非官方渠道"]
    assert scene["screen_design"]["layout"] == "rule_card"
    assert scene["tts_text"]
    assert scene["subtitle"]["segments"]
    assert scene["scene_role"] == "intro"
    assert scene["render_engine"] == "remotion_stable"
    assert scene["creative_brief"]["engine"] == "remotion"


def test_rebuild_falls_back_when_llm_unavailable(tmp_path: Path) -> None:
    raw_path = tmp_path / "raw_material_manifest.json"
    raw_path.write_text(
        json.dumps(
            {
                "task_id": "test-task",
                "source_pptx": "source.pptx",
                "task_root": str(tmp_path),
                "slides": [
                    {
                        "slide_id": "slide-0000",
                        "slide_index": 0,
                        "full_page_png": None,
                        "raw_text": "总则\n本页用于回退测试。",
                        "speaker_notes": None,
                        "shapes": [],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    out_path = tmp_path / "director_manifest.json"
    dm = rebuild_course_from_raw_manifest(
        str(raw_path),
        str(out_path),
        options={"use_llm": True, "llm_client": _UnavailableDirectorLLM()},
    )

    assert dm["generation"]["planning_mode"] == "heuristic_v1"
    assert "未配置可用 LLM client" in dm["generation"]["llm_error"]
    assert dm["scenes"]


def test_rebuild_falls_back_when_llm_returns_no_scenes(tmp_path: Path) -> None:
    raw_path = tmp_path / "raw_material_manifest.json"
    raw_path.write_text(
        json.dumps(
            {
                "task_id": "test-task",
                "source_pptx": "source.pptx",
                "task_root": str(tmp_path),
                "slides": [
                    {
                        "slide_id": "slide-0000",
                        "slide_index": 0,
                        "full_page_png": None,
                        "raw_text": "总则\n本页用于空结果回退测试。",
                        "speaker_notes": None,
                        "shapes": [],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    out_path = tmp_path / "director_manifest.json"
    dm = rebuild_course_from_raw_manifest(
        str(raw_path),
        str(out_path),
        options={"use_llm": True, "llm_client": _EmptyDirectorLLM()},
    )

    assert dm["generation"]["planning_mode"] == "heuristic_v1"
    assert "LLM director 输出缺少 scenes" in dm["generation"]["llm_error"]
    assert dm["scenes"]


def test_penalty_amount_preserved_in_outputs() -> None:
    raw = (
        "红线问题：影响品牌形象；罚款5000元，严重者解除劳动合同。"
    )
    out = build_narration(raw, "rule_explanation")
    assert "5000" in out["tts_text"] or "5000元" in out["tts_text"]
    assert "5000" in out["subtitle_text"] or "5000元" in out["subtitle_text"]


def test_split_subtitle_segments_basic() -> None:
    segs = split_subtitle_segments("第一句。第二句！", 10.0)
    assert len(segs) >= 1
    assert abs(segs[-1]["end_sec"] - 10.0) < 0.02


def test_export_excludes_rejected(tmp_path: Path) -> None:
    dm_path = tmp_path / "director_manifest.json"
    dm_path.write_text(
        json.dumps(
            {
                "task_id": "t1",
                "course": {},
                "assets": [],
                "scenes": [
                    {
                        "scene_id": "sc-a",
                        "scene_type": "explanation",
                        "review_status": "approved",
                    },
                    {
                        "scene_id": "sc-b",
                        "scene_type": "explanation",
                        "review_status": "rejected",
                        "reject_reason": "bad",
                    },
                ],
                "review": {},
                "generated_at": "",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    out_path = tmp_path / "approved.json"
    export_approved_manifest(str(dm_path), str(out_path))
    exp = json.loads(out_path.read_text(encoding="utf-8"))
    ids = {s["scene_id"] for s in exp["scenes"]}
    assert ids == {"sc-a"}
    rej = exp.get("rejected_items") or []
    assert len(rej) == 1 and rej[0].get("scene_id") == "sc-b"


def test_reject_scene_updates_file(tmp_path: Path) -> None:
    dm_path = tmp_path / "director_manifest.json"
    dm_path.write_text(
        json.dumps(
            {
                "task_id": "t1",
                "course": {},
                "assets": [],
                "scenes": [
                    {"scene_id": "s1", "review_status": "pending"},
                ],
                "review": {"pending_count": 1, "approved_count": 0, "rejected_count": 0},
                "generated_at": "",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    reject_scene(str(dm_path), "s1", "nope")
    data = json.loads(dm_path.read_text(encoding="utf-8"))
    assert data["scenes"][0]["review_status"] == "rejected"
    assert data["scenes"][0]["reject_reason"] == "nope"
