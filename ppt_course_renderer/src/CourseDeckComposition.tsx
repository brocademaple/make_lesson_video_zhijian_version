import React from "react";
import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  interpolate,
  OffthreadVideo,
  Sequence,
  Series,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type {CourseDeckProps, CourseDeckSlideSpec, RenderProfile} from "./courseDeckTypes";

/** `input-props` 路径相对仓库根；`public/ppt_course_data` 指向该目录时与 `staticFile` 一致。 */
function publicAsset(relativePath: string): string {
  return staticFile(relativePath.replace(/^\/+/, ""));
}

/** 将总帧数均分为 parts 份，余数摊到前几段，避免丢帧。 */
function splitFrames(total: number, parts: number): number[] {
  if (parts <= 0) {
    return [];
  }
  const base = Math.floor(total / parts);
  const rem = total - base * parts;
  const arr: number[] = [];
  for (let i = 0; i < parts; i++) {
    arr.push(base + (i < rem ? 1 : 0));
  }
  return arr;
}

function slideShotRelatives(slide: CourseDeckSlideSpec): string[] {
  const layout = slide.layout ?? "full_slide";
  const shapes =
    layout === "split_panel" || layout === "case_dialogue"
      ? (slide.shapeRelatives ?? [])
      : [];
  if (shapes.length === 0 || layout === "rule_card" || layout === "summary") {
    return [slide.imageRelative];
  }
  return [slide.imageRelative, ...shapes];
}

function fadeIn(frame: number, offset = 0): number {
  return interpolate(frame, [offset, offset + 18], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
}

function cleanText(value: string | null | undefined, limit = 150): string {
  const text = (value ?? "").replace(/\s+/g, " ").trim();
  if (text.length <= limit) {
    return text;
  }
  return `${text.slice(0, Math.max(0, limit - 1)).trim()}…`;
}

const palette = {
  bg: "#070b14",
  panel: "rgba(12, 20, 36, 0.82)",
  panelStrong: "rgba(8, 13, 24, 0.92)",
  line: "rgba(148, 163, 184, 0.26)",
  text: "#f8fafc",
  muted: "#a8b3c7",
  accent: "#5eead4",
  blue: "#60a5fa",
  warn: "#fbbf24",
  danger: "#fb7185",
};

function profileId(profile?: RenderProfile): string {
  return profile?.id || profile?.remotion?.theme || "knowledge";
}

function profileAccent(profile?: RenderProfile): string {
  switch (profileId(profile)) {
    case "onboarding":
      return "#8b5cf6";
    case "sop":
      return "#22c55e";
    case "sales":
      return "#f59e0b";
    default:
      return palette.accent;
  }
}

function profileBackground(profile?: RenderProfile): string {
  const accent = profileAccent(profile);
  return `radial-gradient(circle at 18% 12%, ${accent}28, transparent 30%), radial-gradient(circle at 80% 18%, ${palette.blue}1f, transparent 26%), #070b14`;
}

function shotMotionStyle(frame: number, profile?: RenderProfile): React.CSSProperties {
  const motion = profile?.motion_style || profile?.remotion?.shot_motion || "slow_push";
  const ease = Easing.bezier(0.16, 1, 0.3, 1);
  const t = interpolate(frame, [0, 90], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: ease,
  });
  if (motion === "process_slide" || motion === "horizontal_track") {
    return {transform: `translateX(${interpolate(t, [0, 1], [18, -10])}px) scale(1.018)`};
  }
  if (motion === "spotlight" || motion === "spotlight_reveal") {
    return {
      transform: `scale(${interpolate(t, [0, 1], [1.035, 1])})`,
      filter: "saturate(1.06) contrast(1.04)",
    };
  }
  if (motion === "guided_steps" || motion === "gentle_pan") {
    return {transform: `translateY(${interpolate(t, [0, 1], [10, -4])}px) scale(1.012)`};
  }
  return {transform: `scale(${interpolate(t, [0, 1], [1, 1.035])})`};
}

const glass = {
  background: palette.panel,
  border: `1px solid ${palette.line}`,
  boxShadow: "0 22px 80px rgba(0, 0, 0, 0.35)",
};

function ProgressRail({slide}: {slide: CourseDeckSlideSpec}) {
  const total = Math.max(1, slide.progress?.total ?? 1);
  const index = Math.min(total, Math.max(1, slide.progress?.index ?? 1));
  return (
    <div
      style={{
        position: "absolute",
        left: 56,
        right: 56,
        bottom: 34,
        height: 4,
        borderRadius: 999,
        background: "rgba(148, 163, 184, 0.18)",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          width: `${(index / total) * 100}%`,
          height: "100%",
          borderRadius: 999,
          background: `linear-gradient(90deg, ${palette.accent}, ${palette.blue})`,
        }}
      />
    </div>
  );
}

