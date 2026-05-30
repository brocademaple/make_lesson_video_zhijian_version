"""从环境变量加载配置（不硬编码密钥）。"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent
load_dotenv(_ROOT / ".env")


def project_root() -> Path:
    return _ROOT


def ai_api_key() -> Optional[str]:
    return os.getenv("AI_API_KEY") or os.getenv("OPENAI_API_KEY")


def ai_base_url() -> str:
    return os.getenv(
        "AI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
    ).rstrip("/")


def ai_model() -> str:
    return os.getenv("AI_MODEL", "qwen-plus")


def output_dir() -> Path:
    return _ROOT / "output"


def input_dir() -> Path:
    return _ROOT / "input"


def templates_dir() -> Path:
    return _ROOT / "templates"


def assets_dir() -> Path:
    return templates_dir() / "assets"
