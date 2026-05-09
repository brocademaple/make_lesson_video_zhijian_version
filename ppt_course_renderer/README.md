# ppt_course_renderer（Remotion）

本目录位于仓库根目录 **`text2classvideo/ppt_course_renderer/`**，与 **`ppt_course_deal/`** 并列，用于 **deal 输出的图片 / 音频 / 逐字稿 → 成片**。与课件侧的集成约定见 **[docs/ppt_course_renderer_architecture.md](../docs/ppt_course_renderer_architecture.md)**。

### 本地用已解析课程试跑

- deal 默认把任务落在 **`ppt_course_data/tasks/<task_id>/`**（根 `.gitignore` 忽略，勿提交）；其中有 **`previews/`**（含 **`slide-NNNN/full.png`**）、`meta.json`。**语音 mp3** 在并列目录 **`ppt_course_data/audio_workspace/task/<task_id>/slide-NNNN/`**（与 **`previews/slide-NNNN`** 同序号），便于在 **`input-props.json`** 里按页拼路径。
- **页时长（帧数）**：在课件 Web 生成 TTS 后，**`ppt_course_data/audio_workspace/task/<task_id>/meta.json`** 含各段 **`segment_duration_sec`**；或 **`GET /api/audio/workspace`** 的 **`slide_duration_sec`**。写 **`input-props.json`** 时 **`durationInFrames`** 可取 **`Math.ceil(秒 * fps)`**（与文件顶部 **`fps`** 一致），使该页视频长度与口播对齐。
- **推荐**：在 **`render_tasks/<任务名>/`** 下放 **`input-props.json`**（素材路径为「相对仓库根」），成片输出到同目录 **`out/`**。示例见 **`render_tasks/my-video-test1/`**，对应 Composition **`MyVideoTest1`**；导出 **`npm run render:test1`**。
- **素材路径**：`CourseDeckComposition` 使用 **`staticFile('ppt_course_data/...')`**（Remotion 要求 `public/` 内资源须如此引用）。**`remotion.config.ts`** 已 **`Config.setPublicDir(仓库根)`**，使 **`ppt_course_data/`** 指向仓库根下真实目录，无需再把整个数据拷进 **`ppt_course_renderer/public/`**（可选保留 **`public/ppt_course_data`** 符号链接作兼容）。请在 **`.env`** 设置 **`REMOTION_WORKSPACE_ROOT=<仓库根绝对路径>`**（见 **`.env.example`**）；在 **`ppt_course_renderer/`** 下执行 **`npm run dev` / `remotion render`**，以便未设置 env 时 **`process.cwd()/..`** 仍指向仓库根。

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
