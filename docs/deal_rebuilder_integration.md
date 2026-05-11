# deal 与 ppt_course_rebuilder 集成说明

## 产品形态（当前）

| 组件 | 角色 |
|------|------|
| **`ppt_course_deal`** | **唯一 FastAPI + Web 工作台**：上传、解析、预览、音频与外部 API、**原始素材清单与导演脚本 API** |
| **`ppt_course_rebuilder`** | **Python 包**：作为库被 deal **import**；读取 **`raw_material_manifest.json`**，写出 **`director_manifest.json`**；**不**单独监听端口、**不**提供独立 Web 前端 |
| **`ppt_course_renderer`** | **Remotion 工程**：与本阶段改造解耦；成片管线仍以手工 / CLI 为主 |

目录 **`ppt_course_rebuilder/`** 仍保留历史 **`main.py` / `src/`** CLI 管线；与 **`rebuilder` 包根目录**导演模块**并存**，互不从 Web 自动拉起。

## 依赖方向

- **允许**：`ppt_course_deal` → `ppt_course_rebuilder`
- **不允许**：`ppt_course_rebuilder` → `ppt_course_deal.web` 或任务存储实现（导演逻辑仅依赖 manifest **文件路径 / dict**）

## 数据流

1. 用户上传并解析 PPT → 任务目录含 `source.pptx`、`meta.json`、`previews/`。
2. **`POST /api/tasks/{task_id}/raw-material-manifest`** → 生成 **`raw_material_manifest.json`**。
3. **`POST /api/tasks/{task_id}/rebuild-course`** → 若缺 raw manifest 则先补生成；调用 **`rebuild_course_from_raw_manifest`** → **`director_manifest.json`**。
4. **`GET /api/tasks/{task_id}/director-manifest`** → 返回 JSON，供工作台「课程重构 / 导演脚本」区域展示。
5. **`POST .../approve-scene/{scene_id}`** / **`reject-scene`** → 更新 **`director_manifest.json`** 内对应镜头审核状态。
6. **`POST .../export-approved-director-manifest`** → 写出 **`approved_director_manifest.json`**（**不覆盖**原始 `director_manifest.json`）。

## 安装与运行

根目录 **`pip install -e .`** 会安装 **`ppt_course_deal`** 与 **`ppt_course_rebuilder`**（见 **`pyproject.toml`** `packages.find`）。

启动工作台：`ppt-course serve`（与此前一致）。

## 局限（刻意保留）

- 导演逻辑为**启发式**，非 LLM；后续可替换 `director.py` / `narration.py` 内部实现而不改 API 路径。
- **真实生图**、**renderer 大改**、**全自动 input-props** 不在本阶段交付范围。
