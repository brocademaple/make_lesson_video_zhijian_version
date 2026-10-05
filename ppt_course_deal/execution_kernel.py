"""Local-first execution kernel for any2video V0.4.

The kernel keeps engine decisions, capability discovery, creative-scene source
artifacts, and an append-friendly run ledger independent from the web UI.
"""

from __future__ import annotations

import html
import json
import os
import re
import shutil
import time
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4


ENGINE_AUTO = "auto"
ENGINE_REMOTION = "remotion"
ENGINE_HYPERFRAMES = "hyperframes"
ENGINE_HYBRID = "hybrid"
VALID_ENGINES = {
    ENGINE_AUTO,
    ENGINE_REMOTION,
    ENGINE_HYPERFRAMES,
    ENGINE_HYBRID,
}


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_suffix(path.suffix + ".tmp")
    pending.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    pending.replace(path)


def read_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _binary(path: Path) -> Optional[str]:
    return str(path) if path.is_file() and os.access(path, os.X_OK) else None


def discover_capabilities(renderer_root: Path, workspace: Path) -> dict[str, Any]:
    remotion = _binary(renderer_root / "node_modules" / ".bin" / "remotion")
    hyperframes = (
        _binary(renderer_root / "node_modules" / ".bin" / "hyperframes")
        or shutil.which("hyperframes")
    )
    npx = shutil.which("npx")
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    capabilities = [
        {
            "id": "storage.local",
            "kind": "storage",
            "status": "ready",
            "executable": True,
            "reason": f"项目与运行账本保存在 {workspace}",
        },
        {
            "id": "remotion.render_project",
            "kind": "renderer",
            "status": "ready" if remotion else "unavailable",
            "executable": bool(remotion),
            "reason": "本机 Remotion 已安装" if remotion else "未找到本机 Remotion CLI",
            "command": remotion or "",
        },
        {
            "id": "hyperframes.render_scene",
            "kind": "renderer",
            "status": "ready" if hyperframes else ("on_demand" if npx else "unavailable"),
            "executable": bool(hyperframes),
            "reason": (
                "本机 HyperFrames CLI 已安装"
                if hyperframes
                else ("可由 npx 按需执行；默认只准备创意任务" if npx else "未找到 HyperFrames CLI 或 npx")
            ),
            "command": hyperframes or "",
            "on_demand_command": (
                f"{npx} --yes --package=hyperframes --package=is-inside-container hyperframes"
                if npx and not hyperframes
                else ""
            ),
        },
        {
            "id": "media.ffmpeg",
            "kind": "media",
            "status": "ready" if ffmpeg else "unavailable",
            "executable": bool(ffmpeg),
            "reason": "FFmpeg 可用" if ffmpeg else "未找到 FFmpeg",
            "command": ffmpeg or "",
        },
        {
            "id": "media.ffprobe",
            "kind": "verification",
            "status": "ready" if ffprobe else "unavailable",
            "executable": bool(ffprobe),
            "reason": "FFprobe 可用" if ffprobe else "未找到 FFprobe",
            "command": ffprobe or "",
        },
    ]
    return {
        "schema_version": "capability_registry.v1",
        "local_first": True,
        "generated_at": now_iso(),
        "capabilities": capabilities,
    }


def capability_by_id(registry: dict[str, Any], capability_id: str) -> dict[str, Any]:
    for item in registry.get("capabilities") or []:
        if isinstance(item, dict) and item.get("id") == capability_id:
            return item
    return {}


def hyperframes_command(registry: dict[str, Any], allow_on_demand: bool = False) -> list[str]:
    item = capability_by_id(registry, "hyperframes.render_scene")
    command = str(item.get("command") or "").strip()
    if command:
        return [command]
    if allow_on_demand:
        raw = str(item.get("on_demand_command") or "").strip()
        if raw:
            return raw.split()
    return []


