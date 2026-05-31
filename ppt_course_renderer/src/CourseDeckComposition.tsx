import React from "react";
import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  interpolate,
  Series,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type {CourseDeckProps, CourseDeckSlideSpec} from "./courseDeckTypes";

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
    "高风险信息需核对原文";
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
        {slide.riskBadge?.label || "需核对原文"}
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
        {slide.evidencePanel?.title || "原文证据"}
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

function FullSlide({slide}: {slide: CourseDeckSlideSpec}) {
  return (
    <>
      <Img
        src={publicAsset(slide.imageRelative)}
        style={{width: "100%", height: "100%", objectFit: "contain"}}
      />
      <TitleStrip slide={slide} />
    </>
  );
}

function RuleCard({slide}: {slide: CourseDeckSlideSpec}) {
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
          <div style={{color: palette.warn, fontSize: 20, fontWeight: 800}}>
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

function SplitPanel({slide, activeShot}: {slide: CourseDeckSlideSpec; activeShot: string}) {
  return (
    <div style={{display: "grid", gridTemplateColumns: "1.08fr 0.92fr", height: "100%"}}>
      <div style={{position: "relative", background: "#0b1020"}}>
        <Img
          src={publicAsset(activeShot)}
          style={{width: "100%", height: "100%", objectFit: "contain"}}
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

function CaseDialogue({slide}: {slide: CourseDeckSlideSpec}) {
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
          <div style={{color: palette.blue, fontSize: 20, fontWeight: 800}}>CASE</div>
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
              <span style={{color: idx === 0 ? palette.warn : palette.accent, fontWeight: 850, marginRight: 12}}>
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

function SummaryLayout({slide}: {slide: CourseDeckSlideSpec}) {
  return (
    <>
      <Img
        src={publicAsset(slide.imageRelative)}
        style={{width: "100%", height: "100%", objectFit: "cover", opacity: 0.26}}
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
}: {
  slide: CourseDeckSlideSpec;
  activeShot: string;
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
        background:
          "radial-gradient(circle at 18% 12%, rgba(94, 234, 212, 0.18), transparent 30%), #070b14",
        opacity,
        transform: `translateY(${y}px)`,
      }}
    >
      {layout === "rule_card" ? (
        <RuleCard slide={slide} />
      ) : layout === "split_panel" ? (
        <SplitPanel slide={slide} activeShot={activeShot} />
      ) : layout === "case_dialogue" ? (
        <CaseDialogue slide={slide} />
      ) : layout === "summary" ? (
        <SummaryLayout slide={slide} />
      ) : (
        <FullSlide slide={slide} />
      )}
      <RiskBadge slide={slide} />
      <SubtitleTrack slide={slide} />
      <ProgressRail slide={slide} />
    </AbsoluteFill>
  );
}

export const CourseDeckComposition: React.FC<CourseDeckProps> = ({
  slides,
}) => {
  return (
    <AbsoluteFill style={{backgroundColor: "#000"}}>
      <Series>
        {slides.map((slide, i) => {
          const shots = slideShotRelatives(slide);
          const segmentFrames = splitFrames(slide.durationInFrames, shots.length);

          return (
            <Series.Sequence
              key={`slide-${slide.imageRelative}-${i}`}
              durationInFrames={slide.durationInFrames}
            >
              <AbsoluteFill>
                <Series>
                  {shots.map((rel, j) => (
                    <Series.Sequence
                      key={`${rel}-${j}`}
                      durationInFrames={segmentFrames[j] ?? 1}
                    >
                      <AbsoluteFill>
                        <SceneFrame slide={slide} activeShot={rel} />
                      </AbsoluteFill>
                    </Series.Sequence>
                  ))}
                </Series>
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
                        <Audio src={publicAsset(rel)} />
                      </Series.Sequence>
                    ))}
                  </Series>
                ) : slide.audioRelative ? (
                  <Audio src={publicAsset(slide.audioRelative)} />
                ) : null}
              </AbsoluteFill>
            </Series.Sequence>
          );
        })}
      </Series>
    </AbsoluteFill>
  );
};
