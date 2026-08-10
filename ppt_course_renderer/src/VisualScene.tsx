import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  OffthreadVideo,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type {Rect, VisualEffect, VisualSceneSpec} from "./visualProjectTypes";

const theme = {
  bg: "#10151f",
  ink: "#f8fafc",
  muted: "#a7b0c0",
  line: "rgba(255,255,255,0.16)",
  panel: "rgba(10, 14, 22, 0.78)",
  accent: "#67e8f9",
  warm: "#fbbf24",
  coral: "#fb7185",
};

function publicAsset(relativePath?: string): string {
  return staticFile((relativePath || "").replace(/^\/+/, ""));
}

function cleanText(value: string | undefined, limit = 120): string {
  const text = (value || "").replace(/\s+/g, " ").trim();
  if (text.length <= limit) {
    return text;
  }
  return `${text.slice(0, Math.max(0, limit - 1)).trim()}…`;
}

function clampRect(rect?: Rect | Record<string, never>): Rect | null {
  if (!rect) {
    return null;
  }
  const r = rect as Rect;
  const values = [r.x, r.y, r.width, r.height];
  if (values.some((v) => typeof v !== "number" || Number.isNaN(v))) {
    return null;
  }
  return {
    x: Math.max(0, Math.min(100, r.x)),
    y: Math.max(0, Math.min(100, r.y)),
    width: Math.max(1, Math.min(100, r.width)),
    height: Math.max(1, Math.min(100, r.height)),
  };
}

function findEffect(effects: VisualEffect[] | undefined, type: string): VisualEffect | undefined {
  return (effects || []).find((effect) => effect.type === type);
}

function stageTransform(scene: VisualSceneSpec, frame: number): string {
  const zoomEffect = findEffect(scene.effects, "camera.zoom_to");
  const rect = clampRect((zoomEffect as {rect?: Rect} | undefined)?.rect || scene.focusRect);
  const preset = scene.motion?.preset || (scene.shotType === "zoom_detail" ? "zoom_in" : "slow_push");
  const intro = interpolate(frame, [0, 36], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const baseScale = preset === "zoom_in" ? 1.08 : preset === "float" ? 1.03 : 1.02;
  if (rect) {
    const cx = rect.x + rect.width / 2;
    const cy = rect.y + rect.height / 2;
    const targetScale = (zoomEffect as {scale?: number} | undefined)?.scale || scene.motion?.scale || 1.7;
    const scale = interpolate(intro, [0, 1], [1, targetScale]);
    const tx = interpolate(intro, [0, 1], [0, 50 - cx]);
    const ty = interpolate(intro, [0, 1], [0, 50 - cy]);
    return `translate(${tx}%, ${ty}%) scale(${scale})`;
  }
  if (preset === "pan_right") {
    const tx = interpolate(frame, [0, 120], [-1.5, 1.5], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    return `translateX(${tx}%) scale(${baseScale})`;
  }
  const scale = interpolate(intro, [0, 1], [1, baseScale]);
  return `scale(${scale})`;
}

function SceneBackground({scene}: {scene: VisualSceneSpec}) {
  const frame = useCurrentFrame();
  const rel = scene.asset?.relative;
  const hasAsset = Boolean(rel);
  return (
    <>
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle at 20% 12%, rgba(103,232,249,0.18), transparent 28%), radial-gradient(circle at 78% 18%, rgba(251,191,36,0.14), transparent 26%), #10151f",
        }}
      />
      {hasAsset ? (
        <Img
          src={publicAsset(rel)}
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            objectFit: "cover",
            opacity: 0.28,
            filter: "blur(22px) saturate(1.08)",
            transform: "scale(1.08)",
          }}
        />
      ) : null}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(180deg, rgba(16,21,31,0.1), rgba(16,21,31,0.88))",
          opacity: interpolate(frame, [0, 30], [0.6, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      />
    </>
  );
}

