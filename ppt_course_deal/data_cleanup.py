"""Safe cleanup of any2video runtime project data.

Configuration, connection logs, checked-in examples, and environment files are
outside the allowlist and are never touched by this module.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class CleanupTarget:
    label: str
    path: Path
    keep_names: frozenset[str] = frozenset()


def cleanup_targets(repo_root: Path = REPO_ROOT) -> tuple[CleanupTarget, ...]:
    root = repo_root.resolve()
    data = root / "ppt_course_data"
    renderer = root / "ppt_course_renderer"
    targets = [
        CleanupTarget("旧 PPT 项目", data / "tasks"),
        CleanupTarget("旧声音工作区", data / "audio_workspace"),
        CleanupTarget("旧 MVP 运行记录", data / "mvp_runs"),
        CleanupTarget("导入源文件", data / "import_sources"),
        CleanupTarget("公共素材缓存", data / "public_sources"),
        CleanupTarget("any2video 项目", root / "video_workspace" / "projects"),
        CleanupTarget(
            "Remotion 运行任务",
            renderer / "render_tasks",
            frozenset(
                {
                    ".gitignore",
                    "README.md",
                    "my-video-test1",
                    "task-2555-pages1-4",
                    "product-experience-demo",
                }
            ),
        ),
        CleanupTarget("Remotion 素材副本", renderer / "public" / "v2_assets"),
    ]
    public_outputs = renderer / "public" / "render_tasks"
    render_tasks = renderer / "render_tasks"
    # The repository may expose render_tasks through this tracked symlink.
    # Its contents are already handled by the primary render_tasks target.
    if not (public_outputs.is_symlink() and public_outputs.resolve() == render_tasks.resolve()):
        targets.append(CleanupTarget("Remotion 输出副本", public_outputs))
    return tuple(targets)


def _assert_safe_target(repo_root: Path, target: CleanupTarget) -> None:
    root = repo_root.resolve()
    raw = target.path
    if raw.is_symlink():
        raise RuntimeError(f"目标是符号链接：{raw}")
    resolved = raw.resolve(strict=False)
    if resolved == root or root not in resolved.parents:
        raise RuntimeError(f"目标不在仓库目录内：{raw}")
    if raw.exists():
        for child in raw.rglob("*"):
            if child.is_symlink():
                raise RuntimeError(f"目标内包含符号链接：{child}")


def _entries(target: CleanupTarget) -> Iterable[Path]:
    if not target.path.is_dir():
        return ()
    return tuple(
        child for child in target.path.iterdir() if child.name not in target.keep_names
    )


def _measure(entries: Iterable[Path]) -> tuple[int, int]:
    count = 0
    size = 0
    for entry in entries:
        if entry.is_file():
            count += 1
            size += entry.stat().st_size
            continue
        for child in entry.rglob("*"):
            if child.is_file():
                count += 1
                size += child.stat().st_size
    return count, size


def cleanup_project_data(
    *, execute: bool = False, repo_root: Path = REPO_ROOT
) -> dict[str, object]:
    """Return a cleanup report and optionally remove only allowlisted entries."""
    root = repo_root.resolve()
    reports: list[dict[str, object]] = []
    pending: list[tuple[CleanupTarget, tuple[Path, ...]]] = []

    for target in cleanup_targets(root):
        _assert_safe_target(root, target)
        entries = tuple(_entries(target))
        file_count, byte_count = _measure(entries)
        reports.append(
            {
                "label": target.label,
                "path": str(target.path),
                "file_count": file_count,
                "byte_count": byte_count,
            }
        )
        pending.append((target, entries))

    if execute:
        for target, entries in pending:
            for entry in entries:
                if entry.is_dir():
                    shutil.rmtree(entry)
                else:
                    entry.unlink()
            target.path.mkdir(parents=True, exist_ok=True)

    return {
        "executed": execute,
        "file_count": sum(int(item["file_count"]) for item in reports),
        "byte_count": sum(int(item["byte_count"]) for item in reports),
        "targets": reports,
    }
