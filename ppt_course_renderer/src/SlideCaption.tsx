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
};

/**
 * 底部渐变条 + 标题 / 副标题；每页开头若干帧淡入（Remotion：用 interpolate，禁用 CSS animation）。
 */
export const SlideCaption: React.FC<SlideCaptionProps> = ({
  slides,
  slideIndex,
  title,
  subtitle,
}) => {
  const frame = useCurrentFrame();
  const local = frame - slideStartFrame(slides, slideIndex);
  const barOpacity = interpolate(local, [0, 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const sub = subtitle?.trim();
  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        justifyContent: "flex-end",
        paddingBottom: 56,
        paddingLeft: 72,
        paddingRight: 72,
      }}
    >
      <div
        style={{
          opacity: barOpacity,
          maxWidth: "92%",
          alignSelf: "center",
          background:
            "linear-gradient(to top, rgba(0,0,0,0.82) 0%, rgba(0,0,0,0.45) 55%, transparent 100%)",
          borderRadius: 12,
          padding: "20px 28px 24px",
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
    </AbsoluteFill>
  );
};
