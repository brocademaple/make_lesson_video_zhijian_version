# PPT 课程化重构工具（MVP）

面向新兵营 / 质检培训等**规则密集型**业务课件：把文字很多的原始 `.pptx`，自动重构为更适合**录播视频**的课程型幻灯片（更少屏幕字、更清晰节奏、配套口播稿）。**业务准确性优先**：不编造规则、不改动处罚含义；所有课程页保留 `source_slide_indexes` 便于人工复核。

## 功能概览

1. **读取**原始 PPTX（文本、表格/图片计数、备注等）
2. **AI 单页分析** → `output/slide_analysis.json`
3. **AI 课程规划** → `output/course_slides.json`（失败时使用保守兜底规划）
4. **模板渲染**生成新版 `output/course_rebuilt.pptx`
5. **逐页讲稿** → `output/page_scripts.md`（供 TTS）
6. 可选：`--export-images` + 本机 LibreOffice 导出 PNG 至 `output/exported_images/`

## 安装

```bash
cd ppt_course_rebuilder
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

复制环境变量模板：

```bash
cp .env.example .env
# 编辑 .env 填入 AI_API_KEY（OpenAI 兼容接口）
```

## 环境变量

| 变量 | 说明 |
|------|------|
| `AI_API_KEY` | API Key（勿提交仓库） |
| `AI_BASE_URL` | 兼容 OpenAI 的 Base URL，默认 `https://api.openai.com/v1` |
| `AI_MODEL` | 模型名，默认 `gpt-4.1-mini` |

## 运行命令

将原始课件保存为 `input/original.pptx`，然后：

```bash
# 全流程（分析 → 规划 → 生成 PPTX + 讲稿）
python main.py --input input/original.pptx --output output/course_rebuilt.pptx --mode full

# 仅分析（输出 slide_analysis.json）
python main.py --mode analyze --input input/original.pptx

# 仅规划（依赖已有 slide_analysis.json）
python main.py --mode plan

# 仅生成（依赖课程 JSON）
python main.py --mode build --course-slides output/course_slides.json --output output/course_rebuilt.pptx

# 无 API Key 时，可用示例 JSON 测模板与生成
python main.py --mode build --course-slides output/sample_course_slides.json --output output/demo_from_sample.pptx
```

可选：导出分页 PNG（需安装 LibreOffice / `soffice` 在 PATH）：

```bash
python main.py --mode full --input input/original.pptx --export-images
```

加 `-v` 可查看调试日志。

## 输入 / 输出（固定于 `output/`）

| 文件 | 说明 |
|------|------|
| `output/slide_analysis.json` | 每页结构化分析结果 |
| `output/course_slides.json` | 课程页脚本（生成 PPTX 的依据） |
| `output/course_rebuilt.pptx` | 新课程幻灯片 |
| `output/page_scripts.md` | 逐页口播稿 |
| `output/summary_report.json` | 运行摘要（错误与警告） |
| `output/exported_images/` | 可选 PNG 导出目录 |
| `output/sample_course_slides.json` | **无 API 时**用于测试 `build` 的样例 |

## 支持的课程页类型（`CourseSlide.type`）

- `title`：标题页  
- `agenda`：路线 / 目录  
- `transition`：章节过渡  
- `rule_card`：规则卡  
- `case_dialogue`：案例对话  
- `quiz`：互动题（配合 `quiz` 字段）  
- `explanation`：解析页  
- `summary`：总结 / 口诀  

模板逻辑见 `src/template_engine.py`，视觉常量见 `templates/theme.py`。替换 `templates/assets/` 下 PNG 可快速换图标（预留后续图床 URL 字段：`image_url`、`asset_urls`）。

## 修改模板

- **版式与配色**：编辑 `templates/theme.py`（主色深蓝 / 洋葱紫 / 警示红）。  
- **各类型排版**：编辑 `src/template_engine.py` 中对应 `render_*` 函数。  
- **图标**：`templates/assets/`（首跑 build 若缺省会自动生成占位 PNG）。

## 后续扩展（预留）

- 图床 / 生图：`CourseSlide.image_prompt`、`visual_suggestion` → 外部 Skill → `image_url`  
- TTS：直接消费 `page_scripts.md` 或 `narration` 字段  
- 视频合成：导出 PNG / 备注轨对接剪辑管线  

## 当前刻意未做

复杂 Web UI、账号体系、真实图床、自动生图、复杂动画、剪映自动化、视频合成；LibreOffice 仅为可选依赖。

## 业务准确性说明

提示词中要求模型：不虚构规则、不调整处罚档位；规划失败时使用**保守兜底**（每页一张 `rule_card`），请务必人工复核后再用于正式培训。
