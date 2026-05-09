---
name: transcript-rewrite-minimax
description: >-
  口播稿优化（transcript rewrite）、MiniMax T2A 白名单/停顿、文末 JSON 合成参数建议（speed/vol/pitch/emotion 等），
  与极简 system + user skill。在改口播、sanitize、或文档中提及插入语/追加规则/合成设参时使用。
---

# 口播稿优化（MiniMax T2A 对齐）

## 单一事实来源

| 内容 | 位置 |
|------|------|
| 允许插入语（sanitize） | `ppt_course_deal/minimax_t2a_allowlist.json` |
| **改写叙事与语气（模型可读长文）** | **`ppt_course_deal/transcript_rewrite/minimax_skill.md`**（完整放入 **user**） |
| **极简 system**（占位） | **`REWRITE_MINIMAL_SYSTEM`**（`prompt.py`） |
| 可选「追加规则」 | `external_apis.json` → **`transcript_rewrite.extra_instructions`** → 并入 **user** 内 **`【课程追加规则】`** |

## Python 包结构（`ppt_course_deal/transcript_rewrite/`）

| 模块 | 职责 |
|------|------|
| **`prompt.py`** | **`REWRITE_MINIMAL_SYSTEM`** + **`build_user_prompt_with_skill`** |
| **`llm.py`** | **`chat_rewrite`** |
| **`sanitize.py`** | **`sanitize_for_minimax_t2a`** |

## 运行时

- **不做**长 **`build_system_prompt`**：约束均在 **user**（skill + 可选追加 + 原文）。
- **`POST /api/transcript/rewrite`**：`system=REWRITE_MINIMAL_SYSTEM`，`user=build_user_prompt_with_skill(...)`。
- **全课语境（可选）**：前端可将当前任务 **各页各段** 逐字稿拼入 **`course_transcript_context`**，并传 **`context_slide_index` / `context_segment_index`**；skill 中 **【全课语气统筹】**与 **【质检与专业课内容红线】** 约束衔接与专业表述不可随意改写。

## 修改清单

增删合法标签：`minimax_t2a_allowlist.json`；改语气/叠用规则/输出格式与 JSON 参数字段说明：`minimax_skill.md`（`POST /api/transcript/rewrite` 会解析文末 `` ```json `` 块，返回 `minimax_hints` / `delivery_notes`）。

## 模型输出与 API

- 正文经 `sanitize_for_minimax_t2a` 后入 `rewritten_text`；JSON 块经 `split_rewrite_output` + `normalize_minimax_rewrite_hints` 后入 `minimax_hints`（可合并进浏览器 `minimax_overrides`）。
- 若用户勾选将改写稿存入 **口播版本库**（`localStorage`），会同时保存当次的 `minimax_hints` 与 `delivery_notes`；「口播版本库」弹窗中逐条展示 **AI 建议的合成参数** 供日后对照（生成时仍可改）。
