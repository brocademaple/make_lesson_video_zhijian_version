# GitHub Pages 静态站点（与 `ppt_course_deal` 隔离）

本目录**仅**存放对外展示用 HTML/CSS/图片，**不参与** Python 包 `ppt_course_deal` 的构建与运行。

## 本地预览

在仓库根目录执行：

```bash
cd github-pages && python3 -m http.server 8080
```

浏览器打开 `http://127.0.0.1:8080/`。

## 与线上代码隔离

| 区域 | 用途 |
|------|------|
| `ppt_course_deal/`、`ppt_course_renderer/` 等 | 产品源码 |
| `github-pages/` | 扁平风产品介绍页 + 运行截图（放 `assets/images/`） |

## 发布到 GitHub Pages

GitHub 仓库设置 **Pages** 时，默认只能从 **`/`（仓库根）** 或 **`/docs`** 发布。

任选其一：

1. **使用 `/docs` 作为站点根**  
   将本目录内容**复制或同步**到仓库 `docs/` 下作为站点入口（例如保持 `docs/index.html` 为落地页），注意不要覆盖团队已有的 `docs/*.md` 文档；或使用仅用于 Pages 的分支/工作流。

2. **使用 GitHub Actions**  
   由 Workflow 将 `github-pages/` 构建产物部署到 `gh-pages` 分支或 Pages artifact（需在仓库 **Settings → Pages** 选择 **GitHub Actions** 来源）。

具体以当前仓库的 Pages 策略为准；更新截图时只需替换 `assets/images/` 下文件并提交。
