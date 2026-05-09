"""将 audio_workspace 内已落盘的 mp3 镜像到任务目录，便于归档与 Remotion 引用（不依赖 MiniMax URL）。"""

from __future__ import annotations

import shutil
from pathlib import Path

from ppt_course_deal.audio_workspace_store import resolve_workspace_audio_path, slide_count_for_task
from ppt_course_deal.task_storage import get_data_root


def task_bundle_audio_dir(task_id: str, slide_index: int) -> Path:
    root = get_data_root() / "tasks" / task_id / "audio" / f"slide-{slide_index:04d}"
    return root


def mirror_workspace_mp3_to_task_bundle(
    task_id: str,
    *,
    max_slides: int | None = None,
) -> tuple[int, list[Path]]:
    """把当前 meta 指向的各段 mp3 复制到 ``tasks/<task_id>/audio/slide-NNNN/``。

    源文件来自 ``audio_workspace``（服务端已从 MiniMax URL/hex 解码并写入磁盘）。
    返回 (复制的文件数, 目标路径列表)。
    """
    sc = slide_count_for_task(task_id)
    if sc is None or sc < 1:
        raise ValueError(f"无法解析任务页数：{task_id}")
    n = min(sc, max_slides) if max_slides is not None else sc

    copied: list[Path] = []
    count = 0
    for i in range(n):
        j = 0
        while True:
            ap = resolve_workspace_audio_path("task", task_id, i, j, "mp3")
            if ap is None or not ap.is_file():
                break
            dest_dir = task_bundle_audio_dir(task_id, i)
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / ap.name
            shutil.copy2(ap, dest)
            copied.append(dest)
            count += 1
            j += 1
            if j > 500:
                break
    return count, copied
