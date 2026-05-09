import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  Series,
  staticFile,
  useVideoConfig,
} from "remotion";
import type {CourseDeckProps, CourseDeckSlideSpec} from "./courseDeckTypes";
import {SlideCaption} from "./SlideCaption";

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
  const shapes = slide.shapeRelatives ?? [];
  if (shapes.length === 0) {
    return [slide.imageRelative];
  }
  return [slide.imageRelative, ...shapes];
}

export const CourseDeckComposition: React.FC<CourseDeckProps> = ({
  slides,
}) => {
  const {width, height} = useVideoConfig();

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
                        <Img
                          src={publicAsset(rel)}
                          style={{
                            width,
                            height,
                            objectFit: "contain",
                          }}
                        />
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
                {slide.caption ? (
                  <SlideCaption
                    slides={slides}
                    slideIndex={i}
                    title={slide.caption.title}
                    subtitle={slide.caption.subtitle}
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
