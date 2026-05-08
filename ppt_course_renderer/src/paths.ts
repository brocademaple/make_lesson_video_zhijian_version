import path from "node:path";

/**
 * 仓库根目录（含 `ppt_course_deal/`、`ppt_course_data/`）。
 * 在 `ppt_course_renderer/` 下执行 CLI 时默认为上一级；也可通过环境变量覆盖（便于 Studio / CI）。
 */
export const getWorkspaceRoot = (): string => {
  if (process.env.REMOTION_WORKSPACE_ROOT) {
    return path.resolve(process.env.REMOTION_WORKSPACE_ROOT);
  }
  return path.resolve(process.cwd(), "..");
};

export const resolveUnderRoot = (
  root: string,
  relativePath: string,
): string => {
  return path.resolve(root, relativePath);
};

/** 将绝对路径转为可在 Chromium / Img 中使用的 file URL（避免直接依赖 node:url 以兼容打包）。 */
export const absPathToFileUrl = (absPath: string): string => {
  const normalized = absPath.replace(/\\/g, "/");
  if (/^[A-Za-z]:\//.test(normalized)) {
    return `file:///${normalized}`;
  }
  if (normalized.startsWith("/")) {
    return `file://${normalized}`;
  }
  return `file://${normalized}`;
};
