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
 * 默认 `public/` 只在 renderer 子目录内；把静态根设为仓库根后，`staticFile('ppt_course_data/...')`
 * 才能稳定命中磁盘文件（不必依赖 `public/ppt_course_data` 符号链接）。
 */
const workspaceRoot =
  process.env.REMOTION_WORKSPACE_ROOT &&
  process.env.REMOTION_WORKSPACE_ROOT.length > 0
    ? path.resolve(process.env.REMOTION_WORKSPACE_ROOT)
    : path.resolve(process.cwd(), "..");

Config.setPublicDir(workspaceRoot);

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.overrideWebpackConfig(enableTailwind);
Config.overrideWebpackConfig((currentConfiguration) => {
	return {
		...currentConfiguration,
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
