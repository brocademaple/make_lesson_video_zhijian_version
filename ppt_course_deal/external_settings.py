"""外部 API 配置（落盘于数据目录，密钥不落日志）。"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from ppt_course_deal.minimax_client import normalize_minimax_api_key
from ppt_course_deal.task_storage import get_data_root

logger = logging.getLogger(__name__)

CONFIG_DIRNAME = "config"
CONFIG_FILENAME = "external_apis.json"

DEFAULT_MINIMAX: dict[str, Any] = {
    "api_base": "https://api.minimaxi.com",
    "group_id": "",
    "model": "speech-2.8-turbo",
    "voice_id": "Chinese (Mandarin)_Lyrical_Voice",
    "language_boost": "Chinese",
    "output_format": "url",
    "audio_format": "mp3",
    "sample_rate": 32000,
    "bitrate": 128000,
    "speed": 1.0,
    "vol": 1.0,
    "pitch": 0,
    "stream": False,
}

DEFAULT_AGENT: dict[str, Any] = {
    "provider": "none",
    "note": "",
}

# 界面「追加规则」**默认**为空。MiniMax 口播结构、19 项插入语与篇幅等**固定指引**已迁至包内
# **transcript_rewrite/minimax_skill.md**，在请求大模型时作为 **user 消息** 前置段下发，不再进入 system。
DEFAULT_TRANSCRIPT_REWRITE_EXTRA_INSTRUCTIONS = ""

# 曾作为「默认追加规则」写入磁盘的**完整长模板**（与 V2 版 Python 默认一致），用于在 load_raw 时识别并**清空**，
# 避免与内置 skill 文件重复。
LEGACY_TRANSCRIPT_REWRITE_FULL_DISK_DEFAULT_V2 = """【场景与语气】
面向在线课程录播：普通话、条理清晰、像在教室里对学生讲解。除下方「白名单插入语」外，可用自然中文衔接（如「那么」「接下来」「我们看一下」），不要堆砌口头禅；禁止编造其它英文括号标签或自造 (中文) 效果。

【MiniMax T2A 支持的插入语（仅允许下列英文标签，须小写、带括号，与官方 speech-2.8 等模型说明一致）】
以下每一个都是合法 token，可按语境**少量**选用，用于气息、停顿感或情绪辅助；**不要**叠用多个，也不要每句都加。

- (laughs)（笑声）
- (chuckle)（轻笑）
- (coughs)（咳嗽）
- (clear-throat)（清嗓子）
- (groans)（呻吟）
- (breath)（正常换气）
- (pant)（喘气）
- (inhale)（吸气）
- (exhale)（呼气）
- (gasps)（倒吸气）
- (sniffs)（吸鼻子）
- (sighs)（叹气）
- (snorts)（喷鼻息）
- (burps)（打嗝）
- (lip-smacking)（咂嘴）
- (humming)（哼唱）
- (hissing)（嘶嘶声）
- (emm)（嗯 / 迟疑）
- (sneezes)（喷嚏）

【停顿标记】
使用 <#x#> 表示停顿 x 秒，x 在 [0.01, 99.99]，最多两位小数；夹在可朗读文本之间，勿连续多个 <#…#>。

【与合成参数 emotion 区分】
voice_setting.emotion（happy/calm 等）由用户在 MiniMax 合成界面单独配置；**不要把上述英文情绪单词当作口播正文插入**。插入情感优先用标点、换行与本节白名单标签。

【内容与节奏】
保留知识点、术语与数字，不编造事实。长句拆分，逗号/句号/问号换气；段落换行。书面语可口语化，但不改变专业含义。

【篇幅】
改写长度一般不超过原文约 1.15 倍；禁止为凑字数堆砌插入语或冗余复述。"""

# 早期默认追加规则（曾写入 external_apis.json）；加载时清空或由用户自定义保留。
LEGACY_TRANSCRIPT_REWRITE_EXTRA_INSTRUCTIONS_V1 = """【场景与语气】
面向在线课程录播：普通话、条理清晰、像在教室里对学生讲解。可适当使用简短口语衔接（例如「那么」「接下来」「我们看一下」），但不要堆砌口头禅；不要用括号自创中文语气符号。

【与 MiniMax T2A 对齐】
改写后的文稿将直接送入 MiniMax 语音合成。除服务端已声明的白名单英文插入语（如 (sighs)、(breath) 等）与停顿标记 <#秒数#> 外，不要再发明其它括号标记或魔法字符串。情绪请靠内容与标点体现；voice_setting.emotion 由用户在合成参数里单独配置，请不要在正文里写 happy/calm 这类英文情绪词。

【内容与节奏】
保留原有知识点、术语与数字，不编造事实。可适当拆分长句、加入逗号/句号/问号控制换气；段落之间用换行分段。若原文过于书面化，可改为更易朗读的说法，但不要改变专业含义。

