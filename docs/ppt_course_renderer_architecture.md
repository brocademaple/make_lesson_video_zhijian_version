# 智课影擎 Remotion 渲染架构

与 **`ppt_course_deal/`** 平行的 **Remotion 成片引擎**：接收智课影擎工作台提供的逐页图片、口播音频、逐字稿和分镜元数据，组装为 [Remotion](https://github.com/remotion-dev/remotion) 可用的合成数据，再驱动模板生成 MP4。

## 关系（数据流）

```
ppt_course_deal（PPT 入仓 / 预览图 / 分镜脚本 / 声音轨）
        │
        ▼ render_tasks/<task>/render_plan.json + input-props.json
ppt_course_renderer（本目录：Node / Remotion 项目）
        │
        ▼ 成片文件（MP4）
```

## 依赖与初始化

- **Remotion 本体**：见官方仓库 [remotion-dev/remotion](https://github.com/remotion-dev/remotion)；入门可用 `npx create-video@latest`（参见 Remotion 文档 [remotion.dev/docs](https://www.remotion.dev/docs)）。
- **本目录**：已在 **`ppt_course_renderer/`** 内初始化 Remotion 工程（`package.json`、`src/Composition.tsx` 等）；启动见该目录 **`README.md`**。

## 当前入口状态

工作台已经能为具体任务生成渲染入参：

```bash
cd ppt_course_renderer
npx remotion render src/index.ts MyVideoTest1 \
  render_tasks/<task_id>/out/video.mp4 \
  --props render_tasks/<task_id>/input-props.json
```

目前还保留一个偏样例工程的入口：Remotion composition 的默认 props 会指向一个固定样例 JSON。举例说，工作台任务 **`2555ebfb-ca07-4982-bf41-03d80b37dbad`** 已生成自己的 **`render_tasks/task-2555.../input-props.json`**，CLI 带 `--props` 渲染时会使用这个任务的数据；但如果直接打开 Remotion Studio，Studio 可能仍展示默认样例任务。这个现象就是“Remotion 入口还不够产品化”。

后续应把 Studio 入口做成任务感知：

- 工作台点击“预览成片”时传入当前任务的 `input-props.json`。
- Renderer 启动时读取 `REMOTION_INPUT_PROPS` 或 `render_tasks/latest/input-props.json`。
- composition id 和任务标题从当前任务派生，避免 Studio 里只看到 `MyVideoTest1` 这类工程名。

## Cursor / Agent 编码规范

Remotion 官方维护的 Agent Skills 位于 [remotion-dev/skills](https://github.com/remotion-dev/skills)（路径 `skills/remotion/`），可在本仓库 Cursor 规则中引用以对齐生成代码风格。

## 与 `ppt_course_rebuilder/`

`ppt_course_rebuilder/` 是工作台生成素材地图和分镜脚本的 Python 库；renderer 只消费最终的 `render_plan/input-props`，不直接依赖 Rebuilder 内部实现。
