# any2video 与 ppt_course_rebuilder 集成说明

## 产品形态（当前）

| 组件 | 角色 |
|------|------|
| **`ppt_course_deal`** | **any2video 的兼容 FastAPI + Web 包**：上传、解析、预览、已存任务、音频、外部 API、素材底稿、素材地图、分镜脚本与成片蓝图 |
| **`ppt_course_rebuilder`** | **Python 包**：作为库被 deal **import**；读取 **`raw_material_manifest.json`**，生成 **`course_material.json`**、**`director_manifest.json`**，并通过 Render Adapter 写出 **`render_plan/input-props`**；默认优先 Director LLM，失败回退启发式；不单独监听端口、不提供独立 Web 前端 |
| **`ppt_course_renderer`** | **Remotion 工程**：工作台可为已存任务生成 `render_tasks/<task>/render_plan.json`、`input-props.json` 与本地渲染命令；实际 MP4 渲染由本机 Remotion CLI 执行 |

目录 **`ppt_course_rebuilder/`** 仍保留历史 **`main.py` / `src/`** CLI 管线；与 **`rebuilder` 包根目录**导演模块**并存**，互不从 Web 自动拉起。

## 依赖方向

- **允许**：`ppt_course_deal` → `ppt_course_rebuilder`
- **不允许**：`ppt_course_rebuilder` → `ppt_course_deal.web` 或任务存储实现（导演逻辑仅依赖 manifest **文件路径 / dict**）

## 数据流

1. 用户上传并解析 PPT → 任务目录含 `source.pptx`、`meta.json`、`previews/`。
2. **素材底稿**：`POST /api/tasks/{task_id}/raw-material-manifest` → 生成 **`raw_material_manifest.json`**。
3. **素材地图**：`POST /api/tasks/{task_id}/course-material` → 生成 **`course_material.json`**，统一页文本、整页图、shape 图、音频段、AI 配图、素材标签与推荐 layout。
4. **分镜脚本**：`POST /api/tasks/{task_id}/rebuild-course` → 若缺 raw/course material 则先补生成；调用 **`rebuild_course_from_raw_manifest`** → **`director_manifest.json`**；请求体可传 `use_llm`、`llm_max_slides`，响应含 `planning_mode`、`llm_error`、`quality_checks`。
5. **`GET /api/tasks/{task_id}/director-manifest`** → 返回 JSON，供工作台「课程重构 / 导演脚本」区域展示。
6. **`POST .../approve-scene/{scene_id}`** / **`reject-scene`** → 更新 **`director_manifest.json`** 内对应镜头审核状态。
7. **`POST .../export-approved-director-manifest`** → 写出 **`approved_director_manifest.json`**（**不覆盖**原始 `director_manifest.json`）。
8. **成片蓝图**：`POST /api/tasks/{task_id}/remotion-render-plan` → 优先读取 approved director，否则读取 director manifest，写出 **`render_plan.json`** 与 **`input-props.json`**；无导演脚本时回退 Deal 元数据直出。

## 工作台 job 接口

工作台按钮使用统一异步接口，避免长耗时步骤占住同步 HTTP 请求：

1. **`POST /api/tasks/{task_id}/pipeline/jobs`** 创建任务，请求体沿用 `PipelineRunStepBody`，`step` 可取 `raw_material / course_material / director / audio / render_plan`。
2. **`GET /api/pipeline/jobs/{job_id}`** 轮询状态；返回 `queued / running / succeeded / failed / cancel_requested / cancelled`，成功时 `result` 内含底层产物路径和统计。
3. **`POST /api/pipeline/jobs/{job_id}/cancel`** 取消任务。排队任务会直接取消；运行中的底层函数目前不可强杀，会记录取消请求，并在当前步骤完成后返回 `cancel_requested`。

旧同步接口 **`POST /api/tasks/{task_id}/pipeline/run-step`** 暂时保留，便于本地脚本和已有调用迁移。

## 安装与运行

根目录 **`pip install -e .`** 会安装 **`ppt_course_deal`** 与 **`ppt_course_rebuilder`**（见 **`pyproject.toml`** `packages.find`）。

启动工作台：`any2video serve`。旧命令 `ppt-course serve` 继续兼容。

## 局限（刻意保留）

- 导演逻辑已支持 **Director LLM 优先 + 启发式回退**；未配置 `director_llm.api_key` 或环境变量 `AI_API_KEY` 时不会阻塞工作台。MiMo Token Plan 推荐 `api_base=https://token-plan-cn.xiaomimimo.com/v1`、`model=mimo-v2.5-pro`。
- **真实生图**、**服务端 Remotion 渲染队列** 不在本阶段交付范围；当前 job 包装的是工作台素材/导演/成片蓝图步骤。
