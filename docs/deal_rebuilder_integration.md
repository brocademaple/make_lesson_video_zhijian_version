# deal 与 ppt_course_rebuilder 集成说明

## 产品形态（当前）

| 组件 | 角色 |
|------|------|
| **`ppt_course_deal`** | **唯一 FastAPI + Web 工作台**：上传、解析、预览、音频与外部 API、**原始素材清单与导演脚本 API** |
| **`ppt_course_rebuilder`** | **Python 包**：作为库被 deal **import**；读取 **`raw_material_manifest.json`**，生成 **`course_material.json`**、**`director_manifest.json`**，并通过 Render Adapter 写出 **`render_plan/input-props`**；默认优先 Director LLM，失败回退启发式；**不**单独监听端口、**不**提供独立 Web 前端 |
| **`ppt_course_renderer`** | **Remotion 工程**：工作台可为已存任务生成 `render_tasks/<task>/render_plan.json`、`input-props.json` 与本地渲染命令；实际 MP4 渲染仍由本机 Remotion CLI 执行 |

目录 **`ppt_course_rebuilder/`** 仍保留历史 **`main.py` / `src/`** CLI 管线；与 **`rebuilder` 包根目录**导演模块**并存**，互不从 Web 自动拉起。

## 依赖方向

- **允许**：`ppt_course_deal` → `ppt_course_rebuilder`
- **不允许**：`ppt_course_rebuilder` → `ppt_course_deal.web` 或任务存储实现（导演逻辑仅依赖 manifest **文件路径 / dict**）

## 数据流

1. 用户上传并解析 PPT → 任务目录含 `source.pptx`、`meta.json`、`previews/`。
2. **`POST /api/tasks/{task_id}/raw-material-manifest`** → 生成 **`raw_material_manifest.json`**。
3. **`POST /api/tasks/{task_id}/course-material`** → 生成 **`course_material.json`**，统一页文本、整页图、shape 图、音频段、AI 配图、素材标签与推荐 layout。
4. **`POST /api/tasks/{task_id}/rebuild-course`** → 若缺 raw/course material 则先补生成；调用 **`rebuild_course_from_raw_manifest`** → **`director_manifest.json`**；请求体可传 `use_llm`、`llm_max_slides`，响应含 `planning_mode`、`llm_error`、`quality_checks`。
5. **`GET /api/tasks/{task_id}/director-manifest`** → 返回 JSON，供工作台「课程重构 / 导演脚本」区域展示。
6. **`POST .../approve-scene/{scene_id}`** / **`reject-scene`** → 更新 **`director_manifest.json`** 内对应镜头审核状态。
7. **`POST .../export-approved-director-manifest`** → 写出 **`approved_director_manifest.json`**（**不覆盖**原始 `director_manifest.json`）。
8. **`POST /api/tasks/{task_id}/remotion-render-plan`** → 优先读取 approved director，否则读取 director manifest，写出 **`render_plan.json`** 与 **`input-props.json`**；无导演脚本时回退 Deal 元数据直出。

## 安装与运行

根目录 **`pip install -e .`** 会安装 **`ppt_course_deal`** 与 **`ppt_course_rebuilder`**（见 **`pyproject.toml`** `packages.find`）。

启动工作台：`ppt-course serve`（与此前一致）。

## 局限（刻意保留）

- 导演逻辑已支持 **Director LLM 优先 + 启发式回退**；未配置 `director_llm.api_key` 或环境变量 `AI_API_KEY` 时不会阻塞工作台。MiMo Token Plan 推荐 `api_base=https://token-plan-cn.xiaomimimo.com/v1`、`model=mimo-v2.5-pro`。
- **真实生图**、**renderer 大改**、**服务端长耗时渲染队列** 不在本阶段交付范围。
