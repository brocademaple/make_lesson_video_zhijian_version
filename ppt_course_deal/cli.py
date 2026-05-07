from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from ppt_course_deal import __version__
from ppt_course_deal.pipeline import transform_pptx

app = typer.Typer(
    name="ppt-course",
    help="PPT 课程化重构：文字密集型培训 PPT → 适合录课的结构化 PPTX（MVP）",
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
        False,
        "--reload",
        help="开发模式：代码变更后自动重载（仅本机调试）",
    ),
) -> None:
    """启动 Web 界面：浏览器上传 PPTX，下载课程化 PPTX。"""
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


def main() -> None:
    app()


if __name__ == "__main__":
    main()
