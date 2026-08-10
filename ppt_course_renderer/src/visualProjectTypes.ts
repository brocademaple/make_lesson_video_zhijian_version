export type Rect = {
  x: number;
  y: number;
  width: number;
  height: number;
};

export type VisualMaterial = {
  id?: string;
  type?: "image" | "screenshot" | "recording" | "text" | "audio" | string;
  relative?: string;
  label?: string;
  alt?: string;
};

export type VisualEffect =
  | {
      type: "camera.zoom_to";
      rect?: Rect;
      scale?: number;
      start?: number;
      end?: number;
    }
  | {
      type: "camera.pan";
      from?: {x?: number; y?: number};
      to?: {x?: number; y?: number};
    }
  | {
      type: "focus.highlight_rect" | "focus.magnify_detail";
      rect?: Rect;
      label?: string;
    }
  | {
      type: "overlay.label" | "overlay.arrow";
      text?: string;
      x?: number;
      y?: number;
    }
  | {
      type: "layout.split_screen" | "layout.before_after" | "transition.chapter_card" | "caption.subtitle_track";
      [key: string]: unknown;
    }
  | {
      type: string;
      [key: string]: unknown;
    };

export type VisualCallout = {
  label: string;
  kind?: string;
  x?: number;
  y?: number;
};

export type VisualSubtitleSegment = {
  start_sec?: number;
  end_sec?: number;
  text: string;
};

export type VisualSceneSpec = {
  id: string;
  title: string;
  narration?: string;
  onscreenText?: string;
  shotType?: "hero" | "screen_focus" | "zoom_detail" | "step_flow" | "compare" | "takeaway" | string;
  durationInFrames: number;
  durationSec?: number;
  asset?: VisualMaterial;
  audio?: VisualMaterial;
  motion?: {
    preset?: "slow_push" | "zoom_in" | "pan_right" | "float" | string;
    scale?: number;
  };
  focusRect?: Rect | Record<string, never>;
  effects?: VisualEffect[];
  callouts?: VisualCallout[];
  subtitleSegments?: VisualSubtitleSegment[];
  creativeAssetNeeded?: boolean;
  progress?: {
    index: number;
    total: number;
  };
};

export type VisualProjectProps = {
  schemaVersion?: string;
  fps: number;
  width?: number;
  height?: number;
  format?: string;
  intent?: string;
  title: string;
  templatePackage?: string;
  style?: {
    palette?: string;
    mood?: string;
  };
  variant?: {
    id?: string;
    angle?: string;
    pace?: string;
  };
  variants?: Array<Record<string, unknown>>;
  audio?: VisualMaterial;
  scenes: VisualSceneSpec[];
};