【篇幅】
在忠于教学的前提下，改写长度一般不超过原文的约 1.15 倍；不要为凑字数加冗余复述。"""


def _normalize_extra_newlines(s: str) -> str:
    return (s or "").replace("\r\n", "\n").strip()


def should_clear_legacy_builtin_long_extra(extra: str | None) -> bool:
    """是否与曾内置的长默认追加规则完全一致（含 19 项释义版）；应由内置 skill 接管，清空磁盘重复。"""
    t = _normalize_extra_newlines(extra or "")
    if not t:
        return False
    return t == _normalize_extra_newlines(LEGACY_TRANSCRIPT_REWRITE_FULL_DISK_DEFAULT_V2)


def should_migrate_legacy_extra_instructions(extra: str | None) -> bool:
    """是否与更早期的短模板一致；迁移为清空（方法论已由 transcript_rewrite/minimax_skill.md 注入 user）。"""
    t = _normalize_extra_newlines(extra or "")
    if not t:
        return False
    if should_clear_legacy_builtin_long_extra(extra):
        return False
    if t == _normalize_extra_newlines(LEGACY_TRANSCRIPT_REWRITE_EXTRA_INSTRUCTIONS_V1):
        return True
    # 曾保存的「如 (sighs)、(breath) 等」短模板，未包含完整列表
    if "【与 MiniMax T2A 对齐】" in t and "如 (sighs)、(breath) 等" in t:
        return True
    return False


DEFAULT_TRANSCRIPT_REWRITE: dict[str, Any] = {
    "provider": "none",
    "api_base": "https://api.openai.com/v1",
    "api_key": "",
    "model": "qwen3.5-flash",
    "extra_instructions": DEFAULT_TRANSCRIPT_REWRITE_EXTRA_INSTRUCTIONS,
}


def config_path() -> Path:
    d = get_data_root() / CONFIG_DIRNAME
    d.mkdir(parents=True, exist_ok=True)
    return d / CONFIG_FILENAME


def load_raw() -> dict[str, Any]:
    path = config_path()
    if not path.is_file():
        return {
            "minimax": {**DEFAULT_MINIMAX},
            "agent": {**DEFAULT_AGENT},
            "transcript_rewrite": {**DEFAULT_TRANSCRIPT_REWRITE},
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        logger.warning("外部配置损坏，已使用默认")
        return {
            "minimax": {**DEFAULT_MINIMAX},
            "agent": {**DEFAULT_AGENT},
            "transcript_rewrite": {**DEFAULT_TRANSCRIPT_REWRITE},
        }
    mm = {**DEFAULT_MINIMAX, **(data.get("minimax") or {})}
    ag = {**DEFAULT_AGENT, **(data.get("agent") or {})}
    tr = {**DEFAULT_TRANSCRIPT_REWRITE, **(data.get("transcript_rewrite") or {})}
    extra = tr.get("extra_instructions")
    if isinstance(extra, str):
        if should_clear_legacy_builtin_long_extra(
            extra
        ) or should_migrate_legacy_extra_instructions(extra):
            tr["extra_instructions"] = DEFAULT_TRANSCRIPT_REWRITE_EXTRA_INSTRUCTIONS
            to_save = {**data, "minimax": mm, "agent": ag, "transcript_rewrite": tr}
            try:
                save_raw(to_save)
            except OSError:
                logger.warning("迁移口播追加规则写盘失败", exc_info=True)
    return {"minimax": mm, "agent": ag, "transcript_rewrite": tr}


def save_raw(data: dict[str, Any]) -> None:
    path = config_path()
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def mask_key(key: str | None) -> dict[str, Any]:
    if not key or not str(key).strip():
        return {"configured": False, "suffix": None}
    s = str(key).strip()
    suf = s[-4:] if len(s) >= 4 else "****"
    return {"configured": True, "suffix": suf}


def public_transcript_rewrite(tr: dict[str, Any]) -> dict[str, Any]:
    """供 GET 返回；本机工作台回显密钥以便编辑。"""
    key = tr.get("api_key") or ""
    out = {k: v for k, v in tr.items() if k != "api_key"}
    out.update(mask_key(str(key) if key else None))
    out["api_key"] = str(key).strip() if str(key).strip() else ""
    return out


def merge_transcript_rewrite_update(
    existing: dict[str, Any], body: dict[str, Any]
) -> dict[str, Any]:
    merged = {**existing}
    for k, v in body.items():
        if k == "api_key":
            if isinstance(v, str):
                merged["api_key"] = normalize_minimax_api_key(v) if v.strip() else ""
            continue
        if v is not None:
            merged[k] = v
    return merged


def get_transcript_rewrite_for_server_call() -> dict[str, Any]:
    raw = load_raw()
    return raw.get("transcript_rewrite") or {**DEFAULT_TRANSCRIPT_REWRITE}


def public_minimax(mm: dict[str, Any]) -> dict[str, Any]:
    """供 GET 返回。本机工作台需回显密钥以便编辑；勿将服务暴露公网。"""
    key = mm.get("api_key") or ""
    out = {k: v for k, v in mm.items() if k != "api_key"}
    out.update(mask_key(str(key) if key else None))
    out["api_key"] = str(key).strip() if str(key).strip() else ""
    return out


def merge_minimax_update(existing: dict[str, Any], body: dict[str, Any]) -> dict[str, Any]:
    merged = {**existing}
    for k, v in body.items():
        if k == "api_key":
            if isinstance(v, str):
                merged["api_key"] = (
                    normalize_minimax_api_key(v) if v.strip() else ""
                )
            continue
        if v is not None:
            merged[k] = v
    return merged


def merge_agent_update(existing: dict[str, Any], body: dict[str, Any]) -> dict[str, Any]:
    merged = {**existing}
    for k, v in body.items():
        if v is not None:
            merged[k] = v
    return merged


def get_minimax_for_server_call() -> dict[str, Any]:
    """含明文 api_key，仅服务端合成调用。"""
    raw = load_raw()
    return raw.get("minimax") or {**DEFAULT_MINIMAX}
