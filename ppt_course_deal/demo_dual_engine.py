"""Generate local dual-engine demo tasks for Remotion + Hyperframes validation."""

from __future__ import annotations

import json
import os
import signal
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from ppt_course_deal.audio_duration import probe_audio_duration_seconds
from ppt_course_deal.audio_workspace_store import (
    append_segment_generation,
    save_meta_for_workspace,
    workspace_relative_segment_path_unique,
    workspace_root,
)
from ppt_course_deal.external_settings import load_raw
from ppt_course_deal.speech_synthesis import synthesize_speech
from ppt_course_deal.task_storage import get_data_root, tasks_dir
from ppt_course_rebuilder.material_normalizer import build_course_material
from ppt_course_rebuilder.render_adapter import write_render_plan_from_task


DEMO_ONBOARDING_TASK_ID = "11111111-1111-4111-8111-111111111111"
DEMO_CREATIVE_TASK_ID = "22222222-2222-4222-8222-222222222222"
SENSITIVE_ENV_MARKERS = ("TOKEN", "SECRET", "PASSWORD", "AUTH", "API_KEY")


@dataclass(frozen=True)
class DemoSlide:
    title: str
    body: str
    narration: str
    scene_type: str
    scene_role: str
    render_engine: str
    layout: str
    accent: str
    bullets: tuple[str, ...]
    risk_flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class DemoCourse:
    task_id: str
    slug: str
    filename: str
    title: str
    audience: str
    goal: str
    video_profile: dict[str, Any]
    slides: tuple[DemoSlide, ...]


