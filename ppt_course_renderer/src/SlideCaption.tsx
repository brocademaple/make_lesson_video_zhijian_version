import React from "react";
import {AbsoluteFill, interpolate, useCurrentFrame} from "remotion";
import type {CourseDeckSlideSpec} from "./courseDeckTypes";

function slideStartFrame(slides: CourseDeckSlideSpec[], slideIndex: number): number {
  let sum = 0;
  for (let i = 0; i < slideIndex; i++) {
    sum += slides[i].durationInFrames;
  }
  return sum;
}

type SlideCaptionProps = {
  slides: CourseDeckSlideSpec[];
  slideIndex: number;
  title: string;
  subtitle?: string | null;
  layout?: string;
  riskFlags?: string[];
};

function layoutLabel(layout?: string): string {
  switch (layout) {
    case "rule_card":
      return "规则要点";
    case "split_panel":
    case "case_dialogue":
      return "案例拆解";
    case "summary":
      return "小结回顾";
    default:
      return "课程讲解";
  }
}

function accentForLayout(layout?: string): string {
  switch (layout) {
    case "rule_card":
      return "#ef4444";
    case "split_panel":
    case "case_dialogue":
      return "#14b8a6";
    case "summary":
      return "#f59e0b";
    default:
      return "#3b82f6";
  }
}

/**
 * 底部渐变条 + 标题 / 副标题；每页开头若干帧淡入（Remotion：用 interpolate，禁用 CSS animation）。
 */
export const SlideCaption: React.FC<SlideCaptionProps> = ({
  slides,
  slideIndex,
  title,
  subtitle,
  layout,
  riskFlags = [],
}) => {
  const frame = useCurrentFrame();
  const local = frame - slideStartFrame(slides, slideIndex);
  const barOpacity = interpolate(local, [0, 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const sub = subtitle?.trim();
  const accent = accentForLayout(layout);
  const hasRisk = riskFlags.length > 0;
  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        justifyContent: "space-between",
        paddingTop: 42,
        paddingBottom: 56,
        paddingLeft: 72,
        paddingRight: 72,
      }}
    >
      <div
        style={{
          opacity: barOpacity,
          alignSelf: "flex-start",
          display: "flex",
          alignItems: "center",
          gap: 14,
          padding: "10px 16px",
          borderRadius: 6,
          background: "rgba(12, 18, 28, 0.72)",
          borderLeft: `6px solid ${accent}`,
          color: "#fff",
          fontFamily:
            "system-ui, -apple-system, 'Segoe UI', Roboto, 'PingFang SC', sans-serif",
          fontSize: 20,
          fontWeight: 700,
          letterSpacing: 0,
          textShadow: "0 1px 8px rgba(0,0,0,0.72)",
        }}
      >
        <span>{layoutLabel(layout)}</span>
        {hasRisk ? (
          <span
            style={{
              color: "#fde68a",
              fontSize: 18,
              fontWeight: 700,
            }}
          >
            需核对原文
          </span>
        ) : null}
      </div>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
         justifyContent: "flex-end",
          alignItems: "center",
      }}
    >
      <div
        style={{
          opacity: barOpacity,
          maxWidth: "92%",
          alignSelf: "center",
          background:
            "linear-gradient(to top, rgba(0,0,0,0.82) 0%, rgba(0,0,0,0.45) 55%, transparent 100%)",
          borderRadius: 8,
          padding: "20px 28px 24px",
          borderTop: `4px solid ${accent}`,
        }}
      >
        <div
          style={{
            color: "#fff",
            fontFamily:
              "system-ui, -apple-system, 'Segoe UI', Roboto, 'PingFang SC', sans-serif",
            fontWeight: 700,
            fontSize: 34,
            lineHeight: 1.25,
            textShadow: "0 2px 12px rgba(0,0,0,0.85)",
          }}
        >
          {title}
        </div>
        {sub ? (
          <div
            style={{
              marginTop: 10,
              color: "rgba(255,255,255,0.92)",
              fontFamily:
                "system-ui, -apple-system, 'Segoe UI', Roboto, 'PingFang SC', sans-serif",
              fontWeight: 500,
              fontSize: 22,
              lineHeight: 1.45,
              maxHeight: 140,
              overflow: "hidden",
              textShadow: "0 1px 8px rgba(0,0,0,0.8)",
            }}
          >
            {sub}
          </div>
        ) : null}
      </div>
      </div>
    </AbsoluteFill>
  );
};
