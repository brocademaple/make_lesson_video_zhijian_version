---
name: product-inline-help
description: >-
  Moves system-usage and instructional copy into an icon-triggered modal so the
  main product surface stays free of long explanatory paragraphs. Use when
  building or editing web UI, help/onboarding copy, or when the user mentions
  说明文案、帮助图标、弹窗、或「说明不要占主视图」.
---

# 产品内联说明 → 图标 + 弹窗

## 硬性规则（与产品约定一致）

凡是关于**系统使用**的说明性文字，须满足：

1. **不得**以长段落形式占据产品主视图（首屏工作区、列表旁、预览主区等）。
2. 使用**单一视觉入口**：在对应模块旁放置**图标按钮**（推荐信息圆标 ⓘ / `aria-label` 说明用途）。
3. 点击后在**弹窗**（优先原生 `<dialog>` + `showModal()`）中展示完整说明；关闭后主视图恢复无干扰布局。
4. **无障碍**：图标按钮须有 `aria-label`；弹窗须有 `aria-labelledby` 指向标题；焦点交给弹窗（浏览器对 `dialog` 的默认行为）。

## 实施要点

- **文案分层**：主视图仅保留操作标题、状态、数据；解释「怎么用 / 是什么」的全部放入弹窗。
- **动态说明**（如随页面状态变化的提示）：仍不写回主视图长文案；在逻辑里保存当前说明字符串，用户点击图标时再写入弹窗正文。
- **例外**：实时错误/告警（解析失败、上传超限）可用 `role="alert"` 条带简短展示；与「使用教程类」说明区分。
- **样式**：图标尺寸与行高对齐模块标题；弹窗宽度 `min(92vw, 28rem)` 左右，`::backdrop` 半透明遮罩。

## 前端骨架（复用）

单例弹窗：`#help-dialog`、`#help-dialog-title`、`#help-dialog-body`；`openHelp(title, bodyText)` 内 `bodyText` 可按 `\n\n` 拆成多段 `<p>`。

关闭：`form method="dialog"` 内提交按钮，或点击 `dialog` 背景（若 `event.target === dialog`）调用 `close()`。

## 校验清单

- [ ] 主视图无大块灰色说明段
- [ ] 每块说明有对应图标入口
- [ ] 键盘可达（Tab 到图标，Enter 打开，Esc 关闭）