function CreativeLayer({scene, overlay = false}: {scene: VisualSceneSpec; overlay?: boolean}) {
  const relative = scene.creativeAsset?.relative;
  if (!relative) {
    return null;
  }
  return (
    <AbsoluteFill
      style={{
        opacity: overlay ? 0.42 : 1,
        mixBlendMode: overlay ? "screen" : "normal",
      }}
    >
      <OffthreadVideo
        src={publicAsset(relative)}
        muted
        style={{width: "100%", height: "100%", objectFit: "cover"}}
      />
    </AbsoluteFill>
  );
}

function MediaStage({scene}: {scene: VisualSceneSpec}) {
  const frame = useCurrentFrame();
  const rel = scene.asset?.relative;
  const showTakeaway = scene.shotType === "takeaway" || !rel;
  const stageWidth = showTakeaway ? "76%" : "86%";
  return (
    <div
      style={{
        position: "absolute",
        left: "7%",
        right: "7%",
        top: "15%",
        height: "58%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          position: "relative",
          width: stageWidth,
          height: "100%",
          borderRadius: 34,
          overflow: "hidden",
          border: `1px solid ${theme.line}`,
          background: showTakeaway ? "rgba(10, 14, 22, 0.58)" : "#05070b",
          boxShadow: "0 30px 110px rgba(0,0,0,0.48)",
        }}
      >
        {rel ? (
          <Img
            src={publicAsset(rel)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "contain",
              transform: stageTransform(scene, frame),
              transformOrigin: "center center",
            }}
          />
        ) : (
          <div
            style={{
              width: "100%",
              height: "100%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              padding: 56,
              color: theme.ink,
              fontFamily: "Inter, PingFang SC, sans-serif",
              fontSize: 58,
              lineHeight: 1.12,
              fontWeight: 850,
              textAlign: "center",
            }}
          >
            {cleanText(scene.onscreenText || scene.title, 56)}
          </div>
        )}
        <FocusLayer scene={scene} />
      </div>
    </div>
  );
}