function RiskBadge({slide}: {slide: CourseDeckSlideSpec}) {
  if (!slide.riskBadge?.show && (!slide.riskFlags || slide.riskFlags.length === 0)) {
    return null;
  }
  const first = slide.riskBadge?.items?.[0];
  const text =
    first?.quote ||
    (slide.riskFlags ?? []).slice(0, 2).join(" / ") ||
    "这里需要重点关注";
  return (
    <div
      style={{
        position: "absolute",
        top: 42,
        right: 52,
        maxWidth: 520,
        padding: "14px 18px",
        borderRadius: 14,
        background: "rgba(64, 24, 36, 0.88)",
        border: "1px solid rgba(251, 113, 133, 0.42)",
        color: palette.text,
        fontFamily: "Inter, PingFang SC, sans-serif",
        fontSize: 22,
        lineHeight: 1.35,
      }}
    >
      <strong style={{color: palette.danger, marginRight: 10}}>
        {slide.riskBadge?.label || "重点提示"}
      </strong>
      {cleanText(text, 82)}
    </div>
  );
}

function EvidencePanel({slide}: {slide: CourseDeckSlideSpec}) {
  const quotes = slide.evidencePanel?.quotes ?? [];
  if (quotes.length === 0) {
    return null;
  }
  return (
    <div
      style={{
        ...glass,
        borderRadius: 18,
        padding: "22px 24px",
        color: palette.text,
        fontFamily: "Inter, PingFang SC, sans-serif",
      }}
    >
      <div
        style={{
          color: palette.accent,
          fontSize: 20,
          fontWeight: 700,
          marginBottom: 12,
        }}
      >
        {slide.evidencePanel?.title || "素材依据"}
      </div>
      {quotes.slice(0, 2).map((item, idx) => (
        <div
          key={`${item.slide_id ?? "quote"}-${idx}`}
          style={{
            color: palette.muted,
            fontSize: 21,
            lineHeight: 1.45,
            marginTop: idx === 0 ? 0 : 10,
          }}
        >
          {cleanText(item.quote, 95)}
        </div>
      ))}
    </div>
  );
}

function CalloutStack({slide}: {slide: CourseDeckSlideSpec}) {
  const callouts = (slide.callouts ?? []).slice(0, 4);
  if (callouts.length === 0) {
    return null;
  }
  return (
    <div style={{display: "grid", gap: 12}}>
      {callouts.map((callout, idx) => (
        <div
          key={`${callout.label}-${idx}`}
          style={{
            ...glass,
            borderRadius: 16,
            padding: "16px 18px",
            color: palette.text,
            fontFamily: "Inter, PingFang SC, sans-serif",
            fontSize: 25,
            lineHeight: 1.35,
          }}
        >
          <span
            style={{
              color: callout.kind === "emphasis" ? palette.accent : palette.blue,
              fontWeight: 800,
              marginRight: 10,
            }}
          >
            {String(idx + 1).padStart(2, "0")}
          </span>
          {cleanText(callout.label, 72)}
        </div>
      ))}
    </div>
  );
}

function SubtitleTrack({slide}: {slide: CourseDeckSlideSpec}) {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const segments = slide.subtitleSegments ?? [];
  if (segments.length === 0) {
    return null;
  }
  const sec = frame / fps;
  const active =
    segments.find((seg) => {
      const start = typeof seg.start_sec === "number" ? seg.start_sec : 0;
      const end =
        typeof seg.end_sec === "number" && seg.end_sec > start
          ? seg.end_sec
          : start + 4;
      return sec >= start && sec <= end;
    }) ?? segments[Math.min(segments.length - 1, Math.floor((frame / Math.max(1, fps * 4)) % segments.length))];

  return (
    <div
      style={{
        position: "absolute",
        left: 120,
        right: 120,
        bottom: 58,
        minHeight: 58,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "13px 30px",
        borderRadius: 18,
        background: "rgba(5, 10, 20, 0.82)",
        border: "1px solid rgba(148, 163, 184, 0.22)",
        color: palette.text,
        fontFamily: "Inter, PingFang SC, sans-serif",
        fontSize: 28,
        lineHeight: 1.35,
        textAlign: "center",
      }}
    >
      {cleanText(active.text, 96)}
    </div>
  );
}

