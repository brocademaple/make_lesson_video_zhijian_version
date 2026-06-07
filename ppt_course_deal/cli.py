from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from ppt_course_deal import __version__
from ppt_course_deal.pipeline import transform_pptx

app = typer.Typer(
    name="ppt-course",
    help="个人影像工坊：素材入仓、导演脚本、声音轨与 Remotion 成片",
    no_args_is_help=True,
    invoke_without_command=True,
)


@app.callback()
def _cli(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="显示版本号"),
) -> None:
    if version:
        typer.echo(__version__)
        raise typer.Exit(0)
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


@app.command("transform")
def cmd_transform(
    input_pptx: Path = typer.Argument(..., help="输入的原始 .pptx 文件路径", exists=True),
    output: Optional[Path] = typer.Option(
        None,
        "-o",
        "--output",
        help="输出路径；默认与输入同目录，文件名加 _course 后缀",
    ),
    plan_json: Optional[Path] = typer.Option(
        None,
        "--plan-json",
        help="可选：将规划结果写入 JSON，便于对接 AI / 自动化",
    ),
) -> None:
    """将整份 PPT 转换为课程向新版式 PPTX。"""
    out = output
    if out is None:
        out = input_pptx.with_name(f"{input_pptx.stem}_course{input_pptx.suffix}")

    result = transform_pptx(
        input_pptx,
        out,
        dump_plan_json=plan_json,
    )
    typer.secho(
        f"完成：源 {result.source_slide_count} 页 → 输出 {result.output_slide_count} 页\n"
        f"已保存：{result.output_path}",
        fg=typer.colors.GREEN,
    )


@app.command("serve")
def cmd_serve(
    host: str = typer.Option(
        "127.0.0.1",
        "--host",
        help="监听地址；局域网访问可设为 0.0.0.0",
    ),
    port: int = typer.Option(8765, "--port", "-p", help="端口"),
    reload: bool = typer.Option(
        True,
        "--reload/--no-reload",
        help="代码变更后自动重载（默认开启，避免新增接口后仍跑旧进程导致 404）；常驻可无 --no-reload",
    ),
) -> None:
    """启动个人影像工坊 Web 工作台。"""
    try:
        import uvicorn
    except ImportError as e:
        typer.secho(
            "缺少依赖：请执行 pip install uvicorn[standard] fastapi python-multipart",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1) from e

    typer.echo(f"Web UI：http://{host}:{port}/")
    try:
        from ppt_course_deal.slide_render import describe_preview_render_env

        if not describe_preview_render_env().get("ready"):
            typer.secho(
                "提示：整页幻灯片预览需本机安装 LibreOffice 与 Poppler（pdftoppm）；"
                "macOS 示例：brew install --cask libreoffice && brew install poppler，安装后重启服务。"
                "详见 README「整页预览图」。",
                fg=typer.colors.YELLOW,
            )
    except Exception:
        pass

    uvicorn.run(
        "ppt_course_deal.web.app:app",
        host=host,
        port=port,
        reload=reload,
    )


@app.command("remotion-input-props")
def cmd_remotion_input_props(
    task_id: str = typer.Argument(..., help="作品项目 task_id"),
    output: Path = typer.Option(
        ...,
        "-o",
        "--output",
        help="输出的 input-props.json 路径",
    ),
    fps: int = typer.Option(30, "--fps", help="与 Remotion Composition 的 fps 一致"),
    max_slides: Optional[int] = typer.Option(
        None,
        "--max-slides",
        help="最多导出前几页（默认该任务全部页）",
    ),
    no_audio_frames: int = typer.Option(
        90,
        "--no-audio-frames",
        help="某页尚无分段 mp3 时的占位帧数",
    ),
    workspace_root: Optional[Path] = typer.Option(
        None,
        "-w",
        "--workspace-root",
        help="REMOTION_WORKSPACE_ROOT（默认仓库根）；数据目录在仓库外时请指定",
    ),
    bundle_audio: bool = typer.Option(
        False,
        "--bundle-audio/--no-bundle-audio",
        help="把 audio_workspace 已落盘的 mp3 复制到 tasks/<task_id>/audio/，JSON 中引用任务内路径（MiniMax 外链短效；此处为本地持久副本）",
    ),
) -> None:
    """根据任务预览与音频工作台生成 Remotion `input-props.json`（路径相对仓库根）。"""
    from ppt_course_deal.remotion_input_props import write_props_file

    try:
        write_props_file(
            task_id,
            output,
            fps=fps,
            max_slides=max_slides,
            no_audio_frames=no_audio_frames,
            remotion_workspace_root=workspace_root,
            bundle_audio=bundle_audio,
        )
    except ValueError as e:
        typer.secho(str(e), fg=typer.colors.RED)
        raise typer.Exit(1) from e
    typer.secho(f"已写入 {output}", fg=typer.colors.GREEN)


