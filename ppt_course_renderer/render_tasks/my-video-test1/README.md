# my-video-test1

试用兼容任务 **`2555ebfb-ca07-4982-bf41-03d80b37dbad`** 的前 **3** 页：每页含 **`full.png`** 与 **`previews/slide-NNNN/shapes/shape-*.png`**（与 `meta.json` 中 `shape_image_manifest` 一致）。该页总时长 **90 帧**会在「整页 + 各 shape」镜头间均分。当前任务下无 mp3；生成 TTS 后可为对应页增加 **`audioRelative`**。

这是保留的兼容输入示例。运行时项目数据清理后，需重新导入对应素材才能渲染。

## 预览（Studio）

在 **`ppt_course_renderer/`** 目录：

```bash
npm run dev
```

在左侧选中 **`MyVideoTest1`**。若预览黑屏或裂图，请在 **`ppt_course_renderer/.env`** 设置：

```bash
REMOTION_WORKSPACE_ROOT=/你的绝对路径/any2video
```

## 导出成片

```bash
npm run render:test1
```

等价命令：

```bash
npx remotion render src/index.ts MyVideoTest1 render_tasks/my-video-test1/out/video.mp4 --props render_tasks/my-video-test1/input-props.json
```
