import "./index.css";
import {Composition} from "remotion";
import myVideoTest1Props from "../render_tasks/my-video-test1/input-props.json";
import {CourseDeckComposition} from "./CourseDeckComposition";
import type {CourseDeckProps} from "./courseDeckTypes";
import {MyComposition} from "./Composition";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="MyComp"
        component={MyComposition}
        durationInFrames={60}
        fps={30}
        width={1280}
        height={720}
      />
      <Composition
        id="MyVideoTest1"
        component={CourseDeckComposition}
        calculateMetadata={async ({props}) => {
          const p = props as CourseDeckProps;
          const fps = p.fps ?? 30;
          const durationInFrames = p.slides.reduce(
            (acc, s) => acc + s.durationInFrames,
            0,
          );
          return {
            fps,
            durationInFrames,
            width: 1920,
            height: 1080,
          };
        }}
        defaultProps={
          myVideoTest1Props as unknown as CourseDeckProps
        }
      />
    </>
  );
};