@app.command("bundle-task-audio")
def cmd_bundle_task_audio(
    task_id: str = typer.Argument(..., help="作品项目 task_id"),
    max_slides: Optional[int] = typer.Option(
        None,
        "--max-slides",
        help="仅复制前几页的音频（默认全部页）",
    ),
) -> None:
    """将 audio_workspace 内该任务的 mp3 复制到 tasks/<task_id>/audio/（与 remotion-input-props --bundle-audio 同源）。"""
    from ppt_course_deal.task_audio_bundle import mirror_workspace_mp3_to_task_bundle

    try:
        n, paths = mirror_workspace_mp3_to_task_bundle(task_id, max_slides=max_slides)
    except ValueError as e:
        typer.secho(str(e), fg=typer.colors.RED)
        raise typer.Exit(1) from e
    typer.secho(f"已复制 {n} 个文件到 ppt_course_data/tasks/{task_id}/audio/", fg=typer.colors.GREEN)
    for p in paths[:12]:
        typer.echo(f"  {p}")
    if len(paths) > 12:
        typer.echo(f"  … 共 {len(paths)} 个")


@app.command("rebuild-director")
def cmd_rebuild_director(
    task_id: str = typer.Argument(..., help="作品项目 task_id"),
    output: Optional[Path] = typer.Option(
        None,
        "-o",
        "--output",
        help="导演脚本输出路径；默认写入任务目录 director_manifest.json",
    ),
    llm: bool = typer.Option(
        True,
        "--llm/--no-llm",
        help="启用百炼/OpenAI-compatible LLM 规划；失败会自动回退启发式",
    ),
    llm_max_slides: Optional[int] = typer.Option(
        None,
        "--llm-max-slides",
        min=1,
        help="LLM 最多读取前几页原始素材；默认读取该任务全部页",
    ),
) -> None:
    """从作品项目生成 raw_material_manifest，并调用 rebuilder 写出 director_manifest。"""
    from ppt_course_deal.raw_material_manifest import build_raw_material_manifest
    from ppt_course_rebuilder.director import rebuild_course_from_raw_manifest

    try:
        raw = build_raw_material_manifest(task_id)
    except ValueError as e:
        typer.secho(str(e), fg=typer.colors.RED)
        raise typer.Exit(1) from e

    task_root = Path(str(raw.get("task_root") or ""))
    raw_path = task_root / "raw_material_manifest.json"
    out_path = output or (task_root / "director_manifest.json")
    options: dict[str, object] = {"use_llm": llm}
    if llm_max_slides is not None:
        options["llm_max_slides"] = llm_max_slides

    dm = rebuild_course_from_raw_manifest(
        str(raw_path),
        str(out_path),
        options=options,
    )
    generation = dm.get("generation") or {}
    planning_mode = generation.get("planning_mode") or "unknown"
    typer.secho(f"已写入 {out_path}", fg=typer.colors.GREEN)
    typer.echo(
        f"规划模式：{planning_mode}；课程标题：{(dm.get('course') or {}).get('title') or ''}；"
        f"镜头数：{len(dm.get('scenes') or [])}"
    )
    if generation.get("llm_error"):
        typer.secho(f"LLM 回退原因：{generation['llm_error']}", fg=typer.colors.YELLOW)


@app.command("course-material")
def cmd_course_material(
    task_id: str = typer.Argument(..., help="作品项目 task_id"),
    output: Optional[Path] = typer.Option(
        None,
        "-o",
        "--output",
        help="输出路径；默认写入任务目录 course_material.json",
    ),
    use_llm: bool = typer.Option(
        False,
        "--llm/--no-llm",
        help="是否使用 director_llm 对素材角色做增强标记；默认关闭以便离线稳定运行",
    ),
) -> None:
    """生成 Rebuilder 的 course_material.json 中间层。"""
    from ppt_course_deal.raw_material_manifest import build_raw_material_manifest
    from ppt_course_rebuilder.material_normalizer import build_course_material

    try:
        raw = build_raw_material_manifest(task_id)
    except ValueError as e:
        typer.secho(str(e), fg=typer.colors.RED)
        raise typer.Exit(1) from e
    task_root = Path(str(raw.get("task_root") or ""))
    raw_path = task_root / "raw_material_manifest.json"
    out_path = output or (task_root / "course_material.json")
    material = build_course_material(raw_path, out_path, use_llm=use_llm)
    typer.secho(f"已写入 {out_path}", fg=typer.colors.GREEN)
    typer.echo(
        f"页数：{len(material.get('slides') or [])}；素材数：{len(material.get('assets') or [])}"
    )


