import "./index.css";
import { Composition } from "remotion";
import task2555Pages14Props from "../render_tasks/task-2555-pages1-4/input-props.json";
import { CourseDeckComposition } from "./CourseDeckComposition";
import type { CourseDeckProps } from "./courseDeckTypes";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="MyVideoTest1"
        component={CourseDeckComposition}
        calculateMetadata={async ({ props }) => {
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
        defaultProps={task2555Pages14Props as unknown as CourseDeckProps}
      />
    </>
  );
};