def demo_courses() -> tuple[DemoCourse, DemoCourse]:
    onboarding = DemoCourse(
        task_id=DEMO_ONBOARDING_TASK_ID,
        slug="demo-onboarding-training",
        filename="demo-onboarding-training.pptx",
        title="企业内部新人培训宣讲",
        audience="新入职同学",
        goal="帮助新人理解协作方式、信息安全和客户沟通边界。",
        video_profile={
            "id": "onboarding",
            "label": "新人培训宣讲",
            "motion_style": "guided_steps",
            "visual_strategy": "source_slide_with_warm_guidance",
            "remotion": {"theme": "onboarding", "shot_motion": "guided_steps"},
        },
        slides=(
            DemoSlide(
                "欢迎加入：先理解我们如何协作",
                "新人第一周最重要的不是记住所有流程，而是知道如何提问、如何同步、如何保护客户信息。",
                "欢迎加入团队。这一节课会用五分钟帮你建立三个基本意识：协作透明、信息安全，以及客户沟通边界。",
                "title",
                "intro",
                "hyperframes_creative",
                "full_slide",
                "#8b5cf6",
                ("协作透明", "信息安全", "客户沟通边界"),
            ),
            DemoSlide(
                "协作规范：让信息在正确的位置流动",
                "所有关键结论进入任务系统；临时讨论可以在群里发生，但决策和风险必须沉淀。",
                "第一条协作规范，是让信息在正确的位置流动。群聊适合快速确认，但关键结论必须回到任务系统，避免后续追溯时找不到依据。",
                "explanation",
                "content",
                "remotion_stable",
                "split_panel",
                "#22c55e",
                ("群聊用于快速确认", "任务系统沉淀结论", "风险必须可追溯"),
            ),
            DemoSlide(
                "信息安全：客户资料只在授权场景中使用",
                "客户手机号、身份证、住址、订单信息都属于敏感资料。不得截图外发，不得私下转存。",
                "第二条是信息安全。客户手机号、身份证、住址和订单信息，都只能在授权场景中使用。不要截图外发，也不要私下转存。",
                "rule_explanation",
                "content",
                "remotion_stable",
                "rule_card",
                "#f59e0b",
                ("授权场景使用", "不得截图外发", "不得私下转存"),
                ("compliance_sensitive",),
            ),
            DemoSlide(
                "客户沟通：错误话术要能立刻换成正确话术",
                "错误：我可以帮你查完整手机号。正确：请通过系统授权流程核验身份后再查询。",
                "第三条是客户沟通。比如，不能直接说我可以帮你查完整手机号。更稳妥的说法是，请先通过系统授权流程核验身份，再进行必要查询。",
                "case_dialogue",
                "concept_animation",
                "hybrid",
                "case_dialogue",
                "#06b6d4",
                ("错误话术", "授权核验", "正确表达"),
            ),
            DemoSlide(
                "遇到不确定：先暂停，再升级",
                "当你不确定某个动作是否合规，不要凭经验继续处理。先暂停，记录上下文，再升级给主管。",
                "最后，如果你不确定某个动作是否合规，不要凭经验继续处理。先暂停，记录上下文，再升级给主管。",
                "summary",
                "recap",
                "hyperframes_creative",
                "summary",
                "#ec4899",
                ("先暂停", "记录上下文", "升级给主管"),
            ),
        ),
    )

    creative = DemoCourse(
        task_id=DEMO_CREATIVE_TASK_ID,
        slug="demo-creative-redline-course",
        filename="demo-creative-redline-course.pptx",
        title="质检红线问题：客户隐私专项训练",
        audience="质检与一线客服团队",
        goal="用更生动的方式整合红线规则、错误案例和正确处理路径。",
        video_profile={
            "id": "quality",
            "label": "质检红线创意课",
            "motion_style": "spotlight_reveal",
            "visual_strategy": "risk_radar_with_source_evidence",
            "remotion": {"theme": "quality", "shot_motion": "spotlight_reveal"},
        },
        slides=(
            DemoSlide(
                "红线雷达：客户隐私不能被随意触碰",
                "今天我们把客户隐私红线拆成三个信号：敏感字段、授权场景、违规承诺。",
                "欢迎来到质检红线专项训练。今天我们用一个红线雷达，把客户隐私问题拆成三个信号：敏感字段、授权场景，以及违规承诺。",
                "title",
                "intro",
                "hyperframes_creative",
                "full_slide",
                "#ef4444",
                ("敏感字段", "授权场景", "违规承诺"),
            ),
            DemoSlide(
                "场景一：完整手机号属于敏感信息",
                "坐席不得在未完成身份核验前查询、复述或截图客户完整手机号。",
                "第一个信号，是完整手机号。没有完成身份核验前，不要查询、复述，也不要截图外发客户完整手机号。",
                "rule_explanation",
                "content",
                "remotion_stable",
                "rule_card",
                "#f97316",
                ("未核验不查询", "不复述完整号码", "不截图外发"),
                ("compliance_sensitive",),
            ),
            DemoSlide(
                "错误对话：我帮你查完整手机号",
                "这句话的问题在于：查询动作发生在授权之前，而且把敏感字段当成普通服务信息。",
                "我们看一个错误对话：我帮你查完整手机号。问题在于，查询动作发生在授权之前，而且把敏感字段当成普通服务信息。",
                "case_dialogue",
                "concept_animation",
                "hybrid",
                "case_dialogue",
                "#fb7185",
                ("授权之前", "敏感字段", "错误承诺"),
            ),
            DemoSlide(
                "正确路径：先核验，再最小必要查询",
                "正确话术：为了保护您的信息安全，请先完成身份核验。核验通过后，我再查询必要信息。",
                "正确路径是，先核验，再做最小必要查询。可以这样说：为了保护您的信息安全，请先完成身份核验。核验通过后，我再查询必要信息。",
                "explanation",
                "concept_animation",
                "hybrid",
                "split_panel",
                "#38bdf8",
                ("先核验", "最小必要", "系统留痕"),
            ),
            DemoSlide(
                "红线后果：严重违规必须升级处理",
                "如果出现私下转存、外发、倒卖客户信息等行为，必须按严重违规升级处理。",
                "如果出现私下转存、外发，甚至倒卖客户信息，就不是普通服务瑕疵，而是严重违规，必须升级处理。",
                "rule_card",
                "content",
                "remotion_stable",
                "rule_card",
                "#f43f5e",
                ("私下转存", "外发截图", "倒卖信息"),
                ("compliance_sensitive", "contains_penalty_or_amount"),
            ),
            DemoSlide(
                "一分钟复盘：看到敏感信息，先停一下",
                "三句话记住：先核验身份；只查必要字段；任何外发和私存都要拒绝。",
                "最后一分钟复盘。看到敏感信息，先停一下。记住三句话：先核验身份，只查必要字段，任何外发和私存都要拒绝。",
                "summary",
                "recap",
                "hyperframes_creative",
                "summary",
                "#a855f7",
                ("先核验身份", "只查必要字段", "拒绝外发私存"),
            ),
        ),
    )
    return onboarding, creative


