"""课程导演层：从 raw_material_manifest 生成 director_manifest（启发式初版）。"""

from __future__ import annotations

from ppt_course_rebuilder.director import rebuild_course_from_raw_manifest

__all__ = ["rebuild_course_from_raw_manifest"]
