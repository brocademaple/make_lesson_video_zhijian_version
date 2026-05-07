# make_lesson_video_zhijian_version

文字密集型培训 **PPT → 课程化 PPTX** 工具集；并预留 **Remotion** 视频成片管线。

详细已实现能力与版本说明见：**[docs/已实现功能说明.md](docs/已实现功能说明.md)**。

---

## 模块怎么区分（命名与目录）

| 中文定位 | 代码位置 | 典型用法 |
|----------|----------|----------|
| **课件处理与工作台** | Python 包 **`ppt_course_deal`**（PyPI 元数据名 `ppt-course-mvp`，命令 **`ppt-course`**） | **默认主力**：本机 **Web 工作台**（上传、预览、已存任务、课程化下载、音频与外部 API 等）+ CLI **`ppt-course transform` / `serve`**；课程化走 **启发式规则流水线**，**不依赖** Rebuilder 里的 LLM。 |
| **视频渲染（Remotion）** | 目录 **`ppt_course_renderer/`** | 与 `ppt_course_deal` **平行**：接收每页图、TTS 音频、逐字稿，生成 Remotion 合成数据并导出成片；见该目录 **README** 与 [remotion-dev/remotion](https://github.com/remotion-dev/remotion)。**工程文件将在该目录内增量添加。** |
| **AI 课程重构管线（Rebuilder）** | 目录 **`ppt_course_rebuilder/`** | **可选、当前非主线**：需 **OpenAI 兼容 API**，跑「分析 → 规划 → 模板生成」与 `output/` 等产物。与 deal / renderer **未做自动串联**；完整 Agent 向扩展可在 deal→renderer 管线调通后再推进。 |
| **GitHub Pages 静态介绍页** | 目录 **`github-pages/`** | **与运行时代码隔离**：仅 HTML/CSS/截图占位；本地预览见该目录 **README**；发布需在仓库 **Settings → Pages** 选择根目录、`/docs` 或 **GitHub Actions** 将本目录产物上线。 |

**不是**「Web = 调试用、Rebuilder = 正式」：日常以 **deal 工作台** 为主；**renderer** 负责成片；Rebuilder 是另一条 **AI 重型** 批处理线。

---

## 快速开始（根目录包 / 课件处理）

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
ppt-course serve    # Web：默认 http://127.0.0.1:8765/
# 或
ppt-course transform /path/to/原始.pptx
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

## AI 课程重构管线（子项目，可选）

- 进入 **`ppt_course_rebuilder/`**，按该目录内 **`README.md`** 单独建 venv、配置 `.env` 后执行 `python main.py ...`（与根目录 `pip install -e .` 无强制关系）。

## 视频渲染（子项目，建设中）

- 见 **`ppt_course_renderer/README.md`**；Remotion 相关 Agent 技能可参考 [remotion-dev/skills](https://github.com/remotion-dev/skills) 中 `skills/remotion/`。

---

远程仓库：`https://github.com/brocademaple/make_lesson_video_zhijian_version`
