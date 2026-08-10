# any2video Remotion 渲染架构

与 **`ppt_course_deal/`** 平行的 **Remotion 成片引擎**：接收 any2video 提供的 `video_project.json`、素材、口播音频、字幕和分镜元数据，组装为 [Remotion](https://github.com/remotion-dev/remotion) 可用的合成数据，再驱动模板生成 MP4。

## 关系（数据流）

```
ppt_course_deal（素材入仓 / video_project / 声音轨 / 版本）
        │
        ▼ render_tasks/<task>/video_project.json + input-props.json
ppt_course_renderer（本目录：Node / Remotion 项目）
        │
        ▼ 成片文件（MP4）
```

## 依赖与初始化

- **Remotion 本体**：见官方仓库 [remotion-dev/remotion](https://github.com/remotion-dev/remotion)；入门可用 `npx create-video@latest`（参见 Remotion 文档 [remotion.dev/docs](https://www.remotion.dev/docs)）。
- **本目录**：已在 **`ppt_course_renderer/`** 内初始化 Remotion 工程（`package.json`、`src/Composition.tsx` 等）；启动见该目录 **`README.md`**。

## 当前入口状态

工作台已经有两条渲染入参路径：

1. 新主线：`video_project.json` → `ProductExperienceVideo` / `KnowledgeExplainer`
2. 兼容线：PPT/PDF 任务 → `CourseDeck`

新主线示例：

```bash
cd ppt_course_renderer
npx remotion render src/index.ts ProductExperienceVideo \
  render_tasks/product-experience-demo/out/video.mp4 \
  --props render_tasks/product-experience-demo/input-props.json
```

兼容线示例：

```bash
cd ppt_course_renderer
npx remotion render src/index.ts CourseDeck \
  render_tasks/<task_id>/out/video.mp4 \
  --props render_tasks/<task_id>/input-props.json
```

当前正式 Composition 为 **`CourseDeck`**。举例说，工作台任务 **`2555ebfb-ca07-4982-bf41-03d80b37dbad`** 已生成自己的 **`render_tasks/task-2555.../input-props.json`**，CLI 带 `--props` 渲染时会使用这个任务的数据。

后续可继续把 Studio 入口做成任务感知：

- 工作台点击“预览成片”时传入当前任务的 `input-props.json`。
- Renderer 启动时读取 `REMOTION_INPUT_PROPS` 或 `render_tasks/latest/input-props.json`。
- 任务标题从当前任务派生，方便 Studio 中辨认当前预览对象。

## Cursor / Agent 编码规范

Remotion 官方维护的 Agent Skills 位于 [remotion-dev/skills](https://github.com/remotion-dev/skills)（路径 `skills/remotion/`），可在本仓库 Cursor 规则中引用以对齐生成代码风格。

## 与 `ppt_course_rebuilder/`

`ppt_course_rebuilder/` 是工作台生成素材地图和分镜脚本的 Python 库；renderer 只消费最终的 `render_plan/input-props`，不直接依赖 Rebuilder 内部实现。
