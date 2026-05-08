export type CourseDeckSlideSpec = {
  /** 整页预览：相对仓库根，如 `.../previews/slide-0000/full.png` */
  imageRelative: string;
  /**
   * 可选：该页从 PPT 抽出的内嵌图切图（`previews/slide-NNNN/shapes/shape-XXXX.png`）。
   * 若存在，该页总时长 `durationInFrames` 会在「整页 + 各 shape」之间均分，依次播放（便于口播强调局部）。
   */
  shapeRelatives?: string[];
  /** 该页总帧数（含整页与各 shape 片段之和） */
  durationInFrames: number;
  /** 可选：相对仓库根的 mp3，覆盖整页时长（单文件；与 audioRelatives 二选一） */
  audioRelative?: string | null;
  /**
   * 可选：同一页多段口播 mp3（按顺序播放）；需配合 audioSegmentDurationInFrames，
   * 且各段帧数之和应等于 durationInFrames。
   */
  audioRelatives?: string[];
  /** 与 audioRelatives 等长：每段口播在成片中的帧数 */
  audioSegmentDurationInFrames?: number[];
};

export type CourseDeckProps = {
  fps: number;
  workspaceRoot?: string;
  slides: CourseDeckSlideSpec[];
};
