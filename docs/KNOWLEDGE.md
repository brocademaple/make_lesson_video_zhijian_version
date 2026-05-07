# 技术备忘：LibreOffice、Poppler 与 PPT 预览

本文说明在本仓库 **Web 整页预览** 链路中，`LibreOffice` 与 **Poppler（`pdftoppm`）** 各自做什么，以及它们为何能还原「幻灯片画面」（像素图），并与 **文本抽取** 区分。

---

## 1. 先说清「解析」在本项目里的两层含义

| 层次 | 工具 | 产出 | 是否等同于 PowerPoint 里的像素画面 |
|------|------|------|--------------------------------------|
| **结构化文本抽取** | `python-pptx` 读 `.pptx`（OOXML） | 标题、`text_blocks`、备注等 | **否**：只有文字与简单结构，不含完整排版渲染 |
| **整页画面预览（本项目预览图）** | `LibreOffice` → `Poppler` | 每页一张 **PNG** | **接近**：按排版引擎「画出来」再栅格化，视觉上接近用办公软件导出 |

因此：**LibreOffice + Poppler 并不是去「解析 OOXML 文本」的主力**——那是 `python-pptx` 的工作；二者负责的是 **把文稿当成版面来渲染，再变成图片**，供浏览器 `<img>` 显示。

实现位置：`ppt_course/slide_render.py` 中函数 `render_pptx_to_pngs`。

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

对应代码：`ppt_course/slide_render.py` 中先 `soffice ... --convert-to pdf`，再在 `png_pages/` 下用 `pdftoppm -png` 生成多张 PNG，排序后返回路径列表。

---

## 5. 与「只用 Python 读 pptx」的对比（小结）

| 问题 | 仅 `python-pptx` | LibreOffice + Poppler |
|------|-------------------|------------------------|
| 能否拿到每页 **像素级外观** | 不能直接生成整页截图 | 可以（PNG） |
| 能否拿到标题、段落文本 | 可以 | 不经由这条链路；本项目仍用 `python-pptx` 抽文本 |
| 依赖 | 纯 Python | 需本机安装 **LibreOffice** 与 **Poppler**，占磁盘与 CPU |

---

## 6. 可选延伸阅读（官方 / 项目）

- LibreOffice：`https://www.libreoffice.org/`（命令行文档可参考发行版自带的 `soffice` 帮助）。
- Poppler：`https://poppler.freedesktop.org/`（`pdftoppm` 属 Poppler 工具集）。
- 本仓库流水线入口：`ppt_course/slide_render.py`、`ppt_course/web/app.py` 中解析与预览接口。

---

若后续产品化要在服务器上跑，通常仍是：**容器镜像内预装 `LibreOffice` + `poppler-utils`**，或将渲染外包给专用微服务；本文原理不变。