@app.command("remotion-render-plan")
def cmd_remotion_render_plan(
    task_id: str = typer.Argument(..., help="作品项目 task_id"),
    fps: int = typer.Option(30, "--fps", help="与 Remotion Composition 的 fps 一致"),
    max_slides: Optional[int] = typer.Option(
        None,
        "--max-slides",
        min=1,
        help="最多导出前几个导演镜头/页面（默认该任务全部镜头）",
    ),
    no_audio_frames: int = typer.Option(
        90,
        "--no-audio-frames",
        help="镜头尚无分段 mp3 时的占位帧数",
    ),
) -> None:
    """由 approved/director manifest 生成 render_plan.json 与 input-props.json。"""
    from ppt_course_rebuilder.render_adapter import write_render_plan_from_task

    try:
        data = write_render_plan_from_task(
            task_id,
            fps=fps,
            no_audio_frames=no_audio_frames,
            max_scenes=max_slides,
        )
    except ValueError as e:
        typer.secho(str(e), fg=typer.colors.RED)
        raise typer.Exit(1) from e
    typer.secho(f"已写入 {data.get('input_props_path')}", fg=typer.colors.GREEN)
    if data.get("render_plan_path"):
        typer.echo(f"Render Plan：{data['render_plan_path']}")
    typer.echo(f"来源：{data.get('source') or 'fallback'}")
    if data.get("hyperframes_task_count") is not None:
        typer.echo(
            "Hyperframes 创意任务："
            f"{data.get('creative_asset_ready_count', 0)} / {data.get('hyperframes_task_count', 0)} 已就绪"
        )
    typer.echo(data.get("render_command") or "")


@app.command("hyperframes-tasks")
def cmd_hyperframes_tasks(
    task_id: str = typer.Argument(..., help="作品项目 task_id"),
    fps: int = typer.Option(30, "--fps", help="与最终 Remotion Composition 的 fps 一致"),
    max_slides: Optional[int] = typer.Option(
        None,
        "--max-slides",
        min=1,
        help="最多导出前几个导演镜头/页面（默认该任务全部镜头）",
    ),
    no_audio_frames: int = typer.Option(
        90,
        "--no-audio-frames",
        help="镜头尚无分段 mp3 时的占位帧数",
    ),
) -> None:
    """生成 render_plan.v2 并列出需要 Hyperframes 生产的创意资产任务。"""
    from ppt_course_rebuilder.render_adapter import write_render_plan_from_task

    try:
        data = write_render_plan_from_task(
            task_id,
            fps=fps,
            no_audio_frames=no_audio_frames,
            max_scenes=max_slides,
        )
    except ValueError as e:
        typer.secho(str(e), fg=typer.colors.RED)
        raise typer.Exit(1) from e
    typer.secho(f"已写入 {data.get('render_plan_path')}", fg=typer.colors.GREEN)
    typer.echo(
        "Hyperframes 创意任务："
        f"{data.get('creative_asset_ready_count', 0)} / {data.get('hyperframes_task_count', 0)} 已就绪"
    )
    typer.echo("creative_brief.json 与 asset_manifest.json 位于 render_tasks/<task>/creative_assets/<scene>/")


@app.command("demo-dual-engine")
def cmd_demo_dual_engine(
    render: bool = typer.Option(
        True,
        "--render/--no-render",
        help="是否调用 Remotion 渲染最终 MP4",
    ),
    try_hyperframes: bool = typer.Option(
        True,
        "--try-hyperframes/--no-try-hyperframes",
        help="是否尝试调用 Hyperframes CLI；失败会记录并使用本地创意片段兜底",
    ),
) -> None:
    """生成两个双引擎课程视频 demo 任务，并写入本地任务系统。"""
    from ppt_course_deal.demo_dual_engine import generate_dual_engine_demo_tasks

    result = generate_dual_engine_demo_tasks(
        render=render,
        try_hyperframes=try_hyperframes,
    )
    for item in result.get("tasks") or []:
        status = "完成" if item.get("ok") else "有问题"
        typer.echo(f"{status}：{item.get('slug')} / {item.get('task_id')}")
        typer.echo(f"报告：{item.get('report_path')}")
        remotion = item.get("remotion") or {}
        if remotion.get("output_video_path"):
            typer.echo(f"视频：{remotion.get('output_video_path')}")
    if not result.get("ok"):
        raise typer.Exit(1)


@app.command("import-pdf-task")
def cmd_import_pdf_task(
    pdf_path: Path = typer.Argument(..., help="输入 PDF 文件路径", exists=True),
    name: Optional[str] = typer.Option(None, "--name", help="项目库中显示的名称"),
    max_pages: int = typer.Option(16, "--max-pages", help="最多导入多少页；0 表示全部页"),
    profile: str = typer.Option("training", "--profile", help="视频画像：knowledge/product/training/quality 等；旧 onboarding/sales 仍兼容"),
    no_director: bool = typer.Option(False, "--no-director", help="只导入项目，不生成导演脚本"),
    no_render_plan: bool = typer.Option(False, "--no-render-plan", help="不生成 Remotion render_plan/input-props"),
) -> None:
    """将 PDF 导入为作品项目，并生成预览图、素材清单与导演计划。"""
    from ppt_course_deal.pdf_task_importer import import_pdf_task

    result = import_pdf_task(
        pdf_path,
        display_name=name,
        max_pages=None if max_pages <= 0 else max_pages,
        video_profile_id=profile,
        build_director=not no_director,
        build_render_plan=not no_render_plan,
    )
    typer.secho(f"已导入 PDF 项目：{result['task_id']}", fg=typer.colors.GREEN)
    typer.echo(f"项目目录：{result['task_root']}")
    typer.echo(f"页数：{result['slide_count']}")
    if result.get("render_plan_path"):
        typer.echo(f"Render Plan：{result['render_plan_path']}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