def _scene_text(scene: dict[str, Any]) -> str:
    return " ".join(
        str(scene.get(key) or "")
        for key in ("title", "purpose", "onscreen_text", "narration", "subtitle")
    )


def _risk_reason(scene: dict[str, Any]) -> str:
    text = _scene_text(scene)
    if re.search(r"(处罚|罚款|金额|合同|合规|红线|法律|医疗|诊断|不得|禁止)", text):
        return "包含合规、处罚或高风险事实，需要稳定模板保留信息边界"
    if re.search(r"(?:\d+[,.]?\d*)\s*(?:元|万|%|％|美元|人民币)", text):
        return "包含金额或比例，优先使用可审计的稳定模板"
    return ""


def route_scene_engine(scene: dict[str, Any], index: int, total: int) -> dict[str, str]:
    requested = str(scene.get("renderer") or ENGINE_AUTO).strip().lower()
    if requested not in VALID_ENGINES:
        requested = ENGINE_AUTO
    if requested != ENGINE_AUTO:
        return {
            "requested": requested,
            "resolved": requested,
            "reason": "导演手动指定渲染引擎",
            "fallback": ENGINE_REMOTION if requested != ENGINE_REMOTION else "",
        }

    risk = _risk_reason(scene)
    if risk:
        return {
            "requested": ENGINE_AUTO,
            "resolved": ENGINE_REMOTION,
            "reason": risk,
            "fallback": "",
        }
    if index == 0:
        return {
            "requested": ENGINE_AUTO,
            "resolved": ENGINE_HYPERFRAMES,
            "reason": "首镜需要建立视觉识别，适合创意动效",
            "fallback": ENGINE_REMOTION,
        }
    if total >= 3 and index == total - 1:
        return {
            "requested": ENGINE_AUTO,
            "resolved": ENGINE_HYPERFRAMES,
            "reason": "收束镜头适合强化结论与品牌记忆",
            "fallback": ENGINE_REMOTION,
        }
    purpose = str(scene.get("purpose") or "")
    if re.search(r"(流程|步骤|对比|解释|结构|机制|关系|演示)", purpose):
        return {
            "requested": ENGINE_AUTO,
            "resolved": ENGINE_HYBRID,
            "reason": "概念或流程镜头适合创意层与稳定信息层叠加",
            "fallback": ENGINE_REMOTION,
        }
    return {
        "requested": ENGINE_AUTO,
        "resolved": ENGINE_REMOTION,
        "reason": "内容镜头优先保证素材、字幕和时间线稳定",
        "fallback": "",
    }


