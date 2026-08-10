from __future__ import annotations

import json
from pathlib import Path

from ppt_course_deal.video_project import (
    validate_video_project,
    video_project_to_props,
    write_video_project_props,
)
from ppt_course_deal.video_profiles import normalize_video_profile_id, video_profile


def _project() -> dict:
    return {
        "title": "AIGC 工作台体验",
        "intent": "product_experience",
        "format": "vertical_1080x1920",
        "materials": [
            {
                "id": "home",
                "type": "screenshot",
                "relative": "assets/home.png",
                "label": "首页",
            },
            {
                "id": "detail",
                "type": "screenshot",
                "relative": "assets/detail.png",
                "label": "详情页",
            },
            {
                "id": "voice",
                "type": "audio",
                "relative": "assets/voice.wav",
                "label": "主旁白",
            },
        ],
        "primary_audio_asset_id": "voice",
        "scenes": [
            {
                "id": "intro",
                "title": "开场",
                "asset_id": "home",
                "duration_sec": 3,
                "narration": "先看它如何把素材组织成项目。",
            },
            {
                "id": "zoom",
                "title": "放大裂变入口",
                "asset_id": "detail",
                "duration_sec": 4,
                "shot_type": "zoom_detail",
                "focus_rect": {"x": 52, "y": 20, "width": 34, "height": 42},
                "effects": [
                    {
                        "type": "camera.zoom_to",
                        "rect": {"x": 52, "y": 20, "width": 34, "height": 42},
                        "scale": 1.6,
                    }
                ],
                "narration": "这里可以生成多个可编辑的视频版本。",
            },
        ],
        "variants": [
            {
                "id": "primary",
                "title": "完整讲解版",
                "scene_ids": ["intro", "zoom"],
                "template_package": "ProductExperience",
            },
            {
                "id": "fast-demo",
                "title": "快速演示版",
                "scene_ids": ["zoom"],
                "template_package": "ProductExperience",
            },
        ],
    }


def test_validate_video_project_accepts_creator_project() -> None:
    assert validate_video_project(_project()) == []


def test_video_project_to_props_supports_variants(tmp_path: Path) -> None:
    project_path = tmp_path / "video_project.json"
    props = video_project_to_props(
        _project(),
        project_path=project_path,
        variant_id="fast-demo",
        fps=30,
    )

    assert props["schemaVersion"] == "visual_project_props.v1"
    assert props["title"] == "快速演示版"
    assert props["templatePackage"] == "ProductExperience"
    assert props["width"] == 1080
    assert props["height"] == 1920
    assert len(props["scenes"]) == 1
    assert props["scenes"][0]["id"] == "zoom"
    assert props["scenes"][0]["durationInFrames"] == 120
    assert props["scenes"][0]["asset"]["relative"] == "assets/detail.png"
    assert props["scenes"][0]["effects"][0]["type"] == "camera.zoom_to"
    assert props["audio"]["relative"] == "assets/voice.wav"


def test_write_video_project_props_roundtrip(tmp_path: Path) -> None:
    project_path = tmp_path / "video_project.json"
    output = tmp_path / "input-props.json"
    project_path.write_text(json.dumps(_project(), ensure_ascii=False), encoding="utf-8")

    props = write_video_project_props(project_path, output, variant_id="primary")

    assert output.is_file()
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved == props
    assert len(saved["scenes"]) == 2


def test_legacy_quality_profile_maps_to_knowledge() -> None:
    assert normalize_video_profile_id("quality") == "knowledge"
    assert video_profile("quality")["label"] == "知识讲解"
