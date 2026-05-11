"""导演脚本人工审核：通过 / 驳回 / 导出已审版本。"""

from __future__ import annotations

import copy
from typing import Any

from ppt_course_rebuilder.manifest_reader import read_json, write_json


def _find_scene_index(scenes: list[dict[str, Any]], scene_id: str) -> int:
    for i, s in enumerate(scenes):
        if str(s.get("scene_id") or "") == scene_id:
            return i
    return -1


def approve_scene(manifest_path: str, scene_id: str) -> dict[str, Any]:
    data = read_json(manifest_path)
    scenes: list[dict[str, Any]] = list(data.get("scenes") or [])
    idx = _find_scene_index(scenes, scene_id)
    if idx < 0:
        raise ValueError(f"scene not found: {scene_id}")
    scenes[idx]["review_status"] = "approved"
    scenes[idx]["reject_reason"] = None
    data["scenes"] = scenes
    data["review"] = _aggregate_review(scenes)
    write_json(manifest_path, data)
    return {"ok": True, "scene": scenes[idx]}


def reject_scene(
    manifest_path: str, scene_id: str, reason: str = ""
) -> dict[str, Any]:
    data = read_json(manifest_path)
    scenes: list[dict[str, Any]] = list(data.get("scenes") or [])
    idx = _find_scene_index(scenes, scene_id)
    if idx < 0:
        raise ValueError(f"scene not found: {scene_id}")
    scenes[idx]["review_status"] = "rejected"
    scenes[idx]["reject_reason"] = (reason or "").strip() or None
    data["scenes"] = scenes
    data["review"] = _aggregate_review(scenes)
    write_json(manifest_path, data)
    return {"ok": True, "scene": scenes[idx]}


def _aggregate_review(scenes: list[dict[str, Any]]) -> dict[str, Any]:
    p = a = rj = 0
    for s in scenes:
        st = str(s.get("review_status") or "pending")
        if st == "approved":
            a += 1
        elif st == "rejected":
            rj += 1
        else:
            p += 1
    return {
        "pending_count": p,
        "approved_count": a,
        "rejected_count": rj,
        "notes": "",
    }


def export_approved_manifest(manifest_path: str, output_path: str) -> dict[str, Any]:
    """
    写出新文件：仅含 approved scenes；rejected 进入 rejected_items；不覆盖源 manifest。
    """
    data = read_json(manifest_path)
    scenes: list[dict[str, Any]] = list(data.get("scenes") or [])
    approved: list[dict[str, Any]] = []
    rejected_items: list[dict[str, Any]] = []
    for s in scenes:
        st = str(s.get("review_status") or "pending")
        if st == "approved":
            approved.append(copy.deepcopy(s))
        elif st == "rejected":
            rejected_items.append(
                {
                    "scene_id": s.get("scene_id"),
                    "reject_reason": s.get("reject_reason"),
                    "scene_type": s.get("scene_type"),
                    "snapshot": copy.deepcopy(s),
                }
            )

    export_body: dict[str, Any] = {
        "task_id": data.get("task_id"),
        "course": copy.deepcopy(data.get("course") or {}),
        "assets": copy.deepcopy(data.get("assets") or []),
        "scenes": approved,
        "rejected_items": rejected_items,
        "review": {
            "pending_count": 0,
            "approved_count": len(approved),
            "rejected_count": len(rejected_items),
            "notes": "导出快照：仅包含审核通过的镜头；其它状态未纳入 scenes。",
        },
        "generated_at": data.get("generated_at"),
        "export_source": manifest_path,
    }
    write_json(output_path, export_body)
    return {
        "ok": True,
        "output_path": output_path,
        "approved_scene_count": len(approved),
        "rejected_item_count": len(rejected_items),
    }