def generate_dual_engine_demo_tasks(
    *,
    render: bool = True,
    try_hyperframes: bool = True,
) -> dict[str, Any]:
    results = []
    for course in demo_courses():
        results.append(
            _generate_one_course(
                course,
                render=render,
                try_hyperframes=try_hyperframes,
            )
        )
    return {
        "ok": all(item.get("ok") for item in results),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tasks": results,
    }


def _generate_one_course(
    course: DemoCourse,
    *,
    render: bool,
    try_hyperframes: bool,
) -> dict[str, Any]:
    task_root = tasks_dir() / course.task_id
    audio_root = get_data_root() / "audio_workspace" / "task" / course.task_id
    renderer_task_root = (
        Path(__file__).resolve().parent.parent
        / "ppt_course_renderer"
        / "render_tasks"
        / f"task-{course.task_id}"
    )
    shutil.rmtree(task_root, ignore_errors=True)
    shutil.rmtree(audio_root, ignore_errors=True)
    shutil.rmtree(renderer_task_root, ignore_errors=True)
    task_root.mkdir(parents=True, exist_ok=True)
    (task_root / "source.pptx").write_bytes(b"demo task generated by Codex\n")

    report: dict[str, Any] = {
        "task_id": course.task_id,
        "slug": course.slug,
        "filename": course.filename,
        "steps": [],
        "tts": [],
        "hyperframes": [],
        "remotion": {},
        "ok": False,
    }
    try:
        slides_meta = _write_previews_and_meta(course, task_root)
        report["steps"].append({"step": "task_meta", "status": "ok", "slide_count": len(slides_meta)})
        raw_path = _write_raw_material(course, task_root)
        report["steps"].append({"step": "raw_material_manifest", "status": "ok", "path": str(raw_path)})
        material = build_course_material(raw_path, task_root / "course_material.json", use_llm=False)
        report["steps"].append(
            {
                "step": "course_material",
                "status": "ok",
                "slide_count": len(material.get("slides") or []),
            }
        )
        director_path = _write_director_manifest(course, task_root)
        report["steps"].append({"step": "director_manifest", "status": "ok", "path": str(director_path)})
        _write_audio(course, report)
        render_plan = write_render_plan_from_task(course.task_id, fps=30, no_audio_frames=90)
        report["render_plan"] = render_plan
        report["steps"].append({"step": "render_plan.v2", "status": "ok", "path": render_plan.get("render_plan_path")})
        if try_hyperframes:
            _try_generate_hyperframes_assets(course, report)
            render_plan = write_render_plan_from_task(course.task_id, fps=30, no_audio_frames=90)
            report["render_plan"] = render_plan
        if render:
            _render_with_remotion(course, report)
        report["ok"] = bool((report.get("remotion") or {}).get("output_video_exists") or not render)
    except Exception as exc:
        report["steps"].append({"step": "fatal", "status": "failed", "error": str(exc)})
    finally:
        report_path = task_root / "render_report.json"
        report["report_path"] = str(report_path)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def _font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for path in candidates:
        if Path(path).is_file():
            try:
                return ImageFont.truetype(path, size=size, index=1 if bold else 0)
            except Exception:
                continue
    return ImageFont.load_default()


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for char in text:
        candidate = current + char
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = char
    if current:
        lines.append(current)
    return lines


