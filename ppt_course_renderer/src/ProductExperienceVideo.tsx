import React from "react";
import {Audio} from "@remotion/media";
import {AbsoluteFill, Series, staticFile} from "remotion";
import {VisualScene} from "./VisualScene";
import type {VisualProjectProps} from "./visualProjectTypes";

function publicAsset(relativePath?: string): string {
  return staticFile((relativePath || "").replace(/^\/+/, ""));
}

export const ProductExperienceVideo: React.FC<VisualProjectProps> = ({scenes, audio}) => {
  return (
    <AbsoluteFill style={{background: "#10151f"}}>
      {audio?.relative ? <Audio src={publicAsset(audio.relative)} /> : null}
      <Series>
        {scenes.map((scene, idx) => (
          <Series.Sequence
            key={scene.id || `scene-${idx}`}
            durationInFrames={Math.max(1, scene.durationInFrames)}
          >
            <VisualScene scene={scene} />
            {!audio?.relative && scene.audio?.relative ? <Audio src={publicAsset(scene.audio.relative)} /> : null}
          </Series.Sequence>
        ))}
      </Series>
    </AbsoluteFill>
  );
};
