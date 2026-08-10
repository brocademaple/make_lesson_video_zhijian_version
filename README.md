# any2video

面向个人 / AIGC 创作者的本地视频生成工作台：把文字、图片、音频和课件素材组织成可执行镜头计划，由 **Remotion + HyperFrames** 本地双引擎生成视频成片。

详细已实现能力与版本说明见：**[docs/已实现功能说明.md](docs/已实现功能说明.md)**。

## V0.4：本地智能执行内核

V0.4 为每个镜头增加可解释的引擎决策：`auto` 会根据镜头位置、内容风险和表达目的，在 Remotion 稳定模板、HyperFrames 创意动效与双引擎叠加之间路由；导演也可逐镜覆盖。HyperFrames 未安装或执行失败时，创意源码仍会保存在本机，最终成片自动使用 Remotion 安全回退。

每次“准备创意镜头”或“生成成片”都会写入 `video_workspace/projects/<project_id>/runs/run-*.json`，记录路由、创意镜头、渲染计划、最终渲染和文件验证状态。导演台会显示本机执行能力、路由原因、镜头状态和最近一次运行进度。

```bash
any2video capabilities
any2video prepare-scenes <project_id>               # 只生成 HTML、DESIGN.md 与 brief
any2video prepare-scenes <project_id> --execute     # 使用已安装的 HyperFrames
any2video project-runs <project_id>
```

详细协议与目录见 [V0.4 本地执行内核](docs/v0.4-local-execution-kernel.md)。

## V0.3：可编辑导演台

V0.3 把“生成镜头初稿”与“生成成片”拆成两个明确阶段。素材入仓后，可在浏览器内逐镜修改镜头名称、时长、画面素材、屏幕文字、旁白和镜头目的；支持新增、复制、删除、拖动排序，以及键盘可访问的前移 / 后移。保存后的导演稿会直接作为下一次 Remotion 渲染输入，不会在生成成片时被自动重建。

核心验收路径：

1. 创建项目并输入文字、图片、旁白。
2. 点“生成镜头”进入导演台。
3. 编辑、增删、复制或重排镜头并保存。
4. 点“生成成片”，在右侧预览或打开生成的 MP4。

项目数据默认保存在 `video_workspace/projects/<project_id>/`；可通过 `ANY2VIDEO_WORKSPACE_ROOT` 覆盖。

---

## 模块怎么区分（命名与目录）

| 中文定位 | 代码位置 | 典型用法 |
|----------|----------|----------|
| **any2video 工作台** | Python 包 **`ppt_course_deal`**（分发名 **`any2video`**，命令 **`any2video`**；旧命令 **`ppt-course`** 继续兼容） | **唯一 Web 入口**：本机 **FastAPI + 静态前端**（素材导入、项目库、声音轨、外部 API、镜头计划、成片蓝图等）+ CLI **`any2video serve` / `video-project-props`**。历史 PPT/PDF 能力保留为素材导入器。 |
| **成片引擎（Remotion）** | 目录 **`ppt_course_renderer/`** | 与 `ppt_course_deal` 平行：接收 `video_project.json` / `input-props.json`、图片/截图/音频/字幕，生成 Remotion 合成数据并导出成片；见该目录 **README**。 |
| **导演模块（Rebuilder 库）** | 目录 **`ppt_course_rebuilder/`**（包名 **`ppt_course_rebuilder`**） | 作为旧素材项目兼容层被 **`ppt_course_deal` import**：从 PPT/PDF 任务生成素材地图和导演脚本，再通过 adapter 转成 Remotion **`render_plan/input-props`**。 |
| **GitHub Pages 静态介绍页** | 目录 **`github-pages/`** | **与运行时代码隔离**：仅 HTML/CSS/截图占位；本地预览见该目录 **README**；发布需在仓库 **Settings → Pages** 选择根目录、`/docs` 或 **GitHub Actions** 将本目录产物上线。 |

日常以 **any2video 工作台** 为唯一产品入口；**renderer** 负责成片；`video_project.json` 是新的通用视频项目模型。旧 PPT/PDF 流程作为素材导入与兼容层保留。

---

