---
name: transcript-rewrite-minimax
description: >-
  口播稿优化（transcript rewrite）与 MiniMax T2A 白名单、停顿、极简 system + user skill。
  在改口播改写、sanitize、或文档中提及插入语/追加规则时使用。
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

## 修改清单

增删合法标签：`minimax_t2a_allowlist.json`；改语气/叠用规则：`minimax_skill.md`。
