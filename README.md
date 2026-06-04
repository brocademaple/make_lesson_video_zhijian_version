# 智课影擎

面向培训内容生产的本地工作台：把 **PPT** 入仓，拆成素材地图和分镜脚本，补齐声音轨，再交给 **Remotion** 生成视频成片。

详细已实现能力与版本说明见：**[docs/已实现功能说明.md](docs/已实现功能说明.md)**。

---

## 模块怎么区分（命名与目录）

| 中文定位 | 代码位置 | 典型用法 |
|----------|----------|----------|
| **智课影擎工作台** | Python 包 **`ppt_course_deal`**（PyPI 元数据名 `ppt-course-mvp`，命令 **`ppt-course`**） | **唯一 Web 入口**：本机 **FastAPI + 静态前端**（上传、预览、已存任务、音频与外部 API、素材底稿 / 素材地图 / 分镜脚本 / 成片蓝图等）+ CLI **`ppt-course transform` / `serve`**。历史的课件版式转换仍保留为启发式 CLI/API 能力。 |
| **成片引擎（Remotion）** | 目录 **`ppt_course_renderer/`** | 与 `ppt_course_deal` 平行：接收每页图、TTS 音频、逐字稿，生成 Remotion 合成数据并导出成片；见该目录 **README**。工作台可为已存任务生成 **`render_tasks/<task>/render_plan.json`** / **`input-props.json`** 并返回本地渲染命令。 |
| **导演模块（Rebuilder 库）** | 目录 **`ppt_course_rebuilder/`**（包名 **`ppt_course_rebuilder`**） | 作为 **Python 库**被 **`ppt_course_deal` import**：读 **`raw_material_manifest.json`**，生成 **`course_material.json`**，写 **`director_manifest.json`**，再通过 adapter 转成 Remotion **`render_plan/input-props`**；默认优先使用本机 **`director_llm`**（MiMo / OpenAI 兼容），失败自动回退启发式。 |
| **GitHub Pages 静态介绍页** | 目录 **`github-pages/`** | **与运行时代码隔离**：仅 HTML/CSS/截图占位；本地预览见该目录 **README**；发布需在仓库 **Settings → Pages** 选择根目录、`/docs` 或 **GitHub Actions** 将本目录产物上线。 |

日常以 **智课影擎工作台** 为唯一产品入口；**renderer** 负责成片；**导演模块**负责「素材底稿 → 素材地图 → 分镜脚本 → 审核」中间层（详见 **`docs/deal_rebuilder_integration.md`**、**`docs/director_manifest_contract.md`**）。

---

## 快速开始

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
ppt-course serve    # Web：默认 http://127.0.0.1:8765/（默认开启 **--reload**，改代码后自动重载；常驻可加 **--no-reload**）
# 或
ppt-course transform /path/to/原始.pptx   # 可选：保留历史 PPTX 版式转换能力
```

### 整页预览图（LibreOffice + Poppler）

工作台左侧缩略图 / 右侧大图若要显示 **真实幻灯片像素图**（而非文本占位图），本机需安装：

- **LibreOffice**（提供 `soffice`，用于 PPTX→PDF）
- **Poppler**（提供 `pdftoppm`，用于 PDF→PNG）

**macOS（Homebrew）示例：**

```bash
brew install --cask libreoffice
brew install poppler
```

安装后 **重启** `ppt-course serve`。打开页面时若依赖未就绪，上传区会显示简要提示；也可访问 **`GET /api/health`** 查看 `preview_render.ready` 与路径探测结果。

### 本地上传与「已存任务」

在 Web 里**上传并成功解析**一份 `.pptx` 后，会在仓库根目录 **`ppt_course_data/tasks/<任务ID>/`** 落盘：`source.pptx`（原文件副本）、`meta.json`（解析结果）、以及可选的 `previews/` 预览图。左侧 **已存任务** 列表即读取该目录。自定义目录可设置环境变量 **`PPT_COURSE_DATA`**（指向数据根路径，其下仍为 `tasks/`）。

单文件上传默认上限 **50MB**；若课件更大，可在启动前设置 **`PPT_COURSE_MAX_UPLOAD_MB`**（例如 `200` 或 `500`）并重启 `ppt-course serve`。前方若有 Nginx 等反代，需同步放宽 `client_max_body_size`。

## 工作台流水线

工作台内的耗时动作走异步 job：

- **`POST /api/tasks/{task_id}/pipeline/jobs`**：创建素材底稿、素材地图、分镜脚本、声音轨检查或成片蓝图任务。
- **`GET /api/pipeline/jobs/{job_id}`**：轮询 `queued / running / succeeded / failed / cancelled` 状态。
- **`POST /api/pipeline/jobs/{job_id}/cancel`**：取消排队任务；运行中的底层步骤会记录取消请求，完成后停止推进。

旧同步接口 **`POST /api/tasks/{task_id}/pipeline/run-step`** 暂保留，用于脚本兼容。

## 导演模块（`ppt_course_rebuilder` 包）

- 与 **`pip install -e .`** 一并安装；由 **deal Web** 调用（「课程重构 / 导演脚本」区域），无需单独启动服务。
- **CLI 旧管线**（`main.py`、AI 规划 PPTX）仍为可选：见 **`ppt_course_rebuilder/README.md`**。

## 成片引擎（Remotion）

- 见 **`ppt_course_renderer/README.md`** 与 **`docs/ppt_course_renderer_architecture.md`**。
- Remotion 相关 Agent 技能可参考 [remotion-dev/skills](https://github.com/remotion-dev/skills) 中 `skills/remotion/`。

---

远程仓库：`https://github.com/brocademaple/make_lesson_video_zhijian_version`
