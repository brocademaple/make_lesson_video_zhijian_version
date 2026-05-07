# make_lesson_video_zhijian_version

文字密集型培训 **PPT → 课程化 PPTX** 工具集：含 **`ppt_course`** 命令行与本机 Web，以及可选子项目 **`ppt_course_rebuilder`**（AI 规划版 CLI）。

详细已实现能力与版本说明见：**[docs/已实现功能说明.md](docs/已实现功能说明.md)**。

## 快速开始（根目录包）

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
ppt-course serve    # Web：默认 http://127.0.0.1:8765/
# 或
ppt-course transform /path/to/原始.pptx
```

### 本地上传与「已存任务」

在 Web 里**上传并成功解析**一份 `.pptx` 后，会在仓库根目录 **`ppt_course_data/tasks/<任务ID>/`** 落盘：`source.pptx`（原文件副本）、`meta.json`（解析结果）、以及可选的 `previews/` 预览图。左侧 **已存任务** 列表即读取该目录。自定义目录可设置环境变量 **`PPT_COURSE_DATA`**（指向数据根路径，其下仍为 `tasks/`）。

## 子项目

- **`ppt_course_rebuilder/`**：独立 `requirements.txt` 与 `main.py`，见该目录 `README.md`。

---

远程仓库：`https://github.com/brocademaple/make_lesson_video_zhijian_version`
