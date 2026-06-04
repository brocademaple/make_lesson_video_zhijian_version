---
name: ppt-course-remotion-director
description: >-
  text2classvideo：deal 产出 → Remotion 成片 的「导演层」方法论（数据契约、caption、时间轴、
  Claude Code 任务拆解）。在编写 input-props、扩展 CourseDeckComposition、或委托 Agent 做
  课件视频时使用。
metadata:
  tags: text2classvideo, remotion, ppt_course_deal, props, scene-plan
---

## 何时使用

- 要把 **PPT 解析结果 / 音频工作台** 接到 **`ppt_course_renderer`**，而不只做「PNG 轮播」。
- 委托 **Claude Code**（或其它 Agent）改 **`input-props.json`**、**Composition**、或设计 **scene-plan** 时，要求其遵守与本仓库一致的契约。

## 三层分工（不要混淆）

| 层 | 目录 / 产物 | 职责 |
|----|----------------|------|
| **抽取** | `ppt_course_deal` → `ppt_course_data/tasks/<id>/` | `meta.json`（标题、正文块）、`previews/`、`audio_workspace` / `tasks/.../audio/` |
| **导演（可选但推荐）** | 心智模型或将来 `scene-plan.json` | 从 meta / 逐字稿归纳 **caption**、段落边界、镜头意图（何时 full / shape） |
| **渲染** | `ppt_course_renderer` | **`staticFile` + `REMOTION_WORKSPACE_ROOT` + `Config.setPublicDir(仓库根)`**；**`<Img>` / `<Audio>`**；动效用 **`interpolate`**，禁止 CSS animation |

## `input-props.json` 契约（当前已实现）

- **`fps`**、**`slides[]`**：每页 **`imageRelative`**（相对仓库根）、**`durationInFrames`**（建议来自真实音频时长 **`ceil(秒×fps)`**）。
- **`shapeRelatives`**：可选；存在时整页时长在 **full + 各 shape** 间 **均分**（可用脚本改为按稿切分）。
- **`audioRelatives` + `audioSegmentDurationInFrames`**：多段口播；各段帧数之和须等于 **`durationInFrames`**。
- **`caption`**（可选）：`{ "title": string, "subtitle"?: string }`，通常来自 **`meta.json` 的 `slides[i].title` + 摘要**；用于底部信息条，避免成片只有画没有「锚点文案」。

生成 props：**`ppt-course remotion-input-props`**（可加 **`--bundle-audio`**）；caption 需手动或脚本从 meta 填入。

## Claude Code 任务拆解模板（粘贴用）

1. **读**：`ppt_course_data/tasks/<task_id>/meta.json` 前 N 页、`render_tasks/.../input-props.json`、**`CourseDeckComposition.tsx`**。
2. **钉时钟**：所有 **`durationInFrames`** 与磁盘 mp3 时长一致（tinytag / meta）。
3. **补叙事**：为每页填 **`caption`**（标题来自 meta.title，subtitle 用 text 首句或人工摘要）；禁止编造与课件无关事实。
4. **Remotion 规范**：素材用 **`staticFile`**；动效 **`interpolate` + `useCurrentFrame`**；参考 **`remotion-best-practices`** skill 与官方 **`skills/remotion/rules/*.md`**（字幕 / sequencing / timing）。
5. **验收**：`npm run dev` 预览；再 **`npx remotion render ... --props ...`**。

## 进阶（未编码亦可写进方案）

- **逐句字幕**：从 **`transcript_segments`** 导出 SRT 式结构，再接入 `@remotion/captions` 或自定义 `Sequence`。
- **非均分 shape 时长**：在 props 里扩展「每镜帧数」数组，取代 **`splitFrames` 均分**。
- **scene-plan**：在 deal 与 renderer 之间增加 JSON（场景类型枚举 + 引用素材 id）， renderer 按类型选不同子 Composition。

## 自检

- [ ] 未使用 **`http://localhost/...`** 裸路径绕过 **`staticFile`**（除非文档另有约定）。
- [ ] **`REMOTION_WORKSPACE_ROOT`** 与 **`remotion.config.ts`** 中 **`setPublicDir`** 一致指向仓库根。
- [ ] 未引入 **CSS transition / Tailwind animate** 做成片动效。