def apply_scene_routes(scenes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    total = len(scenes)
    for index, scene in enumerate(scenes):
        previous = scene.get("engine") if isinstance(scene.get("engine"), dict) else {}
        route = route_scene_engine(scene, index, total)
        changed = previous.get("resolved") != route["resolved"]
        status = str(previous.get("status") or "pending")
        if route["resolved"] == ENGINE_REMOTION:
            status = "ready"
        elif changed or status not in {"ready", "prepared", "fallback"}:
            status = "pending"
        scene["renderer"] = route["requested"]
        scene["engine"] = {
            **route,
            "status": status,
            "capability": (
                "hyperframes.render_scene"
                if route["resolved"] in {ENGINE_HYPERFRAMES, ENGINE_HYBRID}
                else "remotion.render_project"
            ),
            "artifact": previous.get("artifact") if not changed else None,
            "last_run_id": previous.get("last_run_id") if not changed else None,
            "error": previous.get("error") if not changed else "",
        }
    return scenes


def runs_dir(project_root: Path) -> Path:
    return project_root / "runs"


def create_run(
    project_root: Path,
    project_id: str,
    kind: str,
    step_ids: list[str],
    metadata: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    run_id = f"run-{uuid4().hex[:12]}"
    created = now_iso()
    run = {
        "schema_version": "execution_run.v1",
        "id": run_id,
        "project_id": project_id,
        "kind": kind,
        "status": "running",
        "created_at": created,
        "started_at": created,
        "finished_at": None,
        "metadata": metadata or {},
        "steps": [
            {"id": step_id, "status": "pending", "detail": "", "artifact": None}
            for step_id in step_ids
        ],
        "artifacts": [],
        "error": "",
    }
    write_json(runs_dir(project_root) / f"{run_id}.json", run)
    return run


def save_run(project_root: Path, run: dict[str, Any]) -> dict[str, Any]:
    write_json(runs_dir(project_root) / f"{run['id']}.json", run)
    return run


def update_run_step(
    project_root: Path,
    run: dict[str, Any],
    step_id: str,
    status: str,
    *,
    detail: str = "",
    artifact: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    for step in run.get("steps") or []:
        if step.get("id") != step_id:
            continue
        step["status"] = status
        step["detail"] = detail
        if status == "running" and not step.get("started_at"):
            step["started_at"] = now_iso()
        if status in {"ready", "failed", "fallback", "skipped"}:
            step["finished_at"] = now_iso()
        if artifact:
            step["artifact"] = artifact
            run.setdefault("artifacts", []).append(artifact)
        break
    return save_run(project_root, run)


def finish_run(
    project_root: Path,
    run: dict[str, Any],
    status: str,
    error: str = "",
) -> dict[str, Any]:
    run["status"] = status
    run["error"] = error
    run["finished_at"] = now_iso()
    return save_run(project_root, run)


def list_runs(project_root: Path, limit: int = 20) -> list[dict[str, Any]]:
    root = runs_dir(project_root)
    if not root.is_dir():
        return []
    items = []
    for path in root.glob("run-*.json"):
        data = read_json(path, None)
        if isinstance(data, dict):
            items.append(data)
    items.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
    return items[: max(1, limit)]


def _safe_id(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-")
    return cleaned or "scene"


def write_hyperframes_scene(
    target_dir: Path,
    project: dict[str, Any],
    scene: dict[str, Any],
    image_path: Optional[Path],
    *,
    width: int,
    height: int,
    fps: int,
) -> dict[str, Any]:
    target_dir.mkdir(parents=True, exist_ok=True)
    duration = max(0.5, float(scene.get("duration_sec") or 4))
    title = str(scene.get("title") or "未命名镜头")
    onscreen = str(scene.get("onscreen_text") or title)
    purpose = str(scene.get("purpose") or "创意镜头")
    composition_id = _safe_id(str(scene.get("id") or "scene"))
    source_name = ""
    if image_path and image_path.is_file():
        source_name = "source" + image_path.suffix.lower()
        shutil.copy2(image_path, target_dir / source_name)
    background = (
        f"linear-gradient(180deg,rgba(6,9,16,.16),rgba(6,9,16,.9)),url('{source_name}') center/cover"
        if source_name
        else "radial-gradient(circle at 70% 15%,#315fc5 0,transparent 34%),#080b12"
    )
    brief = {
        "schema_version": "creative_brief.v1",
        "project_id": project.get("id"),
        "scene_id": scene.get("id"),
        "title": title,
        "onscreen_text": onscreen,
        "purpose": purpose,
        "duration_sec": duration,
        "canvas": {"width": width, "height": height, "fps": fps},
        "engine": dict(scene.get("engine") or {}),
        "source_image": source_name,
    }
    write_json(target_dir / "creative_brief.json", brief)
    (target_dir / "DESIGN.md").write_text(
        "# Any2Video V0.4 Creative Scene\n\n"
        "## Style Prompt\n"
        "Quiet cinematic editorial frame with deep ink surfaces, cobalt signal color, warm white typography, and deliberate motion.\n\n"
        "## Colors\n"
        "- Background: #080B12\n- Ink: #F7F8FA\n- Muted: #A7B0C0\n- Accent: #315FC5\n\n"
        "## Typography\n"
        "- SF Pro Display, PingFang SC, system sans-serif\n\n"
        "## What NOT to Do\n"
        "- No rainbow gradients\n- No excessive glow\n- No random motion\n- No tiny text\n",
        encoding="utf-8",
    )
    document = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width={width},height={height}" />
  <title>{html.escape(title)}</title>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <style>
    @font-face {{ font-family: "PingFang SC"; src: local("PingFang SC"); }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; width: 100%; height: 100%; overflow: hidden; background: #080b12; }}
    #stage {{ position: relative; width: 100%; height: 100%; overflow: hidden; color: #f7f8fa; font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "PingFang SC", sans-serif; }}
    .scene {{ position: absolute; inset: 0; overflow: hidden; background: {background}; }}
    .scene::after {{ content: ""; position: absolute; inset: 0; background: radial-gradient(circle at 24% 18%, rgba(49,95,197,.32), transparent 30%); }}
    .scene-content {{ position: relative; z-index: 2; display: flex; flex-direction: column; justify-content: flex-end; width: 100%; height: 100%; padding: 12% 9%; gap: 30px; }}
    .eyebrow {{ color: #a7b0c0; font-size: {max(24, round(width * .027))}px; font-weight: 600; letter-spacing: .08em; }}
    .title {{ max-width: 88%; margin: 0; font-size: {max(64, round(width * .09))}px; line-height: 1.04; letter-spacing: -.045em; text-wrap: balance; }}
    .rule {{ width: 22%; height: 8px; border-radius: 99px; background: #315fc5; }}
    .index {{ position: absolute; top: 7%; right: 8%; z-index: 2; color: rgba(247,248,250,.64); font-size: {max(20, round(width * .022))}px; font-variant-numeric: tabular-nums; }}
  </style>
</head>
<body>
  <div id="stage" data-composition-id="{composition_id}" data-start="0" data-duration="{duration:.3f}" data-width="{width}" data-height="{height}">
    <section id="scene-main" class="scene clip" data-start="0" data-duration="{duration:.3f}" data-track-index="0">
      <div class="index">ANY2VIDEO · V0.4</div>
      <div class="scene-content" data-layout-allow-overflow>
        <div class="eyebrow">{html.escape(purpose)}</div>
        <h1 class="title">{html.escape(onscreen)}</h1>
        <div class="rule"></div>
      </div>
    </section>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{paused: true}});
    tl.from('.eyebrow', {{y: 34, opacity: 0, duration: .55, ease: 'power2.out'}}, .18);
    tl.from('.title', {{y: 64, opacity: 0, duration: .75, ease: 'power3.out'}}, .32);
    tl.from('.rule', {{scaleX: 0, transformOrigin: 'left', duration: .65, ease: 'expo.out'}}, .68);
    tl.from('.index', {{x: 28, opacity: 0, duration: .45, ease: 'back.out(1.4)'}}, .24);
    tl.to('.scene', {{backgroundPosition: '52% 50%', duration: {max(1.0, duration - .4):.3f}, ease: 'none'}}, .2);
    tl.to('.scene-content', {{opacity: 0, y: -24, duration: .28, ease: 'power2.in'}}, {max(.4, duration - .32):.3f});
    window.__timelines['{composition_id}'] = tl;
  </script>
</body>
</html>
"""
    (target_dir / "index.html").write_text(document, encoding="utf-8")
    manifest = {
        "schema_version": "hyperframes_asset.v2",
        "project_id": project.get("id"),
        "scene_id": scene.get("id"),
        "status": "prepared",
        "engine": dict(scene.get("engine") or {}),
        "source_html": str(target_dir / "index.html"),
        "creative_brief_path": str(target_dir / "creative_brief.json"),
        "clip_path": str(target_dir / "clip.mp4"),
        "created_at": now_iso(),
    }
    write_json(target_dir / "asset_manifest.json", manifest)
    return manifest
