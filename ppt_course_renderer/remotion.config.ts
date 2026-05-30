/**
 * Note: When using the Node.JS APIs, the config file
 * doesn't apply. Instead, pass options directly to the APIs.
 *
 * All configuration options: https://remotion.dev/docs/config
 */

import path from "path";
import { Config } from "@remotion/cli/config";
import { enableTailwind } from '@remotion/tailwind-v4';

/**
 * `input-props` 里素材路径为「相对仓库根」的 `ppt_course_data/...`。
 * 通过 tracked symlink `public/ppt_course_data -> ../../ppt_course_data` 暴露课件数据。
 * 不把 public dir 设为仓库根，避免 Remotion 打包时复制 `.git`、agent skills、
 * node_modules 等与渲染无关的本地目录。
 */
const workspaceRoot =
  process.env.REMOTION_WORKSPACE_ROOT &&
  process.env.REMOTION_WORKSPACE_ROOT.length > 0
    ? path.resolve(process.env.REMOTION_WORKSPACE_ROOT)
    : path.resolve(process.cwd(), "..");
const publicRoot =
  process.env.REMOTION_PUBLIC_ROOT && process.env.REMOTION_PUBLIC_ROOT.length > 0
    ? path.resolve(process.env.REMOTION_PUBLIC_ROOT)
    : path.join(workspaceRoot, "ppt_course_renderer", "public");

Config.setPublicDir(publicRoot);

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.overrideWebpackConfig(enableTailwind);
Config.overrideWebpackConfig((currentConfiguration) => {
	return {
		...currentConfiguration,
		cache: false,
		resolve: {
			...currentConfiguration.resolve,
			alias: {
				...currentConfiguration.resolve?.alias,
				path: 'path-browserify',
			},
			fallback: {
				...currentConfiguration.resolve?.fallback,
				path: require.resolve('path-browserify'),
				fs: false,
				os: require.resolve('os-browserify/browser'),
			},
		},
		module: {
			...currentConfiguration.module,
			rules: [
				...currentConfiguration.module?.rules,
				{
					test: /\.node$/,
					use: 'node-loader',
				},
			],
		},
	};
});

// Add browser flags for local file access
Config.setChromiumOpenGlRenderer('egl');
Config.setChromiumDisableWebSecurity(true);
