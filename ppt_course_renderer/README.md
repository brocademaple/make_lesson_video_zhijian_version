# ppt_course_renderer（Remotion）

本目录位于 any2video 仓库根目录的 **`ppt_course_renderer/`**，与兼容包 **`ppt_course_deal/`** 并列，用于 **video_project / 素材 / 音频 / 字幕 → 成片**。与工作台侧的集成约定见 **[docs/ppt_course_renderer_architecture.md](../docs/ppt_course_renderer_architecture.md)**。

当前新增了面向 AIGC 创作者的 **Visual Project** 主线：`video_project.json` 通过 adapter 转成 `input-props.json`，`ProductExperienceVideo` / `KnowledgeExplainer` 使用 `VisualScene` 渲染截图、变焦、局部高亮、标注和字幕。旧 `CourseDeck` 仍保留，用于兼容 PPT/PDF 导入后的历史任务。

现在的导演计划支持 **Remotion + Hyperframes 双引擎**：`render_plan.v2` 仍由 Remotion 掌握最终 timeline、音频、字幕和 MP4 导出；`hyperframes_creative` / `hybrid` 镜头会在 `render_tasks/<task>/creative_assets/<scene>/` 下生成 `creative_brief.json` 与 `asset_manifest.json`。当 `clip.mp4` 已就绪时，Remotion 会把它作为创意镜头或动效层嵌入对应帧段；缺失时自动回退到稳定 Remotion 模板。

### 本地用通用视频项目试跑

```bash
cd ..
.venv/bin/any2video video-project-props \
  ppt_course_renderer/render_tasks/product-experience-demo/video_project.json \
  -o ppt_course_renderer/render_tasks/product-experience-demo/input-props.json

cd ppt_course_renderer
npx remotion render src/index.ts ProductExperienceVideo \
  render_tasks/product-experience-demo/out/video.mp4 \
  --props render_tasks/product-experience-demo/input-props.json
```

- **`video_project.json`**：描述素材、镜头、视效 DSL 和 variants。
- **`ProductExperienceVideo`**：产品体验 / 工具演示类模板，适合截图、录屏、局部 zoom、功能说明。
- **`KnowledgeExplainer`**：知识解释类模板，第一版复用 `VisualScene`，后续可演化出更偏图解的风格。
- **视效 DSL**：已支持 `camera.zoom_to`、`focus.highlight_rect`、`focus.magnify_detail`、字幕轨和 callouts。

### 本地用已解析素材任务试跑

- deal 默认把任务落在 **`ppt_course_data/tasks/<task_id>/`**（根 `.gitignore` 忽略，勿提交）；其中有 **`previews/`**（含 **`slide-NNNN/full.png`**）、`meta.json`。**语音 mp3** 在并列目录 **`ppt_course_data/audio_workspace/task/<task_id>/slide-NNNN/`**（与 **`previews/slide-NNNN`** 同序号），便于在 **`input-props.json`** 里按页拼路径。
- **页时长（帧数）**：在课件 Web 生成 TTS 后，**`ppt_course_data/audio_workspace/task/<task_id>/meta.json`** 含各段 **`segment_duration_sec`**；或 **`GET /api/audio/workspace`** 的 **`slide_duration_sec`**。写 **`input-props.json`** 时 **`durationInFrames`** 可取 **`Math.ceil(秒 * fps)`**（与文件顶部 **`fps`** 一致），使该页视频长度与口播对齐。
- **推荐**：在 **`render_tasks/<任务名>/`** 下放 **`input-props.json`**（素材路径为「相对仓库根」），成片输出到同目录 **`out/`**。示例见 **`render_tasks/my-video-test1/`**，对应 Composition **`CourseDeck`**；导出 **`npm run render:test1`**。
- **工作台生成**：在 `any2video serve` 打开的已存任务中，使用 **Remotion 成片 → 生成渲染任务**，会优先读取 `approved_director_manifest.json`，否则读取 `director_manifest.json`，写出 **`render_tasks/task-<task_id>/render_plan.json`** 与 **`input-props.json`** 并显示本地渲染命令，例如 `npx remotion render src/index.ts CourseDeck render_tasks/task-<task_id>/out/video.mp4 --props render_tasks/task-<task_id>/input-props.json`。没有导演脚本时会回退到 Deal 元数据直出的旧 props。
- **CLI 生成**：`any2video remotion-render-plan <task_id>` 生成 director-aware `render_plan/input-props`；`any2video hyperframes-tasks <task_id>` 生成/刷新需要 Hyperframes 生产的创意资产 brief；`any2video remotion-input-props <task_id> -o <path>` 保留为低层 fallback 命令。旧 `ppt-course` 命令继续兼容。
- **素材路径**：`CourseDeckComposition` 使用 **`staticFile('ppt_course_data/...')`**。**`remotion.config.ts`** 将 public dir 设为 **`ppt_course_renderer/public/`**，其中 tracked symlink **`public/ppt_course_data -> ../../ppt_course_data`** 暴露课件数据，避免打包时复制整个仓库。请在 **`.env`** 设置 **`REMOTION_WORKSPACE_ROOT=<仓库根绝对路径>`**（见 **`.env.example`**）；在 **`ppt_course_renderer/`** 下执行 **`npm run dev` / `remotion render`**，以便未设置 env 时 **`process.cwd()/..`** 仍指向仓库根。

---

<p align="center">
  <a href="https://github.com/remotion-dev/logo">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://github.com/remotion-dev/logo/raw/main/animated-logo-banner-dark.apng">
      <img alt="Animated Remotion Logo" src="https://github.com/remotion-dev/logo/raw/main/animated-logo-banner-light.gif">
    </picture>
  </a>
</p>

Welcome to your Remotion project!

## Commands

**Install Dependencies**

```console
npm i
```

**Start Preview**

```console
npm run dev
```

**Render video**

```console
npx remotion render
```

**Upgrade Remotion**

```console
npx remotion upgrade
```

## Docs

Get started with Remotion by reading the [fundamentals page](https://www.remotion.dev/docs/the-fundamentals).

## Help

We provide help on our [Discord server](https://discord.gg/6VzzNDwUwV).

## Issues

Found an issue with Remotion? [File an issue here](https://github.com/remotion-dev/remotion/issues/new).

## License

Note that for some entities a company license is needed. [Read the terms here](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md).
