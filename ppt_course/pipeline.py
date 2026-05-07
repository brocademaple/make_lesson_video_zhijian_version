from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional, Union

from ppt_course.build_pptx import build_course_presentation, save_presentation
from ppt_course.extract import guess_slide_title, load_presentation, slide_plain_text
from ppt_course.extensions import HeuristicAnalyzer, SlideAnalyzer
from ppt_course.models import CourseSlidePlan, SourceSlide, TransformResult
from ppt_course.planner import plan_course_slides


def transform_pptx(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    *,
    analyzer: Optional[SlideAnalyzer] = None,
    dump_plan_json: Optional[Union[str, Path]] = None,
) -> TransformResult:
    """
    读取原始 PPTX → 逐页解析与分类 → 规划课程页 → 写出新版 PPTX。
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    ana = analyzer or HeuristicAnalyzer()

    prs = load_presentation(str(input_path))
    all_plans: list[CourseSlidePlan] = []

    for idx, slide in enumerate(prs.slides):
        raw = slide_plain_text(slide)
        title = guess_slide_title(slide, raw)
        src = SourceSlide(index=idx, title=title, raw_text=raw, blocks=[])
        src.blocks = ana.analyze(src)
        all_plans.extend(plan_course_slides(src))

    out_prs = build_course_presentation(all_plans)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_presentation(out_prs, str(output_path))

    if dump_plan_json:
        p = Path(dump_plan_json)
        p.parent.mkdir(parents=True, exist_ok=True)
        data: dict[str, Any] = {
            "slides": [s.model_dump() for s in all_plans],
            "meta": {
                "analyzer": type(ana).__name__,
                "input": str(input_path),
                "output": str(output_path),
            },
        }
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return TransformResult(
        source_path=str(input_path),
        output_path=str(output_path),
        source_slide_count=len(prs.slides),
        output_slide_count=len(all_plans),
        slides=all_plans,
        meta={"analyzer": type(ana).__name__},
    )
