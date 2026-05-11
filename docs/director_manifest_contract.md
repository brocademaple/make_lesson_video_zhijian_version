# director_manifest 契约说明（初版）

本文描述任务目录下的 **`director_manifest.json`** 与 **`raw_material_manifest.json`** 的字段含义与约束，供 `ppt_course_deal`、**`ppt_course_rebuilder`** 与后续 **`ppt_course_renderer`** 对齐。

## 范围与当前阶段

- **导演脚本生成**当前为**启发式规则**（关键词分镜、固定口播模板），**未**接入真实 LLM。
- **口播 / TTS / 字幕**由规则生成；**未**依赖真实音频文件做字级对齐。
- **生图 / 外部 Skill**字段仅占位；**未**调用 production 级文生图 API。
- **`audio_hash`** 在没有音频成品时可为占位或与内容无关的稳定哈希；后续接入 TTS 成片后可改为绑定音频文件。

## 文件位置（默认数据根）

数据根为 **`ppt_course_data/`**（或环境变量 **`PPT_COURSE_DATA`**）。任务目录：

`ppt_course_data/tasks/<task_id>/`

| 文件 | 说明 |
|------|------|
| `raw_material_manifest.json` | 由 **`ppt_course_deal.raw_material_manifest.build_raw_material_manifest`** 从 `meta.json`、`previews/` 汇总 |
| `director_manifest.json` | 由 **`ppt_course_rebuilder.director.rebuild_course_from_raw_manifest`** 写出 |
| `approved_director_manifest.json` | 由 **`ppt_course_rebuilder.review.export_approved_manifest`** 导出（仅审核通过的 `scenes`，另附 `rejected_items`） |

## raw_material_manifest.json

| 字段 | 类型 | 说明 |
|------|------|------|
| `task_id` | string | UUID 任务 ID |
| `source_pptx` | string | 相对任务目录，一般为 `source.pptx` |
| `task_root` | string | 任务目录绝对路径 |
| `slides` | array | 每页一项 |

单页 **`slides[]`**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `slide_id` | string | 如 `slide-0000` |
| `slide_index` | int | 从 0 起 |
| `full_page_png` | string \| null | 相对 `task_root`，优先 `previews/slide-NNNN/full.png`，否则扁平 `previews/slide-NNNN.png` |
| `raw_text` | string | 来自解析 `text` / `text_blocks` |
| `speaker_notes` | string \| null | 演讲者备注 |
| `shapes` | array | 页内导出图片形状 |

单形状 **`shapes[]`**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `shape_id` | string | 稳定标识 |
| `image_path` | string | 相对 `task_root` |
| `bbox` | object \| null | 预留 |
| `ocr_text` | string \| null | 预留 |
| `source_type` | string \| null | 如 `picture_shape` |

## director_manifest.json

| 字段 | 类型 | 说明 |
|------|------|------|
| `task_id` | string | 与任务一致 |
| `course` | object | `CourseInfo`：标题、受众、目标、版本 |
| `assets` | array | `AssetSpec`，由 **`tag_assets`** 汇总 |
| `scenes` | array | `SceneSpec`，每页至少一条镜头（初版） |
| `review` | object | 汇总：`pending_count` / `approved_count` / `rejected_count` |
| `generated_at` | string | ISO8601 UTC |

### SceneSpec（镜头）

每条 **`scenes[]`** 至少包含：

- **标识**：`scene_id`、`scene_type`、`source_slide_ids`
- **教学**：`learning_goal`、`title`、`onscreen_text`
- **口播**：`narration`（审核长稿）、`tts_text`（合成口语稿）、`subtitle_text`
- **字幕**：`subtitle.segments`：`{ start_sec, end_sec, text }[]`（句级，均匀时长）
- **时间与哈希**：`timing.estimated_duration_sec`、`content_hash`、`asset_hash`、`audio_hash`、`render_cache_key`
- **画面**：`screen_design`（含 `visual_strategy`）、`visual_generation`（占位）
- **审核**：`review_status`（`pending` \| `approved` \| `rejected`）、可选 `reject_reason`、`risk_flags`、`version`

### AssetSpec（素材）

关键字段：`asset_id`、`source`、`source_slide_id`、`path`、`asset_type`、`semantic_tags`、`transparent`、`quality_status`、`usage_suggestion`、`review_status`。

`asset_type` 初版可能为 `full_slide`、`logo`、`icon`、`screenshot`、`decoration`、`unknown` 等；**unknown 不得导致流水线失败**。

## 与 Remotion 的衔接（后续）

当前 **`ppt_course_renderer`** 仍主要消费 **`input-props.json`**（音频路径、时长、图片路径等）。将 **`director_manifest`** 转为 **`input-props`** 的映射规则可在导演层稳定后再实现；本文不预设已实现自动化映射。
