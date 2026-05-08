---
name: github-push-ppt-course
description: >-
  Git commit and push for the text2classvideo repo: what to add vs never add
  (ppt_course_data, build artifacts, secrets), YYMMDD：message format, and
  per-subproject ignores. Use when the user asks to push, 提交, or commit.
---

# 本仓库 Git 提交与推送（按当前结构：该 add 什么、别 add 什么）

## 目标

- 只把**可复现的源码、文档、配置、测试**推到远程；**不**把本机课件数据、合成产物、依赖目录和密钥文件纳入版本库。
- 默认数据目录 **`ppt_course_data/`** 必须在根目录 **`.gitignore`** 中（已包含）；若使用环境变量 **`PPT_COURSE_DATA`** 指向自定义目录，该目录也应 **ignore**，或**永远不要** `git add` 该路径。

## 仓库结构（便于对照该改哪里）

| 区域 | 说明 |
|------|------|
| **`ppt_course_deal/`** | 主 Python 包（Web/CLI、`static/`、`transcript_rewrite/` 等）——**应提交源码** |
| **`docs/`** | 项目文档（含 **`已实现功能说明.md`**）——**应提交** |
| **`tests/`** | 单测；**`tests/fixtures/**/*.pptx`** 为允许的例外课件夹具 |
| **`ppt_course_renderer/`** | Remotion/Node 子工程——**提交源码与配置**；见下文 **勿提交** |
| **`ppt_course_rebuilder/`** | 独立重构管线——**提交源码**；**`output/` 大量生成物**见该目录 `.gitignore` |
| **`ppt_course_data/`** | 默认数据根（任务、预览 PNG、`config/external_apis.json` 等）——**整目录勿提交** |

---

## 建议加入版本库（可以放心 `git add` 的）

- **`ppt_course_deal/**/*.py`**、**`ppt_course_deal/static/**`**、包内 **`*.json`**（如 `minimax_t2a_allowlist.json`）、**`transcript_rewrite/minimax_skill.md`** 等已跟踪资源。
- **`docs/**`**、**`tests/**`**（含允许的 **`tests/fixtures/**/*.pptx`**）。
- 根目录 **`pyproject.toml`**、**`README`** 等元数据。
- **`ppt_course_renderer/`**：**`package.json`、`src/`、`public/`**、doc 等；**不要 add `node_modules/`、`dist/`、`out/`**（见该目录 `.gitignore`）。
- **`ppt_course_renderer/render_tasks/`**：各任务目录内 **`input-props.json`、脚本说明**等可提交；**不要 add 各任务下的 `out/`、以及该目录规则忽略的 `*.mp4` 等成片**。
- **`ppt_course_rebuilder/`**：**源码与 `requirements.txt`** 等；**不要 add** 其 `.gitignore` 中的 **`output/*.pptx`**、部分 **`output/*.json`**、**`output/exported_images/`** 等（详见 **`ppt_course_rebuilder/.gitignore`**）。
- **`.cursor/skills/**`**：若团队约定把 Cursor 技能入库（本 skill 即在此路径），则**修改后的 SKILL 应提交**。

---

## 不要 add（保持本地或应由 ignore 挡住）

| 路径 / 类型 | 原因 |
|-------------|------|
| **`ppt_course_data/`** | 解析任务持久化：课件副本、预览图、本机 API 配置等 |
| **`ppt_course_deal/user_data/`**、**`ppt_course/user_data/`** | 历史用户数据路径（根 `.gitignore`） |
| **`.venv/`**、**`venv/`** | Python 虚拟环境 |
| **`node_modules/`**（renderer） | Node 依赖 |
| **`__pycache__/`**、**`*.pyc`**、**`.pytest_cache/`** | 字节码与测试缓存 |
| **`dist/`**、**`build/`**、**`*.egg-info/`** | 构建产物 |
| **根目录 `*.pptx`** | 误提交课件原件；**例外**：**`tests/fixtures/**/*.pptx`** |
| **`.env`** | 密钥与环境 |
| **`ppt_course_renderer/out`**、**`ppt_course_renderer/render_tasks/**/out/`** | 成片输出目录 |
| **`ppt_course_renderer/render_tasks/`** 下的 **`*.mp4`**、**`*.mkv`**、**`*.mov`** | 渲染视频产物 |
| **`ppt_course_rebuilder/output/`** 中被忽略的生成物 | 见 **`ppt_course_rebuilder/.gitignore`** |

**说明**：若 **`git add -A`** 仍能把 **`ppt_course_data`** 或 **`node_modules`** 加进去，说明 **ignore 未生效或路径不在仓库内**，应先修正 **`.gitignore`**，再提交；**不要**用 **`-f`** 强行加入上述目录。

---

## 提交前检查（代理执行）

1. 阅读根目录 **`.gitignore`**，确认 **`ppt_course_data/`** 存在；若有自定义数据目录，确认已忽略。
2. **`git status`**。若 **`ppt_course_data`** 或 **`node_modules`** 出现在 **staged**，执行 **`git restore --staged <路径>`** 或 **`git reset HEAD -- <路径>`** 取消暂存。
3. **`git diff --cached`**（或 GUI）确认没有误加的密钥文件、成片、整份用户数据目录。
4. 仅在用户明确要求「清理历史上误提交的数据」时，再考虑 **`git rm -r --cached ppt_course_data`**（须单独说明风险）。

---

## Commit message 格式（必须遵守）

单行主题，**不要**在消息里写「年份月份日期」等提示性括注，格式为：

```text
YYMMDD：具体更新说明
```

- **`YYMMDD`**：6 位数字，**年（公历后两位）+ 月 + 日**，月与日不足两位时前补 0。  
  例：2026 年 5 月 6 日 → **`260506`**（不是 20260506）。
- **全角冒号 `：`** 与说明之间**无空格**（与示例一致即可；若团队工具更适合半角 `:`，以一惯性为准，本仓库示例用 **`：`**）。
- **`更新说明`**：简短中文，说明本次改动要点（动词开头亦可）。

**示例（括号为写法说明，勿写入 commit）：**

- `260506：修复已存任务持久化顺序，避免 create_session 失败导致未落盘`
- `260506：新增 docs/KNOWLEDGE.md，说明 LibreOffice 与 Poppler 预览链路`

错误示例：`2026-05-06：xxx`、`260506(日期)：xxx`、`feat: xxx`（若用户明确要求本格式则不用 conventional commits）。

---

## 推荐命令序列（代理执行时）

```bash
git status
# 优先：按路径添加已知安全目录，避免一把 add 进数据目录
git add ppt_course_deal docs tests pyproject.toml .cursor/skills  # 按需增删路径
# 若仍使用 git add -A：
git add -A
git reset HEAD -- ppt_course_data ppt_course_deal/user_data ppt_course/user_data 2>/dev/null || true
git diff --cached --stat
git commit -m "YYMMDD：更新说明"
git push origin <branch>
```

推送前与用户核对当前分支名（如 **`main`** / **`master`**）。

---

## 校验清单

- [ ] **`ppt_course_data`**、**`node_modules`**、**`.venv`** 未出现在 **`git diff --cached`**
- [ ] 无成片 **`out/`**、无根目录误加的 **`.pptx`**（fixtures 例外）
- [ ] Commit message 符合 **`YYMMDD：`** 开头  
- [ ] Push 目标分支与远程一致