function FocusLayer({scene}: {scene: VisualSceneSpec}) {
  const frame = useCurrentFrame();
  const explicit = findEffect(scene.effects, "focus.highlight_rect") as {rect?: Rect; label?: string} | undefined;
  const magnify = findEffect(scene.effects, "focus.magnify_detail") as {rect?: Rect; label?: string} | undefined;
  const rect = clampRect(explicit?.rect || magnify?.rect || scene.focusRect);
  if (!rect) {
    return null;
  }
  const opacity = interpolate(frame, [16, 32], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  return (
    <>
      <div
        style={{
          position: "absolute",
          left: `${rect.x}%`,
          top: `${rect.y}%`,
          width: `${rect.width}%`,
          height: `${rect.height}%`,
          border: `4px solid ${theme.accent}`,
          borderRadius: 18,
          opacity,
          boxShadow: "0 0 0 999px rgba(5,7,11,0.28), 0 0 34px rgba(103,232,249,0.48)",
        }}
      />
      {(explicit?.label || magnify?.label) ? (
        <div
          style={{
            position: "absolute",
            left: `${Math.min(78, rect.x)}%`,
            top: `${Math.max(2, rect.y - 8)}%`,
            padding: "10px 14px",
            borderRadius: 999,
            background: "rgba(103,232,249,0.94)",
            color: "#071018",
            fontFamily: "Inter, PingFang SC, sans-serif",
            fontSize: 22,
            fontWeight: 850,
            opacity,
          }}
        >
          {cleanText(explicit?.label || magnify?.label, 18)}
        </div>
      ) : null}
    </>
  );
}

function Header({scene}: {scene: VisualSceneSpec}) {
  return (
    <div
      style={{
        position: "absolute",
        left: 58,
        right: 58,
        top: 62,
        color: theme.ink,
        fontFamily: "Inter, PingFang SC, sans-serif",
      }}
    >
      <div
        style={{
          display: "inline-flex",
          gap: 10,
          alignItems: "center",
          padding: "8px 14px",
          borderRadius: 999,
          border: `1px solid ${theme.line}`,
          background: "rgba(10,14,22,0.62)",
          color: theme.accent,
          fontSize: 20,
          fontWeight: 800,
          marginBottom: 20,
        }}
      >
        <span>{String(scene.progress?.index || 1).padStart(2, "0")}</span>
        <span>{cleanText(scene.shotType || "visual_scene", 24)}</span>
      </div>
      <div style={{fontSize: 50, lineHeight: 1.08, fontWeight: 880}}>
        {cleanText(scene.title, 34)}
      </div>
      {scene.onscreenText ? (
        <div style={{marginTop: 14, color: theme.muted, fontSize: 27, lineHeight: 1.36}}>
          {cleanText(scene.onscreenText, 70)}
        </div>
      ) : null}
    </div>
  );
}

function Callouts({scene}: {scene: VisualSceneSpec}) {
  const frame = useCurrentFrame();
  const callouts = (scene.callouts || []).slice(0, 3);
  if (callouts.length === 0) {
    return null;
  }
  return (
    <div
      style={{
        position: "absolute",
        left: 72,
        right: 72,
        bottom: 256,
        display: "grid",
        gap: 12,
      }}
    >
      {callouts.map((item, idx) => (
        <div
          key={`${item.label}-${idx}`}
          style={{
            transform: `translateY(${interpolate(frame, [20 + idx * 8, 38 + idx * 8], [18, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.16, 1, 0.3, 1),
            })}px)`,
            opacity: interpolate(frame, [20 + idx * 8, 38 + idx * 8], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
            padding: "16px 20px",
            borderRadius: 18,
            border: `1px solid ${theme.line}`,
            background: theme.panel,
            color: theme.ink,
            fontFamily: "Inter, PingFang SC, sans-serif",
            fontSize: 25,
            lineHeight: 1.3,
          }}
        >
          <span style={{color: idx === 0 ? theme.warm : theme.accent, fontWeight: 900, marginRight: 12}}>
            {idx + 1}
          </span>
          {cleanText(item.label, 42)}
        </div>
      ))}
    </div>
  );
}

function Subtitle({scene}: {scene: VisualSceneSpec}) {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const segments = scene.subtitleSegments || [];
  if (segments.length === 0) {
    return null;
  }
  const sec = frame / fps;
  const active =
    segments.find((seg) => {
      const start = typeof seg.start_sec === "number" ? seg.start_sec : 0;
      const end = typeof seg.end_sec === "number" && seg.end_sec > start ? seg.end_sec : start + 4;
      return sec >= start && sec <= end;
    }) || segments[0];
  return (
    <div
      style={{
        position: "absolute",
        left: 58,
        right: 58,
        bottom: 74,
        minHeight: 92,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "20px 26px",
        borderRadius: 24,
        background: "rgba(5, 8, 14, 0.82)",
        border: `1px solid ${theme.line}`,
        color: theme.ink,
        fontFamily: "Inter, PingFang SC, sans-serif",
        fontSize: 30,
        lineHeight: 1.34,
        textAlign: "center",
      }}
    >
      {cleanText(active.text, 78)}
    </div>
  );
}

export const VisualScene: React.FC<{scene: VisualSceneSpec}> = ({scene}) => {
  const creativeReady = Boolean(scene.creativeAsset?.relative && scene.rendererStatus === "ready");
  const creativeReplacement = creativeReady && scene.rendererResolved === "hyperframes";
  const creativeOverlay = creativeReady && scene.rendererResolved === "hybrid";
  return (
    <AbsoluteFill style={{background: theme.bg, overflow: "hidden"}}>
      {creativeReplacement ? (
        <CreativeLayer scene={scene} />
      ) : (
        <>
          <SceneBackground scene={scene} />
          <MediaStage scene={scene} />
          {creativeOverlay ? <CreativeLayer scene={scene} overlay /> : null}
          <Header scene={scene} />
          <Callouts scene={scene} />
        </>
      )}
      <Subtitle scene={scene} />
    </AbsoluteFill>
  );
};
