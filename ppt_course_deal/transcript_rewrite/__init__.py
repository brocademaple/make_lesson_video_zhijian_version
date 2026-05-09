"""口播稿优化（MiniMax T2A）：服务端「开始改写」整条链路。

按执行顺序：

- **prompt** — 极简 **system** + **user**（内置 ``minimax_skill.md``；可选课程追加）
- **llm** — OpenAI 兼容 ``/v1/chat/completions`` HTTP 调用
- **sanitize** — 模型输出按 ``minimax_t2a_allowlist.json`` 清理

与本目录并列、名称相近但职责不同：**``transcript_import``**（逐字稿导入预览），不参与 LLM 改写。
"""

from ppt_course_deal.transcript_rewrite.llm import (
    chat_rewrite,
    normalize_minimax_rewrite_hints,
    normalize_rewrite_api_key,
    parse_chat_completions_response_body,
    resolve_chat_completions_url,
    split_rewrite_output,
)
from ppt_course_deal.transcript_rewrite.prompt import (
    REWRITE_MINIMAL_SYSTEM,
    build_user_prompt,
    build_user_prompt_with_skill,
    load_transcript_rewrite_minimax_skill_text,
)
from ppt_course_deal.transcript_rewrite.sanitize import sanitize_for_minimax_t2a

__all__ = [
    "REWRITE_MINIMAL_SYSTEM",
    "build_user_prompt",
    "build_user_prompt_with_skill",
    "chat_rewrite",
    "load_transcript_rewrite_minimax_skill_text",
    "normalize_minimax_rewrite_hints",
    "normalize_rewrite_api_key",
    "parse_chat_completions_response_body",
    "resolve_chat_completions_url",
    "sanitize_for_minimax_t2a",
    "split_rewrite_output",
]
