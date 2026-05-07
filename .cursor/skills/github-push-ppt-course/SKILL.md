---
name: github-push-ppt-course
description: >-
  Git commit and push for the text2classvideo repo without uploading local PPT
  storage (ppt_course_data). Use when the user asks to push to GitHub, 提交,
  commit, or wants the YYMMDD：更新信息 message format.
---

# 本仓库 Git 提交与推送（排除本地课件数据）

## 目标

- 只将**代码与文档**推到远程，**不**把本机落盘的解析结果与用户上传的 `.pptx` 副本纳入版本库。
- 默认数据目录 **`ppt_course_data/`** 必须在 **`.gitignore`** 中（本仓库已包含）；若用户改用了 `PPT_COURSE_DATA`，需把对应目录同样加入 ignore 或提醒勿 `git add` 该路径。

## 提交前检查

1. 阅读根目录 **`.gitignore`**，确认存在行：`ppt_course_data/`（及可选的 `ppt_course/user_data/`）。
2. 执行 `git status`。若出现 `ppt_course_data` 下文件被 **staged**，执行  
   `git reset HEAD -- ppt_course_data`（或 `git restore --staged`）取消暂存，**不要**用 `-f` 把该目录强加入库。
3. 若曾误提交过 `ppt_course_data`，需从跟踪中移除并保留本地文件：  
   `git rm -r --cached ppt_course_data`（仅当用户明确要求清理历史时再做，并单独说明风险）。

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

## 推荐命令序列（代理执行时）

```bash
git status
git add -A   # 确认 status 中不会出现 ppt_course_data 下的新文件被加入；若会，改用按路径 add 或先修正 ignore
git reset HEAD -- ppt_course_data 2>/dev/null || true
git commit -m "YYMMDD：更新说明"
git push origin <branch>
```

推送前应用户要求核对当前分支名（如 `main` / `master`）。

## 与本仓库相关的排除项小结

| 路径 / 模式        | 原因 |
|--------------------|------|
| `ppt_course_data/` | Web 解析任务持久化：含 `source.pptx`、`meta.json`、预览 PNG |
| `*.pptx`（根规则） | 避免误提交课件原件；测试夹具可用 `!tests/fixtures/**` 例外 |
| `.venv/`、`__pycache__/` | 环境与字节码 |

## 校验清单

- [ ] `ppt_course_data` 未出现在 `git diff --cached` 中  
- [ ] Commit message 符合 `YYMMDD：` 开头  
- [ ] Push 目标分支与远程一致
