# ppt_course_renderer（Remotion）

本目录位于仓库根目录 **`text2classvideo/ppt_course_renderer/`**，与 **`ppt_course_deal/`** 并列，用于 **deal 输出的图片 / 音频 / 逐字稿 → 成片**。与课件侧的集成约定见 **[docs/ppt_course_renderer_architecture.md](../docs/ppt_course_renderer_architecture.md)**。

当前模板已经从“PPT 轮播”升级为 **scene-aware 企业培训视频模板**：Render Adapter 会把 DirectorManifest 中的 `layout`、`subtitle.segments`、`render_overlays.callouts`、`source_evidence`、`risk_items` 转成 `input-props.json`，`CourseDeckComposition` 根据 `full_slide`、`rule_card`、`split_panel`、`case_dialogue`、`summary` 五类 layout 渲染标题条、字幕轨、风险核对条、证据框和进度条。原 PPT 仍是主视觉证据，动画只使用 Remotion frame/interpolate。

现在的导演计划支持 **Remotion + Hyperframes 双引擎**：`render_plan.v2` 仍由 Remotion 掌握最终 timeline、音频、字幕和 MP4 导出；`hyperframes_creative` / `hybrid` 镜头会在 `render_tasks/<task>/creative_assets/<scene>/` 下生成 `creative_brief.json` 与 `asset_manifest.json`。当 `clip.mp4` 已就绪时，Remotion 会把它作为创意镜头或动效层嵌入对应帧段；缺失时自动回退到稳定 Remotion 模板。

### 本地用已解析课程试跑

- deal 默认把任务落在 **`ppt_course_data/tasks/<task_id>/`**（根 `.gitignore` 忽略，勿提交）；其中有 **`previews/`**（含 **`slide-NNNN/full.png`**）、`meta.json`。**语音 mp3** 在并列目录 **`ppt_course_data/audio_workspace/task/<task_id>/slide-NNNN/`**（与 **`previews/slide-NNNN`** 同序号），便于在 **`input-props.json`** 里按页拼路径。
- **页时长（帧数）**：在课件 Web 生成 TTS 后，**`ppt_course_data/audio_workspace/task/<task_id>/meta.json`** 含各段 **`segment_duration_sec`**；或 **`GET /api/audio/workspace`** 的 **`slide_duration_sec`**。写 **`input-props.json`** 时 **`durationInFrames`** 可取 **`Math.ceil(秒 * fps)`**（与文件顶部 **`fps`** 一致），使该页视频长度与口播对齐。
- **推荐**：在 **`render_tasks/<任务名>/`** 下放 **`input-props.json`**（素材路径为「相对仓库根」），成片输出到同目录 **`out/`**。示例见 **`render_tasks/my-video-test1/`**，对应 Composition **`MyVideoTest1`**；导出 **`npm run render:test1`**。
- **工作台生成**：在 `ppt-course serve` 打开的已存任务中，使用 **Remotion 成片 → 生成渲染任务**，会优先读取 `approved_director_manifest.json`，否则读取 `director_manifest.json`，写出 **`render_tasks/task-<task_id>/render_plan.json`** 与 **`input-props.json`** 并显示本地渲染命令，例如 `npx remotion render src/index.ts MyVideoTest1 render_tasks/task-<task_id>/out/video.mp4 --props render_tasks/task-<task_id>/input-props.json`。没有导演脚本时会回退到 Deal 元数据直出的旧 props。
- **CLI 生成**：`ppt-course remotion-render-plan <task_id>` 生成 director-aware `render_plan/input-props`；`ppt-course hyperframes-tasks <task_id>` 生成/刷新需要 Hyperframes 生产的创意资产 brief；`ppt-course remotion-input-props <task_id> -o <path>` 保留为低层 fallback 命令。
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