function ProfileCue({profile}: {profile?: RenderProfile}) {
  const label = profile?.label || "视频项目";
  const accent = profileAccent(profile);
  return (
    <div
      style={{
        position: "absolute",
        left: 52,
        bottom: 52,
        padding: "8px 14px",
        borderRadius: 999,
        border: `1px solid ${accent}66`,
        background: "rgba(5, 10, 20, 0.72)",
        color: accent,
        fontFamily: "Inter, PingFang SC, sans-serif",
        fontSize: 18,
        fontWeight: 800,
      }}
    >
      {cleanText(label, 16)}
    </div>
  );
}

function TitleStrip({slide}: {slide: CourseDeckSlideSpec}) {
  const title = slide.caption?.title || slide.transition?.label || "课程镜头";
  const subtitle = slide.caption?.subtitle || slide.onscreenText || "";
  return (
    <div
      style={{
        position: "absolute",
        left: 52,
        top: 42,
        maxWidth: 760,
        color: palette.text,
        fontFamily: "Inter, PingFang SC, sans-serif",
      }}
    >
      <div
        style={{
          fontSize: 34,
          fontWeight: 800,
          lineHeight: 1.18,
          textShadow: "0 8px 32px rgba(0, 0, 0, 0.42)",
        }}
      >
        {cleanText(title, 34)}
      </div>
      {subtitle ? (
        <div
          style={{
            marginTop: 10,
            color: palette.muted,
            fontSize: 21,
            lineHeight: 1.35,
            maxWidth: 680,
          }}
        >
          {cleanText(subtitle, 92)}
        </div>
      ) : null}
    </div>
  );
}

function FullSlide({slide, profile}: {slide: CourseDeckSlideSpec; profile?: RenderProfile}) {
  const frame = useCurrentFrame();
  return (
    <>
      <Img
        src={publicAsset(slide.imageRelative)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "contain",
          ...shotMotionStyle(frame, profile),
        }}
      />
      <Sequence from={8} durationInFrames={Math.max(1, slide.durationInFrames - 8)} layout="none">
        <TitleStrip slide={slide} />
      </Sequence>
    </>
  );
}

function RuleCard({slide, profile}: {slide: CourseDeckSlideSpec; profile?: RenderProfile}) {
  const frame = useCurrentFrame();
  const accent = profileAccent(profile);
  const scanX = interpolate(frame, [0, 75], [-18, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.45, 0, 0.55, 1),
  });
  return (
    <>
      <Img
        src={publicAsset(slide.imageRelative)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "contain",
          opacity: 0.64,
          filter: "saturate(0.82) contrast(0.9)",
          ...shotMotionStyle(frame, profile),
        }}
      />
      <div
        style={{
          position: "absolute",
          top: 0,
          bottom: 0,
          left: `${scanX}%`,
          width: 4,
          background: `linear-gradient(180deg, transparent, ${accent}, transparent)`,
          boxShadow: `0 0 32px ${accent}`,
          opacity: 0.42,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 70,
          top: 120,
          width: 560,
          display: "grid",
          gap: 16,
        }}
      >
        <div
          style={{
            ...glass,
            borderRadius: 20,
            padding: "28px 30px",
            color: palette.text,
            fontFamily: "Inter, PingFang SC, sans-serif",
          }}
        >
          <div style={{color: accent, fontSize: 20, fontWeight: 800}}>
            RULE CHECK
          </div>
          <div style={{fontSize: 42, lineHeight: 1.14, fontWeight: 850, marginTop: 10}}>
            {cleanText(slide.caption?.title || "规则口径", 30)}
          </div>
          <div style={{fontSize: 25, lineHeight: 1.45, color: palette.muted, marginTop: 18}}>
            {cleanText(slide.onscreenText || slide.caption?.subtitle, 120)}
          </div>
        </div>
        <EvidencePanel slide={slide} />
      </div>
    </>
  );
}

function SplitPanel({slide, activeShot, profile}: {slide: CourseDeckSlideSpec; activeShot: string; profile?: RenderProfile}) {
  const frame = useCurrentFrame();
  return (
    <div style={{display: "grid", gridTemplateColumns: "1.08fr 0.92fr", height: "100%"}}>
      <div style={{position: "relative", background: "#0b1020"}}>
        <Img
          src={publicAsset(activeShot)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "contain",
            ...shotMotionStyle(frame, profile),
          }}
        />
      </div>
      <div
        style={{
          padding: "98px 64px 110px",
          display: "grid",
          alignContent: "center",
          gap: 18,
          background:
            "linear-gradient(135deg, rgba(7, 11, 20, 0.96), rgba(17, 28, 50, 0.92))",
        }}
      >
        <div
          style={{
            color: palette.text,
            fontFamily: "Inter, PingFang SC, sans-serif",
            fontSize: 42,
            lineHeight: 1.15,
            fontWeight: 850,
          }}
        >
          {cleanText(slide.caption?.title || "镜头重点", 34)}
        </div>
        <CalloutStack slide={slide} />
        <EvidencePanel slide={slide} />
      </div>
    </div>
  );
}

