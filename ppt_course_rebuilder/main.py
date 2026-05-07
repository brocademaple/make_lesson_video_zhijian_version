#!/usr/bin/env python3
"""PPT → 课程化 PPT CLI（analyze / plan / build / full）。"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
# 先插入 ROOT，再插入 SRC → sys.path 顺序为 [SRC, ROOT]，优先加载 src 内模块
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import config as cfg  # noqa: E402
from ai_client import AIClient  # noqa: E402
from course_planner import plan_course, plan_course_fallback  # noqa: E402
from image_exporter import export_pptx_to_png  # noqa: E402
from models import CourseSlide, RunSummary, SlideAnalysis  # noqa: E402
from ppt_reader import read_presentation  # noqa: E402
from ppt_writer import build_presentation, write_page_scripts  # noqa: E402
from slide_analyzer import analyze_all  # noqa: E402
from utils import read_json, setup_logging, write_json, ensure_placeholder_assets  # noqa: E402


def _norm_api_base() -> str:
    u = cfg.ai_base_url().rstrip("/")
    if u.endswith("/v1"):
        return u
    return u + "/v1"


def _make_ai_client() -> AIClient:
    return AIClient(cfg.ai_api_key(), _norm_api_base(), cfg.ai_model())


def _out_dir() -> Path:
    d = cfg.output_dir()
    d.mkdir(parents=True, exist_ok=True)
    return d


def _assets_dir() -> Path:
    return cfg.assets_dir()


def _write_summary(path: Path, summary: RunSummary) -> None:
    write_json(path, summary.model_dump())


def run_analyze(input_pptx: Path, summary: RunSummary) -> None:
    if not input_pptx.is_file():
        raise FileNotFoundError(f"找不到输入文件：{input_pptx}")

    raw = read_presentation(str(input_pptx))
    if not raw:
        summary.warnings.append("原始 PPT 未解析到任何页面或文本为空")

    client = _make_ai_client()
    analyses = analyze_all(client, raw)
    out_path = _out_dir() / "slide_analysis.json"
    write_json(out_path, [a.model_dump() for a in analyses])
    summary.output_paths["slide_analysis.json"] = str(out_path)
    logging.info("已写入 %s", out_path)


def run_plan(summary: RunSummary) -> None:
    path = _out_dir() / "slide_analysis.json"
    if not path.is_file():
        raise FileNotFoundError(f"请先运行 analyze 或提供 {path}")

    data = read_json(path)
    analyses = [SlideAnalysis.model_validate(x) for x in data]

    client = _make_ai_client()

    try:
        if not client.available:
            raise RuntimeError("未配置 AI_API_KEY")
        slides = plan_course(client, analyses)
    except Exception as e:
        logging.warning("课程规划 AI 失败，启用兜底：%s", e)
        summary.warnings.append(f"课程规划使用兜底：{e}")
        slides = plan_course_fallback(analyses)

    out_path = _out_dir() / "course_slides.json"
    write_json(out_path, [s.model_dump() for s in slides])
    summary.output_paths["course_slides.json"] = str(out_path)


def run_build(
    course_json: Path,
    out_pptx: Path,
    summary: RunSummary,
    write_scripts: bool = True,
) -> None:
    out_pptx.parent.mkdir(parents=True, exist_ok=True)

    if not course_json.is_file():
        raise FileNotFoundError(f"找不到课程 JSON：{course_json}")

    data = read_json(course_json)
    slides = [CourseSlide.model_validate(x) for x in data]

    ensure_placeholder_assets(_assets_dir())
    errs = build_presentation(slides, out_pptx, _assets_dir())
    summary.output_paths["course_rebuilt.pptx"] = str(out_pptx)
    for e in errs:
        summary.errors.append(e)

    if write_scripts:
        ps = _out_dir() / "page_scripts.md"
        write_page_scripts(slides, ps)
        summary.output_paths["page_scripts.md"] = str(ps)


def main() -> int:
    parser = argparse.ArgumentParser(description="PPT 课程化重构工具（MVP）")
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "input" / "original.pptx",
        help="输入 PPTX",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "output" / "course_rebuilt.pptx",
        help="输出 PPTX 路径",
    )
    parser.add_argument(
        "--mode",
        choices=("analyze", "plan", "build", "full"),
        default="full",
        help="analyze：仅分析；plan：仅规划；build：仅生成；full：全流程",
    )
    parser.add_argument(
        "--course-slides",
        type=Path,
        default=ROOT / "output" / "course_slides.json",
        help="build 模式使用的课程 JSON",
    )
    parser.add_argument(
        "--export-images",
        action="store_true",
        help="若本机有 LibreOffice，尝试导出 PNG 到 output/exported_images/",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    setup_logging(args.verbose)
    _out_dir()

    summary = RunSummary(mode=args.mode, ok=True)

    try:
        if args.mode == "analyze":
            run_analyze(args.input, summary)
        elif args.mode == "plan":
            run_plan(summary)
        elif args.mode == "build":
            run_build(args.course_slides, args.output, summary)
        elif args.mode == "full":
            run_analyze(args.input, summary)
            path_an = _out_dir() / "slide_analysis.json"
            analyses = [SlideAnalysis.model_validate(x) for x in read_json(path_an)]
            client = _make_ai_client()
            try:
                if not client.available:
                    raise RuntimeError("未配置 AI_API_KEY")
                slides = plan_course(client, analyses)
            except Exception as e:
                logging.warning("课程规划 AI 失败：%s", e)
                summary.warnings.append(str(e))
                slides = plan_course_fallback(analyses)
            cs_path = _out_dir() / "course_slides.json"
            write_json(cs_path, [s.model_dump() for s in slides])
            summary.output_paths["course_slides.json"] = str(cs_path)
            run_build(cs_path, args.output, summary)
            if args.export_images:
                img_dir = _out_dir() / "exported_images"
                export_pptx_to_png(args.output, img_dir)
                summary.output_paths["exported_images/"] = str(img_dir)

        summary.ok = True
    except Exception as e:
        summary.ok = False
        summary.errors.append(str(e))
        logging.exception("运行失败")
        _write_summary(_out_dir() / "summary_report.json", summary)
        logging.error("%s", e)
        return 1

    _write_summary(_out_dir() / "summary_report.json", summary)
    logging.info(
        "完成。errors=%s warnings=%s",
        len(summary.errors),
        len(summary.warnings),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