def _write_previews_and_meta(course: DemoCourse, task_root: Path) -> list[dict[str, Any]]:
    slides_meta: list[dict[str, Any]] = []
    previews = task_root / "previews"
    previews.mkdir(parents=True, exist_ok=True)
    for idx, slide in enumerate(course.slides):
        slide_dir = previews / f"slide-{idx:04d}"
        slide_dir.mkdir(parents=True, exist_ok=True)
        png = slide_dir / "full.png"
        _render_slide_png(course, slide, idx, png)
        text_blocks = [slide.title, slide.body, *slide.bullets]
        slides_meta.append(
            {
                "index": idx,
                "slide_index": idx,
                "slide_id": f"slide-{idx:04d}",
                "title": slide.title,
                "text": "\n".join(text_blocks),
                "text_blocks": text_blocks,
                "speaker_notes": slide.narration,
            }
        )
    meta = {
        "id": course.task_id,
        "filename": course.filename,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "slide_count": len(course.slides),
        "slides": slides_meta,
        "preview_source": "codex_demo_generator",
        "images_error": "",
        "images_available": True,
        "preview_count": len(course.slides),
        "shape_image_manifest": [],
        "video_profile": course.video_profile,
        "demo": {"slug": course.slug, "generated_by": "dual_engine_demo"},
    }
    (task_root / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return slides_meta


def _render_slide_png(course: DemoCourse, slide: DemoSlide, idx: int, path: Path) -> None:
    width, height = 1920, 1080
    img = Image.new("RGB", (width, height), "#070b14")
    draw = ImageDraw.Draw(img)
    accent = slide.accent
    for i in range(0, width, 16):
        shade = int(18 + 28 * (i / width))
        draw.line((i, 0, i, height), fill=(shade, shade + 4, shade + 16), width=16)
    draw.rounded_rectangle((86, 78, 1834, 1002), radius=34, outline=accent, width=4, fill=(9, 17, 33))
    draw.rectangle((86, 78, 1834, 170), fill=accent)
    title_font = _font(58, bold=True)
    body_font = _font(36)
    bullet_font = _font(34, bold=True)
    small_font = _font(24)
    draw.text((130, 101), course.title, fill="#ffffff", font=small_font)
    draw.text((130, 230), slide.title, fill="#f8fafc", font=title_font)
    y = 340
    for line in _wrap_text(draw, slide.body, body_font, 1280)[:5]:
        draw.text((130, y), line, fill="#cbd5e1", font=body_font)
        y += 54
    bx = 130
    by = 710
    for bidx, bullet in enumerate(slide.bullets[:3]):
        x = bx + bidx * 520
        draw.rounded_rectangle((x, by, x + 455, by + 130), radius=24, fill=(16, 30, 55), outline=accent, width=3)
        draw.text((x + 28, by + 38), bullet, fill="#ffffff", font=bullet_font)
    draw.text((130, 930), f"{idx + 1:02d} · {slide.render_engine} · {slide.scene_role}", fill="#94a3b8", font=small_font)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG")


def _write_raw_material(course: DemoCourse, task_root: Path) -> Path:
    slides = []
    for idx, slide in enumerate(course.slides):
        slides.append(
            {
                "slide_id": f"slide-{idx:04d}",
                "slide_index": idx,
                "full_page_png": f"previews/slide-{idx:04d}/full.png",
                "raw_text": "\n".join([slide.title, slide.body, *slide.bullets]),
                "speaker_notes": slide.narration,
                "shapes": [],
            }
        )
    raw = {
        "task_id": course.task_id,
        "source_pptx": "source.pptx",
        "task_root": str(task_root),
        "slides": slides,
    }
    path = task_root / "raw_material_manifest.json"
    path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _write_director_manifest(course: DemoCourse, task_root: Path) -> Path:
    scenes = []
    for idx, slide in enumerate(course.slides):
        duration = max(3.0, min(16.0, len(slide.narration) / 8.0 + 1.5))
        evidence = [{"slide_id": f"slide-{idx:04d}", "quote": slide.body[:220]}]
        risk_items = (
            [{"risk_type": "compliance", "quote": slide.body[:160], "numbers": [], "slide_id": f"slide-{idx:04d}"}]
            if slide.risk_flags
            else []
        )
        scenes.append(
            {
                "scene_id": f"sc-{idx:04d}-{slide.scene_type}",
                "scene_type": slide.scene_type,
                "scene_role": slide.scene_role,
                "render_engine": slide.render_engine,
                "fallback_engine": "remotion_stable" if slide.render_engine != "remotion_stable" else "",
                "source_slide_ids": [f"slide-{idx:04d}"],
                "learning_goal": f"理解「{slide.title}」的关键要求。",
                "title": slide.title,
                "onscreen_text": slide.body,
                "narration": slide.narration,
                "tts_text": slide.narration,
                "subtitle_text": slide.narration,
                "content": {"title": slide.title, "onscreen_text": slide.body, "bullets": list(slide.bullets)},
                "subtitle": {"segments": [{"start_sec": 0, "end_sec": round(duration, 2), "text": slide.narration[:120]}]},
                "timing": {"estimated_duration_sec": round(duration, 2)},
                "screen_design": {
                    "layout": slide.layout,
                    "visual_strategy": course.video_profile.get("visual_strategy", ""),
                    "emphasis": list(slide.bullets),
                },
                "render_intent": {
                    "style": course.video_profile.get("id", ""),
                    "profile_label": course.video_profile.get("label", ""),
                    "layout": slide.layout,
                    "use_source_slide_as_evidence": True,
                },
                "source_evidence": evidence,
                "risk_items": risk_items,
                "render_overlays": {
                    "callouts": [{"label": b, "kind": "emphasis"} for b in slide.bullets],
                    "evidence_panel": {"title": "原文证据", "quotes": evidence},
                    "risk_badge": {"show": bool(risk_items), "label": "需核对原文" if risk_items else "", "items": risk_items},
                    "transition": {"type": "chapter" if slide.scene_role in {"intro", "recap"} else "cut", "label": slide.title},
                    "render_profile": course.video_profile,
                },
                "creative_brief": {
                    "engine": "hyperframes" if slide.render_engine in {"hyperframes_creative", "hybrid"} else "remotion",
                    "scene_role": slide.scene_role,
                    "intent": _creative_intent(slide),
                    "style": course.video_profile.get("label", course.title),
                    "title": slide.title,
                    "onscreen_text": slide.body,
                    "subtitle_text": slide.narration[:240],
                    "duration_sec": round(duration, 2),
                    "canvas": {"width": 1920, "height": 1080, "fps": 30},
                    "source_slide_ids": [f"slide-{idx:04d}"],
                    "must_not": ["不要遮挡字幕安全区", "不要改写合规事实", "不要依赖外部网络素材"],
                },
                "visual_generation": {"mode": "codex_demo", "notes": "本地模拟课程素材。"},
                "review_status": "pending",
                "reject_reason": None,
                "risk_flags": list(slide.risk_flags),
                "version": "1",
            }
        )
    manifest = {
        "task_id": course.task_id,
        "course": {"title": course.title, "audience": course.audience, "goal": course.goal, "version": "demo"},
        "assets": [],
        "course_outline": [{"order": i + 1, "title": s.title, "source_scene_id": f"sc-{i:04d}-{s.scene_type}"} for i, s in enumerate(course.slides)],
        "chapters": [{"chapter_id": "demo-chapter", "title": course.title, "scene_ids": [f"sc-{i:04d}-{s.scene_type}" for i, s in enumerate(course.slides)]}],
        "render_intent": {
            "style": course.video_profile.get("id", ""),
            "profile": course.video_profile,
            "visual_policy": "dual_engine_demo",
            "layouts_supported": ["full_slide", "rule_card", "split_panel", "case_dialogue", "summary"],
        },
        "scenes": scenes,
        "review": {"pending_count": len(scenes), "approved_count": 0, "rejected_count": 0, "notes": "demo"},
        "generation": {"planning_mode": "codex_demo_director", "llm_model": "mimo-v2.5-pro if configured, otherwise deterministic demo", "llm_error": "", "material_source": "generated_demo"},
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "quality_checks": {"ok": True, "errors": [], "warnings": [], "error_count": 0, "warning_count": 0},
    }
    path = task_root / "director_manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _creative_intent(slide: DemoSlide) -> str:
    if slide.render_engine == "hyperframes_creative":
        return f"生成完整创意镜头：{slide.title}，使用动态图形、标题节奏和品牌化转场。"
    if slide.render_engine == "hybrid":
        return f"生成叠加动效层：{slide.title}，突出关键词和判断过程，主内容由 Remotion 保留。"
    return "保留原 PPT 证据与字幕节奏，避免艺术化改写高风险信息。"


def _write_audio(course: DemoCourse, report: dict[str, Any]) -> None:
    save_meta_for_workspace(
        "task",
        course.task_id,
        len(course.slides),
        transcript_segments=[[slide.narration] for slide in course.slides],
        transcripts_flat=None,
    )
    cfg = load_raw()
    for idx, slide in enumerate(course.slides):
        entry = {"slide_index": idx, "provider": "", "status": "pending", "errors": []}
        try:
            result = synthesize_speech(
                minimax=cfg.get("minimax") or {},
                tts=cfg.get("tts") or {},
                text=slide.narration,
            )
            rel = workspace_relative_segment_path_unique(idx, 0, slide.narration, result.audio_format, "tts")
            out = workspace_root("task", course.task_id) / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(result.audio_bytes)
            duration = probe_audio_duration_seconds(out)
            if not _valid_audio_file(out, duration):
                raise RuntimeError(f"{result.provider} 返回的音频不可用或时长异常：{out}")
            append_segment_generation("task", course.task_id, idx, 0, rel, duration_sec=duration)
            entry.update(
                {
                    "provider": result.provider,
                    "fallback_used": result.fallback_used,
                    "duration_sec": duration,
                    "rel": rel,
                    "status": "ok",
                    "primary_error": result.primary_error,
                }
            )
        except Exception as exc:
            entry["errors"].append(f"project_tts_failed: {exc}")
            local = _synthesize_with_macos_say(course.task_id, idx, slide.narration)
            if local.get("ok"):
                append_segment_generation(
                    "task",
                    course.task_id,
                    idx,
                    0,
                    str(local["rel"]),
                    duration_sec=local.get("duration_sec"),
                )
                entry.update(
                    {
                        "provider": "macos_say",
                        "fallback_used": True,
                        "duration_sec": local.get("duration_sec"),
                        "rel": local.get("rel"),
                        "status": "ok",
                    }
                )
            else:
                entry["errors"].append(str(local.get("error") or "macos_say_failed"))
                entry["status"] = "failed"
        report["tts"].append(entry)


def _synthesize_with_macos_say(task_id: str, slide_index: int, text: str) -> dict[str, Any]:
    ffmpeg = shutil.which("ffmpeg")
    say = shutil.which("say")
    if not ffmpeg or not say:
        return {"ok": False, "error": "缺少 say 或 ffmpeg，无法生成本地兜底语音"}
    root = workspace_root("task", task_id)
    rel = workspace_relative_segment_path_unique(slide_index, 0, text, "mp3", "say")
    out = root / rel
    aiff = out.with_suffix(".aiff")
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run([say, "-o", str(aiff), text], check=True, capture_output=True, text=True, timeout=60)
        subprocess.run([ffmpeg, "-y", "-i", str(aiff), "-codec:a", "libmp3lame", "-q:a", "4", str(out)], check=True, capture_output=True, text=True, timeout=60)
        duration = probe_audio_duration_seconds(out)
        if not _valid_audio_file(out, duration):
            return {"ok": False, "error": "macOS say 生成的音频无有效时长，可能系统语音资源未就绪"}
        return {"ok": True, "rel": rel, "duration_sec": duration}
    except Exception as exc:
        return {"ok": False, "error": f"macOS say/ffmpeg 失败：{exc}"}
    finally:
        try:
            if aiff.is_file():
                aiff.unlink()
        except OSError:
            pass


def _valid_audio_file(path: Path, duration: float | None) -> bool:
    try:
        size = path.stat().st_size
    except OSError:
        return False
    return bool(duration is not None and duration >= 0.5 and size >= 1024)


def _try_generate_hyperframes_assets(course: DemoCourse, report: dict[str, Any]) -> None:
    renderer_root = Path(__file__).resolve().parent.parent / "ppt_course_renderer"
    task_dir = renderer_root / "render_tasks" / f"task-{course.task_id}"
    plan_path = task_dir / "render_plan.json"
    if not plan_path.is_file():
        report["hyperframes"].append({"status": "skipped", "reason": "render_plan.json 不存在"})
        return
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    tasks = plan.get("hyperframes_tasks") if isinstance(plan.get("hyperframes_tasks"), list) else []
    for item in tasks:
        if not isinstance(item, dict):
            continue
        asset_dir = Path(str(item.get("creative_brief_path") or "")).parent
        clip = asset_dir / "clip.mp4"
        status = {
            "scene_id": item.get("scene_id"),
            "creative_brief_path": item.get("creative_brief_path"),
            "clip_path": str(clip),
            "hyperframes_cli": "not_attempted",
            "fallback_clip": "not_attempted",
        }
        html = asset_dir / "index.html"
        html.write_text(_hyperframes_html(item), encoding="utf-8")
        cli = _attempt_hyperframes_cli(asset_dir)
        status["hyperframes_cli"] = cli
        if not clip.is_file():
            fallback = _render_local_creative_clip(asset_dir, clip)
            status["fallback_clip"] = fallback
        status["clip_exists"] = clip.is_file()
        report["hyperframes"].append(status)


def _hyperframes_html(item: dict[str, Any]) -> str:
    title = str(item.get("scene_id") or "creative-scene")
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    body {{ margin:0; width:1920px; height:1080px; background:#080b14; color:white; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif; }}
    .stage {{ width:100%; height:100%; display:grid; place-items:center; background: radial-gradient(circle at 30% 30%, #ef444455, transparent 35%), #080b14; }}
    h1 {{ font-size:88px; max-width:1280px; text-align:center; }}
  </style>
</head>
<body>
  <main class="stage" data-start="0" data-duration="4">
    <h1>{title}</h1>
  </main>
</body>
</html>
"""


def _attempt_hyperframes_cli(asset_dir: Path) -> dict[str, Any]:
    npx = shutil.which("npx")
    if not npx:
        return {"status": "failed", "reason": "npx 不存在"}
    cmd = [npx, "hyperframes", "render", "index.html", "clip.mp4"]
    result = _run_captured_process(cmd, cwd=asset_dir, timeout=25)
    return {
        "status": "ok" if result["returncode"] == 0 else "failed",
        "cmd": " ".join(cmd),
        "returncode": result["returncode"],
        "stdout": result["stdout"][-2000:],
        "stderr": result["stderr"][-4000:],
        "reason": result.get("reason", ""),
    }


def _render_local_creative_clip(asset_dir: Path, clip: Path) -> dict[str, Any]:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return {"status": "failed", "reason": "ffmpeg 不存在"}
    png = asset_dir / "fallback_frame.png"
    try:
        brief_path = asset_dir / "creative_brief.json"
        brief = json.loads(brief_path.read_text(encoding="utf-8")) if brief_path.is_file() else {}
        img = Image.new("RGB", (1920, 1080), "#080b14")
        draw = ImageDraw.Draw(img)
        title_font = _font(72, bold=True)
        body_font = _font(34)
        draw.rounded_rectangle((90, 90, 1830, 990), radius=40, fill=(10, 18, 36), outline="#ef4444", width=5)
        draw.ellipse((1260, 80, 2020, 840), fill="#ef444433")
        draw.ellipse((-220, 460, 480, 1160), fill="#38bdf833")
        title = str(brief.get("title") or "创意镜头")
        intent = str(brief.get("intent") or "Hyperframes 不可用，使用本地创意片段兜底。")
        draw.text((160, 260), title, fill="#ffffff", font=title_font)
        y = 390
        for line in _wrap_text(draw, intent, body_font, 1200)[:4]:
            draw.text((160, y), line, fill="#cbd5e1", font=body_font)
            y += 52
        draw.text((160, 850), "LOCAL CREATIVE FALLBACK · Remotion will embed this clip", fill="#fca5a5", font=body_font)
        img.save(png, "PNG")
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-loop",
                "1",
                "-i",
                str(png),
                "-t",
                "4",
                "-vf",
                "scale=1920:1080,format=yuv420p",
                "-r",
                "30",
                "-pix_fmt",
                "yuv420p",
                str(clip),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=90,
        )
        return {"status": "ok", "reason": "Hyperframes 不可用时生成本地创意片段，供 Remotion 嵌入验证流程"}
    except Exception as exc:
        return {"status": "failed", "reason": str(exc)}


def _render_with_remotion(course: DemoCourse, report: dict[str, Any]) -> None:
    renderer_root = Path(__file__).resolve().parent.parent / "ppt_course_renderer"
    task_name = f"task-{course.task_id}"
    cmd = [
        "npx",
        "remotion",
        "render",
        "src/index.ts",
        "CourseDeck",
        f"render_tasks/{task_name}/out/video.mp4",
        "--props",
        f"render_tasks/{task_name}/input-props.json",
    ]
    result = _run_captured_process(cmd, cwd=renderer_root, timeout=600)
    out = renderer_root / "render_tasks" / task_name / "out" / "video.mp4"
    report["remotion"] = {
        "cmd": " ".join(cmd),
        "returncode": result["returncode"],
        "stdout": result["stdout"][-4000:],
        "stderr": result["stderr"][-6000:],
        "error": result.get("reason", ""),
        "output_video_path": str(out),
        "output_video_exists": out.is_file(),
        "output_video_size_bytes": out.stat().st_size if out.is_file() else 0,
    }


def _safe_subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    for key in list(env):
        upper = key.upper()
        if any(marker in upper for marker in SENSITIVE_ENV_MARKERS):
            env.pop(key, None)
    return env


def _run_captured_process(cmd: list[str], *, cwd: Path, timeout: int) -> dict[str, Any]:
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
        env=_safe_subprocess_env(),
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        return {"returncode": proc.returncode, "stdout": stdout or "", "stderr": stderr or "", "reason": ""}
    except subprocess.TimeoutExpired:
        _terminate_process_group(proc.pid)
        try:
            stdout, stderr = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            _kill_process_group(proc.pid)
            stdout, stderr = proc.communicate()
        return {
            "returncode": -9,
            "stdout": stdout or "",
            "stderr": stderr or "",
            "reason": f"命令超过 {timeout}s 未完成，已结束进程组并使用 fallback。",
        }


def _terminate_process_group(pid: int) -> None:
    try:
        os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    except OSError:
        return


def _kill_process_group(pid: int) -> None:
    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    except OSError:
        return