## 快速开始

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
any2video serve    # Web：默认 http://127.0.0.1:8765/（默认开启 **--reload**，改代码后自动重载；常驻可加 **--no-reload**）
# 或
any2video video-project-props ppt_course_renderer/render_tasks/product-experience-demo/video_project.json \
  -o ppt_course_renderer/render_tasks/product-experience-demo/input-props.json
```

### 通用视频项目

新的创作主线使用 **`video_project.json`**：

- **materials**：截图、录屏、图片、文本、音频、链接摘要等素材。
- **scenes**：每个镜头的旁白、屏幕文字、素材引用、视效组件、时长。
- **variants**：同一批素材的不同版本，例如快速演示版、教程版、创作者种草版。
- **effects**：视效 DSL，例如 `camera.zoom_to`、`focus.highlight_rect`、`overlay.label`、`caption.subtitle_track`。

示例项目位于 **`ppt_course_renderer/render_tasks/product-experience-demo/video_project.json`**，可生成 **`ProductExperienceVideo`** 或 **`KnowledgeExplainer`** 的 Remotion 入参。

### 整页预览图（LibreOffice + Poppler）

工作台左侧缩略图 / 右侧大图若要显示 **真实幻灯片像素图**（而非文本占位图），本机需安装：

- **LibreOffice**（提供 `soffice`，用于 PPTX→PDF）
- **Poppler**（提供 `pdftoppm`，用于 PDF→PNG）

**macOS（Homebrew）示例：**

```bash
brew install --cask libreoffice
brew install poppler
```

安装后 **重启** `any2video serve`。打开页面时若依赖未就绪，上传区会显示简要提示；也可访问 **`GET /api/health`** 查看 `preview_render.ready` 与路径探测结果。

### 本地上传与「已存任务」

在 Web 里**上传并成功解析**一份 `.pptx` 后，会在仓库根目录 **`ppt_course_data/tasks/<任务ID>/`** 落盘：`source.pptx`（原文件副本）、`meta.json`（解析结果）、以及可选的 `previews/` 预览图。左侧 **已存任务** 列表即读取该目录。自定义目录优先使用环境变量 **`ANY2VIDEO_DATA_ROOT`**；旧变量 **`PPT_COURSE_DATA`** 继续兼容。

新版视频项目可通过 **`ANY2VIDEO_WORKSPACE_ROOT`** 和 **`ANY2VIDEO_RENDERER_ROOT`** 覆盖工作区与渲染器路径；旧变量 `VIDEO_WORKSPACE_ROOT`、`VIDEO_RENDERER_ROOT` 仍可使用。

清理本机项目产物时先预览，再明确确认：

```bash
any2video clear-project-data
any2video clear-project-data --yes
```

单文件上传默认上限 **50MB**；若课件更大，可在启动前设置 **`PPT_COURSE_MAX_UPLOAD_MB`**（例如 `200` 或 `500`）并重启 `any2video serve`。前方若有 Nginx 等反代，需同步放宽 `client_max_body_size`。

## 工作台流水线

工作台内的耗时动作走异步 job：

- **`POST /api/tasks/{task_id}/pipeline/jobs`**：创建素材底稿、素材地图、分镜脚本、声音轨检查或成片蓝图任务。
- **`GET /api/pipeline/jobs/{job_id}`**：轮询 `queued / running / succeeded / failed / cancelled` 状态。
- **`POST /api/pipeline/jobs/{job_id}/cancel`**：取消排队任务；运行中的底层步骤会记录取消请求，完成后停止推进。

旧同步接口 **`POST /api/tasks/{task_id}/pipeline/run-step`** 暂保留，用于脚本兼容。

## 导演模块（`ppt_course_rebuilder` 包）

- 与 **`pip install -e .`** 一并安装；由 **any2video Web** 调用（「课程重构 / 导演脚本」区域），无需单独启动服务。
- **CLI 旧管线**（`main.py`、AI 规划 PPTX）仍为可选：见 **`ppt_course_rebuilder/README.md`**。

## 成片引擎（Remotion）

- 见 **`ppt_course_renderer/README.md`** 与 **`docs/ppt_course_renderer_architecture.md`**。
- Remotion 相关 Agent 技能可参考 [remotion-dev/skills](https://github.com/remotion-dev/skills) 中 `skills/remotion/`。

---

远程仓库：`https://github.com/brocademaple/make_lesson_video_zhijian_version`
