# 技术备忘：LibreOffice、Poppler、PPT 预览、页内小图与 API 文档

## 目录

- [1. 先说清「解析」在本项目里的两层含义](#1-先说清解析在本项目里的两层含义)
- [2. LibreOffice 在本链路里做什么？](#2-libreoffice-在本链路里做什么)
- [3. Poppler（`pdftoppm`）在本链路里做什么？](#3-popplerpdftoppm在本链路里做什么)
- [4. 两条链路如何串起来（与本仓库代码对应）](#4-两条链路如何串起来与本仓库代码对应)
- [5. 与「只用 Python 读 pptx」的对比（小结）](#5-与只用-python-读-pptx的对比小结)
- [6. 本机安装与自检（macOS 实践备忘）](#6-本机安装与自检macos-实践备忘)
  - [6.1 需要安装的两类组件](#61-需要安装的两类组件)
  - [6.2 常见安装方式（Homebrew）](#62-常见安装方式homebrew)
  - [6.3 Cask 安装 LibreOffice 时出现 checksum 不一致](#63-cask-安装-libreoffice-时出现-checksum-不一致)
  - [6.4 自检命令与健康检查](#64-自检命令与健康检查)
  - [6.5 运行本项目时是否需要「打开 LibreOffice」？](#65-运行本项目时是否需要打开-libreoffice)
- [7. 页内「扣小图」是怎么实现的？（与整页预览不是一条路）](#7-页内扣小图是怎么实现的与整页预览不是一条路)
  - [7.1 与全文第 1 节两条「解析」的关系](#71-与全文第-1-节两条解析的关系)
  - [7.2 核心算法（`ppt_course_deal/shape_image_export.py`）](#72-核心算法ppt_course_dealshape_image_exportpy)
  - [7.3 何时写入磁盘、元数据与 API](#73-何时写入磁盘元数据与-api)
  - [7.4 小结](#74-小结)
- [8. Swagger UI、OpenAPI 与智课影擎「全部 API」从哪来？](#8-swagger-uiopenapi-与智课影擎全部-api从哪来)
  - [8.1 Swagger UI 是什么？](#81-swagger-ui-是什么)
  - [8.2 OpenAPI 与 `openapi.json`](#82-openapi-与-openapijson)
  - [8.3 为什么页面上能看到「当前项目的所有 API」？](#83-为什么页面上能看到当前项目的所有-api)
  - [8.4 与本项目产品的对应关系（给人看 vs 给程序看）](#84-与本项目产品的对应关系给人看-vs-给程序看)
  - [8.5 常见误区与排障要点](#85-常见误区与排障要点)
- [9. 可选延伸阅读（官方 / 项目）](#9-可选延伸阅读官方--项目)

> **范围**：本文针对 **智课影擎工作台**（包 `ppt_course_deal`）：**第 1–6 节**为 **Web 整页预览** 与 `slide_render`（LibreOffice + Poppler）；**第 7 节**为 **页内「扣小图」**；**第 8 节**为 **Swagger UI / OpenAPI** 与 **`ppt-course serve`** 暴露的 HTTP API 文档原理。子目录 **`ppt_course_rebuilder/`** 若单独导出 PNG，见该子项目 `image_exporter` 与文档，与下述 `ppt_course_deal` 不是同一条代码路径。

本文说明在 **智课影擎工作台** **Web 整页预览** 链路中，`LibreOffice` 与 **Poppler（`pdftoppm`）** 各自做什么，以及它们为何能还原「幻灯片画面」（像素图），并与 **文本抽取** 区分。

---

## 1. 先说清「解析」在本项目里的两层含义

| 层次 | 工具 | 产出 | 是否等同于 PowerPoint 里的像素画面 |
|------|------|------|--------------------------------------|
| **结构化文本抽取** | `python-pptx` 读 `.pptx`（OOXML） | 标题、`text_blocks`、备注等 | **否**：只有文字与简单结构，不含完整排版渲染 |
| **整页画面预览（本项目预览图）** | `LibreOffice` → `Poppler` | 每页一张 **PNG** | **接近**：按排版引擎「画出来」再栅格化，视觉上接近用办公软件导出 |

因此：**LibreOffice + Poppler 并不是去「解析 OOXML 文本」的主力**——那是 `python-pptx` 的工作；二者负责的是 **把文稿当成版面来渲染，再变成图片**，供浏览器 `<img>` 显示。

实现位置：`ppt_course_deal/slide_render.py` 中函数 `render_pptx_to_pngs`。

---

## 2. LibreOffice 在本链路里做什么？

**LibreOffice** 是一套办公软件套件，内置与 Microsoft Office 类似的 **文档排版与渲染引擎**。在无界面模式下，可通过命令行调用其 **过滤器（filter）**，把 `.pptx` **转换为 PDF**。

本项目使用的典型调用形态为：

```bash
soffice --headless --convert-to pdf --outdir <输出目录> <输入.pptx>
```

含义简述：

- **`--headless`**：不打开图形界面，适合服务端跑。
- **`--convert-to pdf`**：走 LibreOffice 内置的导出管线，相当于用它的版面引擎把幻灯片 **排版结果** 写到 PDF（固定版式、分页）。

**为何这样能对应「PPT 页面」？**

- `.pptx` 内部是 XML + 资源，直接「抽文本」得不到画面。
- LibreOffice 在转换时会 **按自己的布局规则** 解释幻灯片母版、占位符、字体、图片位置等，生成 **可视结果** 的 PDF。这一步本质是 **渲染**，不是简单的解压读字符串。

**局限**：与 PowerPoint / WPS 的像素级一致并非 100%（字体缺失、复杂动画、部分 SmartArt 等可能有差异），但对培训类静态稿通常足够做预览。

---

## 3. Poppler（`pdftoppm`）在本链路里做什么？

**Poppler** 是一套开源 **PDF 渲染库**，常见于 Linux/macOS 工具链。其中的 **`pdftoppm`** 命令用于把 **PDF 的每一页** 光栅化成 **PNG / PPM** 等位图。

本项目中的用法是把上一步得到的 PDF 按页转成 PNG（分辨率由 `-r` 等参数控制），便于前端直接展示：

```bash
pdftoppm -png -r 144 <输入.pdf> <输出前缀>
```

**为何需要这一步？**

- 浏览器最省事展示「一整页的样子」的方式之一是 **图片**。
- PDF 在网页里也可嵌入，但统一成 PNG 便于缩略图列表、同源缓存、与现有 `/api/preview/...` 接口一致。

**LibreOffice 为什么不直接出 PNG？**

- 也可以探索「导出 PNG」类过滤器，但常见、稳定的组合是 **PPTX → PDF（固定版式）→ 按页栅格化**。PDF 作为中间格式，分页清晰，Poppler 专精 PDF 栅格化。

---

## 4. 两条链路如何串起来（与本仓库代码对应）

整体流水线：

```text
.pptx  ──(LibreOffice headless)──►  .pdf  ──(pdftoppm)──►  slide-01.png, slide-02.png, …
```

对应代码：`ppt_course_deal/slide_render.py` 中先 `soffice ... --convert-to pdf`，再在 `png_pages/` 下用 `pdftoppm -png` 生成多张 PNG，排序后返回路径列表。

---

## 5. 与「只用 Python 读 pptx」的对比（小结）

| 问题 | 仅 `python-pptx` | LibreOffice + Poppler |
|------|-------------------|------------------------|
| 能否拿到每页 **像素级外观** | 不能直接生成整页截图 | 可以（PNG） |
| 能否拿到标题、段落文本 | 可以 | 不经由这条链路；本项目仍用 `python-pptx` 抽文本 |
| 依赖 | 纯 Python | 需本机安装 **LibreOffice** 与 **Poppler**，占磁盘与 CPU |

---

## 6. 本机安装与自检（macOS 实践备忘）

本节记录 **智课影擎工作台** 依赖的「系统级」组件如何安装、如何确认就绪；与 **python-pptx 文本解析** 无关（后者仅需 `pip install` 根目录包）。

### 6.1 需要安装的两类组件

| 组件 | 提供的命令 | 作用（与本项目） |
|------|------------|------------------|
| **LibreOffice** | `soffice`（无界面时常用 `--headless`） | 将 `.pptx` 转为中间 **PDF** |
| **Poppler** | `pdftoppm` | 将 PDF 每页栅格化为 **PNG** |

二者缺一不可时，Web 会退回到 **文本占位整页预览**（非像素级幻灯片图）；安装齐全并重启 `ppt-course serve` 后，可走完整预览链路。

### 6.2 常见安装方式（Homebrew）

```bash
brew install poppler
```

LibreOffice 任选其一即可：

- **Cask（命令行一条龙时）**：`brew install --cask libreoffice`  
- **官网安装包**：从 [LibreOffice 下载页](https://www.libreoffice.org/download/download/) 安装 **macOS** 版本，将应用拖入 **「应用程序」**。

Apple Silicon 上 Poppler 安装后，`pdftoppm` 常在 **`/opt/homebrew/bin/pdftoppm`**。本仓库 `slide_render.find_pdftoppm()` 除 `PATH` 外，也会探测该路径，以减轻 **从 IDE 启动服务时 PATH 未包含 Homebrew** 的情况。

### 6.3 Cask 安装 LibreOffice 时出现 checksum 不一致

若 `brew install --cask libreoffice` 报 **SHA-256 / checksum 与预期不符**，多为上游更换安装包与 Homebrew 元数据暂不同步，或本地缓存损坏。可依次尝试：`brew update`、清理该 cask 的下载缓存后重装；仍失败则改用 **官网 DMG 安装到 `/Applications/LibreOffice.app`**（见下节自检，**不依赖** `which soffice`）。

### 6.4 自检命令与健康检查

**命令行（本机）：**

```bash
# Poppler：应能打印版本或路径
which pdftoppm
pdftoppm -v

# LibreOffice：未配置 PATH 时 which 可能为空，仍以 App 内可执行文件为准
test -x /Applications/LibreOffice.app/Contents/MacOS/soffice && echo "LibreOffice OK"
```

**通过正在运行的 Web 服务（推荐）：**

```bash
curl -s http://127.0.0.1:8765/api/health | python3 -m json.tool
```

查看返回中的 **`preview_render`**：

- **`ready`: true**，且 **`libreoffice` / `pdftoppm` 均为 true**：两条依赖均已探测到，与本项目 `describe_preview_render_env()` 一致。
- **`install_hint_zh`** 非空：仍有组件未找到，按提示补装后 **重启** `ppt-course serve`。

### 6.5 运行本项目时是否需要「打开 LibreOffice」？

**不需要**为了预览或解析去手动打开 LibreOffice 图形界面。

- 预览管线调用的是 **`soffice --headless ...`**，每次处理相当于短时后台子进程，**无需**常驻 LibreOffice 窗口。
- 若 **`which soffice`** 无输出，只要 **`/Applications/LibreOffice.app/Contents/MacOS/soffice` 存在且可执行**，本项目仍会选用该路径（见 `slide_render.find_soffice()`）。
- 极少数情况下，**首次**从官网安装后 macOS 安全策略要求用户在「应用程序」里手动打开一次 LibreOffice 以完成信任；一次即可。

---

## 7. 页内「扣小图」是怎么实现的？（与整页预览不是一条路）

产品里常说的 **扣小图**，指把某一页幻灯片里 **插入的图片对象**（Picture）的内嵌位图单独落盘，得到多张 **`shape-0000.png`**（或其它扩展名）的小文件，而不是再跑一次 LibreOffice 把整页裁切。

### 7.1 与全文第 1 节两条「解析」的关系

| 链路 | 依赖 | 产出 |
|------|------|------|
| **整页像素预览** | LibreOffice → PDF → Poppler | `slide-NNNN.png` / `slide-NNNN/full.png`，接近屏幕上看一整页 |
| **页内小图** | 仅用 **`python-pptx`** 读 OOXML | `slide-NNNN/shapes/shape-XXXX.ext`，每张对应一个 **PICTURE** 形状的内嵌二进制 |

二者互补：**整页图**解决「版式长什么样」；**小图**解决「页面上每张插图的原素材文件是什么」（可用于对齐、替换素材或下游管线）。

### 7.2 核心算法（`ppt_course_deal/shape_image_export.py`）

1. **`Presentation(path)`** 打开与任务同目录落盘的 **`source.pptx`**（与解析时上传的副本一致）。
2. 对每一页 `slide`，遍历 `slide.shapes`；对 **组合（GROUP）** 用 **`_iter_shapes_recursive`** 递归进子形状，避免漏掉组内图片。
3. 只处理 **`MSO_SHAPE_TYPE.PICTURE`** 的形状；其它类型（纯文本框、自绘图形、表格等）跳过。
4. 对每个图片形状取 **`shape.image.blob`**（及 **`image.ext`** 推断扩展名），写入  
   **`previews/slide-{页索引四位}/shapes/shape-{序号四位}.{ext}`**，序号按遍历顺序递增。
5. 扩展名会做白名单规范化（未知扩展名时退回 **`png`**）；导出异常的形状记日志并跳过，不中断整页。

**不包含**：图表（Chart）、SmartArt、公式对象等 **无法** 用「`PICTURE` 形状 + `image.blob`」直接取出的对象——这类在本链路里不会当作一张「可抠的内嵌图」导出。

### 7.3 何时写入磁盘、元数据与 API

- **触发时机**：持久化任务时，`ppt_course_deal/task_storage.py` 的 **`save_task_from_parse`** 在写完顶层 **`slide-NNNN.png`**（若有）之后，调用 **`populate_slide_preview_folders`**，同步生成各页 **`full.png`**（与顶层整页图相同文件的副本）与 **`shapes/`** 下小图列表。
- **`meta.json`**：增加 **`shape_image_manifest`**，按页记录是否有 **`full`**、以及该页 **`shapes`** 文件名列表，便于排查与前端展示。
- **HTTP**：`GET /api/tasks/{task_id}/slide/{slide_index}/shapes` 列出文件名；`GET .../shape/{shape_index}` 按 **`natural_shape_sort_key`** 排序后按下标取文件（与列表顺序一致）。
- **工作台 UI**：当前会话存在 **task_id**（含解析后已落盘的任务）时，前端将 **整页预览** 与上述 **shape** 图片 URL 组成 **轮播**（整页为第一帧，其后为各切图），与仅会话、未绑定任务的上传流程（无切图 API）区分。

### 7.4 小结

**扣小图** = **`python-pptx` 枚举 PICTURE 形状 → 写 `image.blob`**，不依赖 LibreOffice/Poppler；与 **整页预览** 是否成功无关（即便没有整页 PNG，只要 `source.pptx` 可读，仍可对页内插图做小图导出）。

---

## 8. Swagger UI、OpenAPI 与智课影擎「全部 API」从哪来？

本节说明：浏览器里 **`/docs`**（Swagger UI）、**`/openapi.json`** 与 **`ppt_course_deal/web/app.py`** 里注册的接口之间的关系——**不是** Swagger「扫描磁盘自动生成 Python 路由」，而是 **FastAPI 根据已注册路由与类型注解汇总出一份 OpenAPI 描述**，Swagger UI 只负责把这份描述 **画成网页并支持调试**。

### 8.1 Swagger UI 是什么？

**Swagger UI** 是一套开源 **前端页面**：向服务端请求一份 **API 描述**（本项目默认 **`GET /openapi.json`**），把其中的路径、方法、参数、请求体、响应结构 **渲染**成可读的文档，并提供 **Try it out** 发起真实 HTTP 请求。它 **不包含** 课件解析、MiniMax 等业务逻辑；本质是 **OpenAPI 说明书 + 交互式调试壳**。

### 8.2 OpenAPI 与 `openapi.json`

**OpenAPI**（早年常称 Swagger 规范）约定了一种 **JSON/YAML** 格式，用来机器可读地描述 REST API：有哪些路径、每种 HTTP 方法、Query/Path/Body 的形状、响应大致类型等。

FastAPI 在运行时会 **生成** 满足该规范的一份字典，并通过 **`GET /openapi.json`**（默认路径）暴露。**Swagger UI（`/docs`）** 页面加载后，会用 JavaScript **再请求** `/openapi.json`，据此绘制界面。若 **`openapi.json` 生成失败或返回 500**，页面外壳可能仍能打开，但会提示 **Failed to load API definition**——因为缺少那份描述文件。

### 8.3 为什么页面上能看到「当前项目的所有 API」？

Web 服务使用 **`ppt_course_deal.web.app` 里的单个 FastAPI `app`**，所有路由（如 **`@application.get`**、**`@application.post`**）都 **注册在同一应用实例**上。FastAPI 在构建 OpenAPI schema 时，会 **遍历这些路由**，并结合：

- 路径参数、查询参数、**Pydantic 请求体模型**；
- 返回值注解（若有）；
- `Query` / `Path` / `Body` 等附加元数据；

汇总成 **一份完整的 OpenAPI 文档**。因此：**凡是挂在这个 `app` 上的接口**，都会出现在 **`openapi.json`** 里；Swagger UI **只是完整展示**这份 JSON，看起来像「自动列出了项目里所有 API」——本质是 **框架根据路由与类型定义自动生成说明书**，而不是 Swagger 单独去「发现」业务代码。

实现入口：**`ppt_course_deal/web/app.py`** 中 **`create_app()`**；命令 **`ppt-course serve`** 通过 **uvicorn** 加载 **`ppt_course_deal.web.app:app`**。

### 8.4 与本项目产品的对应关系（给人看 vs 给程序看）

| 地址 | 用途 |
|------|------|
| **`GET /docs`** | 人类可读的 **Swagger UI**（网页调试）。工作台顶栏 **「API」** 链到此处（新标签打开）。 |
| **`GET /openapi.json`** | **机器可读**的 OpenAPI JSON；可用于客户端代码生成、契约对照、**`ppt_course_rebuilder`** 等外部工具拉取 **与本机服务一致的接口列表**。 |
| **`GET /redoc`** | FastAPI 自带的 **ReDoc** 风格文档（若未关闭），同样依赖同一份 OpenAPI schema。 |

三者 **共用同一份** OpenAPI 描述；维护接口时只需改 **FastAPI 路由与 Pydantic 模型**，文档会随 **重启服务** 后的 schema 生成而更新（无需手写 Swagger YAML）。

### 8.5 常见误区与排障要点

- **误区**：以为 Swagger「实现了」接口——实现始终在 **`app.py`** 与各模块里；Swagger 仅展示与试调。
- **排障**：若 **`/openapi.json` 500**，多为 **OpenAPI 生成阶段异常**（例如历史上请求体参数命名为保留名 **`body`** 导致 Pydantic 无法完全解析、或模型定义不当）。此时应看 **服务启动日志**（本项目可在 **lifespan** 里预调用 **`app.openapi()`** 以便尽早打 ERROR），并修复路由/模型后再访问 **`/docs`**。

---

## 9. 可选延伸阅读（官方 / 项目）

- OpenAPI 规范说明：`https://www.openapis.org/`（**Swagger UI** 上游一般为 **swagger-api/swagger-ui**；概念上以 **OpenAPI** 为准）。
- LibreOffice：`https://www.libreoffice.org/`（命令行文档可参考发行版自带的 `soffice` 帮助）。
- Poppler：`https://poppler.freedesktop.org/`（`pdftoppm` 属 Poppler 工具集）。
- 本仓库流水线入口：`ppt_course_deal/slide_render.py`、`ppt_course_deal/shape_image_export.py`、`ppt_course_deal/task_storage.py`、`ppt_course_deal/web/app.py` 中解析、预览、任务持久化与 **HTTP API**（OpenAPI 见上文 **第 8 节**）。
- 根目录 **README** 中「整页预览图（LibreOffice + Poppler）」亦有一版精简安装说明，可与本节对照。

---

若后续产品化要在服务器上跑，通常仍是：**容器镜像内预装 `LibreOffice` + `poppler-utils`**，或将渲染外包给专用微服务；本文原理不变。
