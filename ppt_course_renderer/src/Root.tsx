import "./index.css";
import { Composition } from "remotion";
import task2555Pages14Props from "../render_tasks/task-2555-pages1-4/input-props.json";
import productExperienceDemoProps from "../render_tasks/product-experience-demo/input-props.json";
import { CourseDeckComposition } from "./CourseDeckComposition";
import { ProductExperienceVideo } from "./ProductExperienceVideo";
import type { CourseDeckProps } from "./courseDeckTypes";
import type { VisualProjectProps } from "./visualProjectTypes";

const compositionId = "CourseDeck";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id={compositionId}
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
      <Composition
        id="ProductExperienceVideo"
        component={ProductExperienceVideo}
        calculateMetadata={async ({ props }) => {
          const p = props as VisualProjectProps;
          const fps = p.fps ?? 30;
          const durationInFrames = p.scenes.reduce(
            (acc, s) => acc + s.durationInFrames,
            0,
          );
          return {
            fps,
            durationInFrames,
            width: p.width ?? 1080,
            height: p.height ?? 1920,
          };
        }}
        defaultProps={productExperienceDemoProps as unknown as VisualProjectProps}
      />
      <Composition
        id="KnowledgeExplainer"
        component={ProductExperienceVideo}
        calculateMetadata={async ({ props }) => {
          const p = props as VisualProjectProps;
          const fps = p.fps ?? 30;
          const durationInFrames = p.scenes.reduce(
            (acc, s) => acc + s.durationInFrames,
            0,
          );
          return {
            fps,
            durationInFrames,
            width: p.width ?? 1080,
            height: p.height ?? 1920,
          };
        }}
        defaultProps={{
          ...(productExperienceDemoProps as unknown as VisualProjectProps),
          templatePackage: "KnowledgeExplainer",
          title: "AIGC 创作者工作台解释版",
        }}
      />
    </>
  );
};
