export type SceneCallout = {
  label: string;
  kind?: string;
};

export type SubtitleSegment = {
  start_sec?: number;
  end_sec?: number;
  text: string;
};

export type EvidencePanel = {
  title?: string;
  quotes?: Array<{
    slide_id?: string;
    quote: string;
  }>;
};

export type RiskBadge = {
  show?: boolean;
  label?: string;
  items?: Array<{
    risk_type?: string;
    quote?: string;
    numbers?: string[];
    slide_id?: string;
  }>;
};

export type SceneTransition = {
  type?: string;
  label?: string;
};

export type RenderProfile = {
  id?: string;
  label?: string;
  motion_style?: string;
  visual_strategy?: string;
  remotion?: {
    theme?: string;
    shot_motion?: string;
    overlay_density?: string;
    evidence_mode?: string;
  };
};

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
  /** 来自 director/render_plan 的镜头标识，用于调试与未来缓存。 */
  sceneId?: string;
  /** 导演模块分配的镜头角色：content / transition / intro / recap / concept_animation。 */
  sceneRole?: string;
  /** 双引擎调度结果：remotion_stable / hyperframes_creative / hybrid。 */
  renderEngine?: "remotion_stable" | "hyperframes_creative" | "hybrid" | string;
  /** 创意资产缺失或失败时使用的兜底引擎。 */
  fallbackEngine?: string;
  /** 给 Hyperframes 或 Remotion 创意模板的导演 brief。 */
  creativeBrief?: Record<string, unknown>;
  /** Hyperframes 预渲染产物；Remotion 最终 timeline 只引用该资产，不把导出权交给 Hyperframes。 */
  creativeAsset?: {
    clipRelative?: string;
    clipPath?: string;
    exists?: boolean;
    mode?: "replace" | "overlay" | string;
    assetManifestPath?: string;
    creativeBriefPath?: string;
  };
  /** 初版 scene-aware layout：full_slide / rule_card / split_panel / case_dialogue / summary。 */
  layout?: "full_slide" | "rule_card" | "split_panel" | "case_dialogue" | "summary" | string;
  /** 高风险规则、金额、处罚等标记；模板仅做轻量提示，不改变原 PPT 证据。 */
  riskFlags?: string[];
  /** 导演希望屏幕上保留的主文本，Renderer 会按 layout 做不同密度呈现。 */
  onscreenText?: string;
  /** 字幕轨，优先来自 DirectorManifest 的 subtitle.segments。 */
  subtitleSegments?: SubtitleSegment[];
  /** 重点提示条，可由导演脚本的 emphasis/source evidence 转换而来。 */
  callouts?: SceneCallout[];
  /** 简单高亮词，用于未来定位局部重点；当前模板用于文案提示。 */
  highlights?: string[];
  /** 原文证据框，企业培训场景里用于保留规则和金额来源。 */
  evidencePanel?: EvidencePanel;
  /** 风险核对条：处罚、金额、边界条件等必须可见。 */
  riskBadge?: RiskBadge;
  /** 章节/镜头转场意图。 */
  transition?: SceneTransition;
  /** 从视频意图下沉到 Remotion 的主题、镜头运动和证据层策略。 */
  renderProfile?: RenderProfile;
  /** 当前 scene 在完整视频中的位置。 */
  progress?: {
    index: number;
    total: number;
  };
  /** 保留给调试和审核用的 slide/source evidence。 */
  sourceEvidence?: Array<{
    slide_id?: string;
    quote: string;
  }>;
  sourceSlideIds?: string[];
  /**
   * 可选：底部信息条（通常来自 deal **`meta.json`** 的标题 + 摘要），用于「音画之上还有一点叙事锚点」，
   * 而非单纯轮播 PNG。
   */
  caption?: {
    title: string;
    subtitle?: string | null;
  };
};

export type CourseDeckProps = {
  schemaVersion?: string;
  fps: number;
  workspaceRoot?: string;
  videoProfile?: RenderProfile;
  timelineItems?: Array<{
    index: number;
    scene_id: string;
    scene_role?: string;
    render_engine?: string;
    fallback_engine?: string;
    start_frame: number;
    duration_frames: number;
    end_frame: number;
    layout?: string;
  }>;
  slides: CourseDeckSlideSpec[];
};
