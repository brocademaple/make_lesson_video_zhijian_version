# 技术备忘：LibreOffice、Poppler 与 PPT 预览

> **范围**：本文仅针对 **课件处理与工作台**（包 `ppt_course_deal`）里 **Web 整页预览** 与 `slide_render` 相关实现。子目录 **`ppt_course_rebuilder/`**（**AI 课程重构管线**）若单独导出 PNG，见该子项目 `image_exporter` 与文档，与下述 `ppt_course_deal/web` 会话预览不是同一条代码路径。

本文说明在 **课件工作台** **Web 整页预览** 链路中，`LibreOffice` 与 **Poppler（`pdftoppm`）** 各自做什么，以及它们为何能还原「幻灯片画面」（像素图），并与 **文本抽取** 区分。

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

本节记录 **课件工作台** 依赖的「系统级」组件如何安装、如何确认就绪；与 **python-pptx 文本解析** 无关（后者仅需 `pip install` 根目录包）。

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

## 7. 可选延伸阅读（官方 / 项目）

- LibreOffice：`https://www.libreoffice.org/`（命令行文档可参考发行版自带的 `soffice` 帮助）。
- Poppler：`https://poppler.freedesktop.org/`（`pdftoppm` 属 Poppler 工具集）。
- 本仓库流水线入口：`ppt_course_deal/slide_render.py`、`ppt_course_deal/web/app.py` 中解析与预览接口。
- 根目录 **README** 中「整页预览图（LibreOffice + Poppler）」亦有一版精简安装说明，可与本节对照。

---

若后续产品化要在服务器上跑，通常仍是：**容器镜像内预装 `LibreOffice` + `poppler-utils`**，或将渲染外包给专用微服务；本文原理不变。
