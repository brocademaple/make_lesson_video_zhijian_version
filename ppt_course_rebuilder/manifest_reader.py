"""读写 manifest JSON（仅文件 I/O，无业务依赖）。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Union


def read_json(path: Union[str, Path]) -> dict[str, Any]:
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8"))


def write_json(path: Union[str, Path], data: dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