function CaseDialogue({slide, profile}: {slide: CourseDeckSlideSpec; profile?: RenderProfile}) {
  const frame = useCurrentFrame();
  const accent = profileAccent(profile);
  const callouts = slide.callouts ?? [];
  return (
    <>
      <Img
        src={publicAsset(slide.imageRelative)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "contain",
          opacity: 0.42,
          filter: "blur(1px) saturate(0.75)",
          ...shotMotionStyle(frame, profile),
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 130,
          right: 130,
          top: 126,
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 22,
          fontFamily: "Inter, PingFang SC, sans-serif",
        }}
      >
        <div style={{...glass, borderRadius: 22, padding: "30px 32px"}}>
          <div style={{color: accent, fontSize: 20, fontWeight: 800}}>CASE</div>
          <div style={{color: palette.text, fontSize: 38, lineHeight: 1.18, fontWeight: 850, marginTop: 12}}>
            {cleanText(slide.caption?.title || "案例情境", 34)}
          </div>
          <div style={{color: palette.muted, fontSize: 25, lineHeight: 1.45, marginTop: 18}}>
            {cleanText(slide.onscreenText || slide.caption?.subtitle, 130)}
          </div>
        </div>
        <div style={{display: "grid", gap: 16}}>
          {(callouts.length ? callouts : [{label: "判断问题", kind: "key_point"}]).slice(0, 3).map((item, idx) => (
            <div
              key={`${item.label}-${idx}`}
              style={{
                ...glass,
                borderRadius: 20,
                padding: "22px 24px",
                color: palette.text,
                fontSize: 28,
                lineHeight: 1.32,
              }}
            >
              <span style={{color: idx === 0 ? palette.warn : accent, fontWeight: 850, marginRight: 12}}>
                {idx === 0 ? "问题" : idx === 1 ? "判断" : "解释"}
              </span>
              {cleanText(item.label, 52)}
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

function SummaryLayout({slide, profile}: {slide: CourseDeckSlideSpec; profile?: RenderProfile}) {
  const frame = useCurrentFrame();
  return (
    <>
      <Img
        src={publicAsset(slide.imageRelative)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          opacity: 0.26,
          ...shotMotionStyle(frame, profile),
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: "110px 120px 130px",
          display: "grid",
          gridTemplateRows: "auto 1fr",
          gap: 28,
          fontFamily: "Inter, PingFang SC, sans-serif",
        }}
      >
        <div style={{color: palette.text, fontSize: 54, fontWeight: 880, lineHeight: 1.12}}>
          {cleanText(slide.caption?.title || "本节复盘", 30)}
        </div>
        <div style={{display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 20}}>
          {(slide.callouts ?? []).slice(0, 4).map((callout, idx) => (
            <div
              key={`${callout.label}-${idx}`}
              style={{
                ...glass,
                borderRadius: 22,
                padding: "26px 28px",
                color: palette.text,
                fontSize: 30,
                lineHeight: 1.32,
                display: "flex",
                alignItems: "center",
              }}
            >
              <span style={{color: palette.accent, fontWeight: 900, marginRight: 14}}>
                {idx + 1}
              </span>
              {cleanText(callout.label, 48)}
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

function SceneFrame({
  slide,
  activeShot,
  profile,
}: {
  slide: CourseDeckSlideSpec;
  activeShot: string;
  profile?: RenderProfile;
}) {
  const frame = useCurrentFrame();
  const opacity = fadeIn(frame);
  const y = interpolate(frame, [0, 22], [14, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const layout = slide.layout ?? "full_slide";

  return (
    <AbsoluteFill
      style={{
        background: profileBackground(profile),
        opacity,
        transform: `translateY(${y}px)`,
      }}
    >
      {layout === "rule_card" ? (
        <RuleCard slide={slide} profile={profile} />
      ) : layout === "split_panel" ? (
        <SplitPanel slide={slide} activeShot={activeShot} profile={profile} />
      ) : layout === "case_dialogue" ? (
        <CaseDialogue slide={slide} profile={profile} />
      ) : layout === "summary" ? (
        <SummaryLayout slide={slide} profile={profile} />
      ) : (
        <FullSlide slide={slide} profile={profile} />
      )}
      <Sequence from={10} durationInFrames={Math.max(1, slide.durationInFrames - 10)} layout="none">
        <RiskBadge slide={slide} />
      </Sequence>
      <Sequence from={14} durationInFrames={Math.max(1, slide.durationInFrames - 14)} layout="none">
        <SubtitleTrack slide={slide} />
      </Sequence>
      <ProfileCue profile={profile} />
      <ProgressRail slide={slide} />
    </AbsoluteFill>
  );
}

function CreativeClip({
  slide,
  overlay = false,
}: {
  slide: CourseDeckSlideSpec;
  overlay?: boolean;
}) {
  const frame = useCurrentFrame();
  const rel = slide.creativeAsset?.clipRelative;
  if (!rel || !slide.creativeAsset?.exists) {
    return null;
  }
  const opacity = overlay ? interpolate(frame, [0, 18], [0, 0.42], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  }) : fadeIn(frame);
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#050814",
        opacity,
        mixBlendMode: overlay ? "screen" : "normal",
      }}
    >
      <OffthreadVideo
        src={publicAsset(rel)}
        muted
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
        }}
      />
    </AbsoluteFill>
  );
}

function StableSceneSeries({
  slide,
  profile,
}: {
  slide: CourseDeckSlideSpec;
  profile?: RenderProfile;
}) {
  const shots = slideShotRelatives(slide);
  const segmentFrames = splitFrames(slide.durationInFrames, shots.length);
  return (
    <Series>
      {shots.map((rel, j) => (
        <Series.Sequence
          key={`${rel}-${j}`}
          durationInFrames={segmentFrames[j] ?? 1}
        >
          <AbsoluteFill>
            <SceneFrame
              slide={slide}
              activeShot={rel}
              profile={profile}
            />
          </AbsoluteFill>
        </Series.Sequence>
      ))}
    </Series>
  );
}

export const CourseDeckComposition: React.FC<CourseDeckProps> = ({
  slides,
  videoProfile,
}) => {
  return (
    <AbsoluteFill style={{backgroundColor: "#000"}}>
      <Series>
        {slides.map((slide, i) => {
          const profile = slide.renderProfile || videoProfile;
          const canUseCreative = Boolean(slide.creativeAsset?.exists && slide.creativeAsset?.clipRelative);
          const renderEngine = slide.renderEngine || "remotion_stable";
          const replaceWithCreative = renderEngine === "hyperframes_creative" && canUseCreative;
          const overlayCreative = renderEngine === "hybrid" && canUseCreative;

          return (
            <Series.Sequence
              key={`slide-${slide.imageRelative}-${i}`}
              durationInFrames={slide.durationInFrames}
            >
              <AbsoluteFill>
                {replaceWithCreative ? (
                  <>
                    <CreativeClip slide={slide} />
                    <Sequence from={14} durationInFrames={Math.max(1, slide.durationInFrames - 14)} layout="none">
                      <SubtitleTrack slide={slide} />
                    </Sequence>
                    <ProfileCue profile={profile} />
                    <ProgressRail slide={slide} />
                  </>
                ) : (
                  <>
                    <StableSceneSeries slide={slide} profile={profile} />
                    {overlayCreative ? <CreativeClip slide={slide} overlay /> : null}
                  </>
                )}
                {slide.audioRelatives && slide.audioRelatives.length > 0 ? (
                  <Series>
                    {slide.audioRelatives.map((rel, idx) => (
                      <Series.Sequence
                        key={`audio-${rel}-${idx}`}
                        durationInFrames={
                          slide.audioSegmentDurationInFrames?.[idx] ??
                          slide.durationInFrames
                        }
                      >
                        <Audio
                          src={publicAsset(rel)}
                          volume={(f) =>
                            interpolate(f, [0, 8], [0, 1], {
                              extrapolateLeft: "clamp",
                              extrapolateRight: "clamp",
                            })
                          }
                        />
                      </Series.Sequence>
                    ))}
                  </Series>
                ) : slide.audioRelative ? (
                  <Audio
                    src={publicAsset(slide.audioRelative)}
                    volume={(f) =>
                      interpolate(f, [0, 8], [0, 1], {
                        extrapolateLeft: "clamp",
                        extrapolateRight: "clamp",
                      })
                    }
                  />
                ) : null}
              </AbsoluteFill>
            </Series.Sequence>
          );
        })}
      </Series>
    </AbsoluteFill>
  );
};
