import path from "path";

/**
 * 仓库根目录（含 `ppt_course_deal/`、`ppt_course_data/`）。
 * 在 `ppt_course_renderer/` 下执行 CLI 时默认为上一级；也可通过环境变量覆盖（便于 Studio / CI）。
 */
export const getWorkspaceRoot = (): string => {
  if (process.env.REMOTION_WORKSPACE_ROOT) {
    return process.env.REMOTION_WORKSPACE_ROOT;
  }
  return path.resolve(process.cwd(), "..");
};

/**
 * 浏览器（Studio / `remotion render` 的 Chromium 页）里必须用 **http(s)** 访问素材：从
 * `http://` 页面加载 `file://` 图片会被拦截，`<Img>` 会报 “Error loading image”。
 * Remotion 将 **`public/`** 挂到当前站点根，故在 **`public/ppt_course_data` → 仓库
 * `ppt_course_data` 的符号链接** 存在时，用 **`origin + "/" + 相对仓库根路径`** 即可。
 *
 * 非浏览器环境（如有）仍解析为绝对磁盘路径，再经 {@link absPathToFileUrl} 转 `file://`。
 */
export const resolveUnderRoot = (
  root: string,
  relativePath: string,
): string => {
  const clean = relativePath.replace(/^\/+/, "");
  if (typeof window !== "undefined") {
    const origin =
      typeof window.location !== "undefined"
        ? window.location.origin
        : "http://localhost:3000";
    return `${origin}/${clean}`;
  }
  return path.resolve(root, clean);
};

/** 将绝对路径转为可在 Chromium / Img 中使用的 file URL（避免直接依赖 node:url 以兼容打包）。 */
export const absPathToFileUrl = (absPath: string): string => {
  // If it's already a URL, return as is
  if (absPath.startsWith('http://') || absPath.startsWith('https://')) {
    return absPath;
  }

  // In browser environment, if it's already a relative path, return as is
  if (typeof window !== 'undefined' && !absPath.startsWith('/')) {
    return absPath;
  }

  const normalized = absPath.replace(/\\/g, "/");
  if (/^[A-Za-z]:\//.test(normalized)) {
    return `file:///${normalized}`;
  }
  if (normalized.startsWith("/")) {
    return `file://${normalized}`;
  }
  return `file://${normalized}`;
};
