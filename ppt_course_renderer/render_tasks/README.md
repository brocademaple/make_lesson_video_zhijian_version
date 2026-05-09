# 渲染任务目录（成片输出与任务级配置）

本目录用于按「任务」组织 **Remotion 输入参数**（`input-props.json`）与 **生成视频产物**（各子目录下的 `out/`），避免与 `src/` 源码混放。

- **约定**：每个子目录（如 `my-video-test1/`）代表一次可复现的试跑或正式导出配置。
- **素材路径**：`input-props.json` 内的图片/音频使用 **相对仓库根目录** 的路径（与 `ppt_course_data/` 下 deal 落盘结构对齐）；**不是**相对本 JSON 文件所在目录。
- **自动生成**：在仓库根激活 venv 后执行  
  `ppt-course remotion-input-props <task_id> -o ppt_course_renderer/render_tasks/<名称>/input-props.json`  
  可从 **`audio_workspace`** 读取分段时长并写入 **`audioRelatives`** / **`durationInFrames`**（详见 **`docs/已实现功能说明.md`**）。  
  MiniMax 返回的音频外链有效期短；服务端合成时已下载字节写入 **`audio_workspace`**。若希望 **`input-props` 只引用任务目录内副本**（便于打包），请加 **`--bundle-audio`**（会把 mp3 复制到 **`ppt_course_data/tasks/<task_id>/audio/`**）。亦可用 **`ppt-course bundle-task-audio <task_id>`** 仅复制不生成 JSON。
- **环境**：在 `ppt_course_renderer/` 下可复制 `.env.example` 为 `.env`，设置 `REMOTION_WORKSPACE_ROOT` 为 **本仓库根目录的绝对路径**，以便 Remotion Studio 正确解析素材（CLI 默认从 `ppt_course_renderer` 启动时已等价于「上一级为仓库根」）。
