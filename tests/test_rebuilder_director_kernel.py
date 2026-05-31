from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppt_course_deal import external_settings
from ppt_course_rebuilder.director_validator import validate_director_manifest
from ppt_course_rebuilder.material_normalizer import build_course_material
from ppt_course_rebuilder.render_adapter import write_render_plan_from_task


def test_director_llm_settings_are_independent(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(external_settings, "get_data_root", lambda: tmp_path)

    raw = external_settings.load_raw()
    assert raw["director_llm"]["provider"] == "mimo"
    assert raw["director_llm"]["model"] == "mimo-v2.5-pro"
    assert raw["transcript_rewrite"]["model"] != raw["director_llm"]["model"]

    merged = external_settings.merge_director_llm_update(
        raw["director_llm"],
        {"enabled": True, "api_key": "Bearer tp-abc123", "model": "mimo-v2.5-pro"},
    )
    assert merged["enabled"] is True
    assert merged["api_key"] == "tp-abc123"


def test_tts_settings_default_to_edge_fallback(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(external_settings, "get_data_root", lambda: tmp_path)

    raw = external_settings.load_raw()

    assert raw["tts"]["provider"] == "edge_tts"
    assert raw["tts"]["fallback_enabled"] is True
    assert raw["tts"]["fallback_provider"] == "edge_tts"
    assert raw["tts"]["edge_tts"]["voice"] == "zh-CN-XiaoxiaoNeural"

    merged = external_settings.merge_tts_update(
        raw["tts"],
        {"provider": "edge_tts", "edge_tts": {"rate": "+8%"}},
    )
    assert merged["provider"] == "edge_tts"
    assert merged["edge_tts"]["rate"] == "+8%"


def test_course_material_normalizes_slides_without_audio(tmp_path: Path) -> None:
    task_root = tmp_path / "ppt_course_data" / "tasks" / "task-1"
    preview = task_root / "previews" / "slide-0000"
    preview.mkdir(parents=True)
    full = preview / "full.png"
    full.write_bytes(b"png")
    (task_root / "meta.json").write_text(
        json.dumps({"filename": "合规培训.pptx"}, ensure_ascii=False),
        encoding="utf-8",
    )
    raw_path = task_root / "raw_material_manifest.json"
    raw_path.write_text(
        json.dumps(
            {
                "task_id": "task-1",
                "source_pptx": "/tmp/合规培训.pptx",
                "task_root": str(task_root),
                "slides": [
                    {
                        "slide_id": "slide-0000",
                        "slide_index": 0,
                        "full_page_png": str(full),
                        "raw_text": "处罚标准：迟到罚款 50 元，不得代打卡。",
                        "shapes": [],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    out_path = task_root / "course_material.json"
    material = build_course_material(raw_path, out_path)

    assert out_path.is_file()
    slide = material["slides"][0]
    assert "risk_or_penalty" in slide["material_tags"]
    assert slide["material_role"] == "risk_rule_material"
    assert "金额" in slide["teaching_purpose"]
    assert slide["recommended_layout"] == "rule_card"
    assert slide["recommended_scene_layout"] == "rule_card"
    assert "primary_slide_evidence" in slide["asset_roles"]
    assert slide["risk_items"][0]["numbers"] == ["50"]
    assert slide["evidence_texts"]
    assert slide["audio_segments"] == []


def test_course_material_can_be_enriched_by_fake_director_llm(tmp_path: Path) -> None:
    task_root = tmp_path / "ppt_course_data" / "tasks" / "task-1"
    preview = task_root / "previews" / "slide-0000"
    preview.mkdir(parents=True)
    full = preview / "full.png"
    full.write_bytes(b"png")
    raw_path = task_root / "raw_material_manifest.json"
    raw_path.write_text(
        json.dumps(
            {
                "task_id": "task-1",
                "source_pptx": "/tmp/合规培训.pptx",
                "task_root": str(task_root),
                "slides": [
                    {
                        "slide_id": "slide-0000",
                        "slide_index": 0,
                        "full_page_png": str(full),
                        "raw_text": "服务期违规：员工提前离职需赔偿 100 元。",
                        "shapes": [],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    class FakeLLM:
        available = True

        def call_json(self, **_kwargs):
            return {
                "slides": [
                    {
                        "slide_id": "slide-0000",
                        "material_role": "compliance_rule",
                        "teaching_purpose": "解释赔偿边界并提醒人工核对。",
                        "recommended_scene_layout": "rule_card",
                        "asset_roles": ["primary_slide_evidence", "risk_information"],
                        "evidence_texts": ["员工提前离职需赔偿 100 元"],
                    }
                ]
            }

    material = build_course_material(
        raw_path,
        task_root / "course_material.json",
        use_llm=True,
        llm_client=FakeLLM(),
    )

    assert material["llm_enhancement"]["status"] == "applied"
    slide = material["slides"][0]
    assert slide["material_role"] == "compliance_rule"
    assert slide["asset_roles"] == ["primary_slide_evidence", "risk_information"]


def test_director_validator_warns_when_risk_number_is_missing() -> None:
    material = {
        "slides": [
            {
                "slide_id": "slide-0000",
                "raw_text": "处罚标准：迟到罚款 50 元。",
            }
        ]
    }
    manifest = {
        "scenes": [
            {
                "scene_id": "sc-1",
                "source_slide_ids": ["slide-0000"],
                "tts_text": "迟到会罚款，请注意。",
                "timing": {"estimated_duration_sec": 8},
                "risk_flags": ["contains_penalty_or_amount"],
            }
        ]
    }

    checks = validate_director_manifest(manifest, material)

    assert checks["ok"] is True
    assert checks["warning_count"] == 1
    assert checks["warnings"][0]["code"] == "risk_number_missing"


def test_render_adapter_uses_director_manifest_before_fallback(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    task_id = "task-1"
    data_root = tmp_path / "ppt_course_data"
    task_root = data_root / "tasks" / task_id
    preview = task_root / "previews" / "slide-0000"
    preview.mkdir(parents=True)
    (preview / "full.png").write_bytes(b"png")
    (task_root / "director_manifest.json").write_text(
        json.dumps(
            {
                "scenes": [
                    {
                        "scene_id": "sc-1",
                        "source_slide_ids": ["slide-0000"],
                        "title": "处罚标准",
                        "onscreen_text": "处罚标准：迟到罚款 50 元",
                        "subtitle_text": "迟到罚款 50 元",
                        "subtitle": {
                            "segments": [
                                {"start_sec": 0, "end_sec": 3, "text": "迟到罚款 50 元"}
                            ]
                        },
                        "timing": {"estimated_duration_sec": 5},
                        "screen_design": {"layout": "rule_card"},
                        "risk_flags": ["contains_penalty_or_amount"],
                        "risk_items": [
                            {
                                "risk_type": "risk_or_penalty",
                                "quote": "迟到罚款 50 元",
                                "numbers": ["50"],
                            }
                        ],
                        "source_evidence": [
                            {"slide_id": "slide-0000", "quote": "处罚标准：迟到罚款 50 元"}
                        ],
                        "render_overlays": {
                            "callouts": [{"label": "迟到罚款 50 元", "kind": "emphasis"}],
                            "evidence_panel": {
                                "title": "原文证据",
                                "quotes": [
                                    {
                                        "slide_id": "slide-0000",
                                        "quote": "处罚标准：迟到罚款 50 元",
                                    }
                                ],
                            },
                            "risk_badge": {
                                "show": True,
                                "label": "需核对原文",
                                "items": [
                                    {
                                        "risk_type": "risk_or_penalty",
                                        "quote": "迟到罚款 50 元",
                                        "numbers": ["50"],
                                    }
                                ],
                            },
                            "transition": {"type": "chapter", "label": "处罚标准"},
                        },
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    import ppt_course_rebuilder.render_adapter as adapter

    monkeypatch.setattr(adapter, "get_data_root", lambda: data_root)
    monkeypatch.setattr(adapter, "load_meta", lambda _kind, _key: {})
    monkeypatch.setattr(
        adapter, "resolve_workspace_audio_path", lambda *_args, **_kwargs: None
    )

    renderer_root = tmp_path / "ppt_course_renderer"
    result = write_render_plan_from_task(task_id, fps=30, root=renderer_root)

    props_path = Path(result["input_props_path"])
    plan_path = Path(result["render_plan_path"])
    props = json.loads(props_path.read_text(encoding="utf-8"))
    assert result["source"] == "director_manifest"
    assert props["slides"][0]["layout"] == "rule_card"
    assert props["slides"][0]["durationInFrames"] == 150
    assert props["slides"][0]["callouts"][0]["label"] == "迟到罚款 50 元"
    assert props["slides"][0]["evidencePanel"]["quotes"][0]["quote"].endswith("50 元")
    assert props["slides"][0]["riskBadge"]["show"] is True
    assert props["slides"][0]["subtitleSegments"][0]["text"] == "迟到罚款 50 元"
    assert props["slides"][0]["transition"]["type"] == "chapter"
    assert result["layout_counts"] == {"rule_card": 1}
    assert result["risk_scene_count"] == 1
    assert plan_path.is_file()
