"""LLM planning layer for raw material manifests."""

from __future__ import annotations

import json
from typing import Any

from ppt_course_rebuilder.llm_client import DirectorLLMClient

SYSTEM_PROMPT = """你是培训课程导演，负责把原始 PPT 素材重构成可用于录播视频的导演脚本。
你必须只输出合法 JSON，不要 markdown，不要额外解释。
业务准确性优先：不得编造规则、处罚、金额、案例；可以改写表达，但含义必须来自原文。
输出要服务于后续 Remotion 渲染，所以每个 scene 都要给出清晰的教学目标、口播、字幕、画面策略和素材使用建议。"""


USER_PROMPT_TEMPLATE = """请基于以下 raw_material_manifest 摘要，生成课程导演脚本 JSON。

【输出 JSON 结构】
{{
  "course": {{
    "title": "课程标题",
    "audience": "受众",
    "goal": "课程目标"
  }},
  "scenes": [
    {{
      "source_slide_ids": ["slide-0000"],
      "scene_type": "title | agenda | rule_explanation | rule_card | case_dialogue | explanation | summary",
      "title": "短标题",
      "learning_goal": "本镜头学习目标",
      "onscreen_text": "适合屏幕展示的精简文字",
      "bullets": ["最多 3 条"],
      "tts_text": "自然口播稿，适合中文 TTS",
      "subtitle_text": "字幕精简稿",
      "screen_design": {{
        "layout": "full_slide | split_panel | rule_card | case_dialogue | summary",
        "visual_strategy": "如何使用整页图、小图、强调层或字幕",
        "emphasis": ["关键词"]
      }},
      "risk_flags": ["如 compliance_sensitive / contains_penalty_or_amount"]
    }}
  ]
}}

【约束】
1. 每个原始页至少进入一个 scene；允许相邻页合并，但 source_slide_ids 必须保留。
2. onscreen_text 要比原文更短，适合视频画面展示。
3. tts_text 必须保留原文中的关键数字、金额、处罚后果和规则边界。
4. bullets 最多 3 条，每条尽量短。
5. 不要虚构案例；若原文没有案例，不要创造对话。
6. 字段缺失时用空字符串或空数组，不要省略核心字段。

【raw_material_manifest 摘要】
{payload}
"""


def _compact_slide(slide: dict[str, Any], max_chars: int) -> dict[str, Any]:
    raw_text = str(slide.get("raw_text") or "")
    shapes = slide.get("shapes") or []
    if not isinstance(shapes, list):
        shapes = []
    return {
        "slide_id": slide.get("slide_id") or f"slide-{int(slide.get('slide_index') or 0):04d}",
        "slide_index": int(slide.get("slide_index") or 0),
        "raw_text": raw_text[:max_chars],
        "speaker_notes": slide.get("speaker_notes") or "",
        "has_full_page_png": bool(slide.get("full_page_png")),
        "shape_count": len(shapes),
    }


def build_director_prompt(raw_manifest: dict[str, Any], *, max_slides: int = 30) -> str:
    slides = raw_manifest.get("slides") or []
    if not isinstance(slides, list):
        slides = []
    compact = {
        "task_id": raw_manifest.get("task_id") or "",
        "source_pptx": raw_manifest.get("source_pptx") or "",
        "slides": [_compact_slide(s, 1600) for s in slides[:max_slides] if isinstance(s, dict)],
    }
    payload = json.dumps(compact, ensure_ascii=False, indent=2)
    return USER_PROMPT_TEMPLATE.format(payload=payload)


def plan_director_manifest_with_llm(
    raw_manifest: dict[str, Any],
    *,
    client: DirectorLLMClient | None = None,
    max_slides: int = 30,
) -> dict[str, Any]:
    llm = client or DirectorLLMClient()
    prompt = build_director_prompt(raw_manifest, max_slides=max_slides)
    data = llm.call_json(system=SYSTEM_PROMPT, user=prompt, temperature=0.2)
    scenes = data.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise ValueError("LLM director 输出缺少 scenes")
    course = data.get("course")
    if not isinstance(course, dict):
        data["course"] = {}
    return data
