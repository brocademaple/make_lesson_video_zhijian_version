# ppt_course_renderer

与 **`ppt_course_deal/`** 平行的 **Remotion 视频渲染**子项目：接收课件侧提供的 **逐页图片**、**MiniMax 等 TTS 音频**、**逐字稿文本**，组装为 [Remotion](https://github.com/remotion-dev/remotion) 可用的合成数据，再驱动模板生成成片。

## 关系（数据流）

```
ppt_course_deal（PPT 解析 / 预览图 / 语音与文案落盘）
        │
        ▼ 每页 PNG、每页 mp3、逐字稿、时间轴元数据（契约待定）
ppt_course_renderer（本目录：Node / Remotion 项目 + 可选 CLI）
        │
        ▼ 成片文件（mp4 等）
```

## 依赖与初始化

- **Remotion 本体**：见官方仓库 [remotion-dev/remotion](https://github.com/remotion-dev/remotion)；入门可用 `npx create-video@latest`（参见 Remotion 文档 [remotion.dev/docs](https://www.remotion.dev/docs)）。
- **本目录**：后续在此放置 Remotion 工程（`package.json`、`src/Composition.tsx` 等）；当前仅为占位，便于与 `ppt_course_deal` 同步演进。

## Cursor / Agent 编码规范

Remotion 官方维护的 Agent Skills 位于 [remotion-dev/skills](https://github.com/remotion-dev/skills)（路径 `skills/remotion/`），可在本仓库 Cursor 规则中引用以对齐生成代码风格。

## 与 `ppt_course_rebuilder/`

**AI 课程重构管线**（`ppt_course_rebuilder/`）与本案 **无强制串联**；在整条「deal → renderer」管线调通前，Rebuilder 侧可暂不扩展。
