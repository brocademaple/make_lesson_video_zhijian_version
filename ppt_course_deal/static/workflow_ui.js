(function () {
  "use strict";

  function createWorkflowUI(options) {
    var taskWorkflowMeter = options.taskWorkflowMeter;
    var taskWorkflowActions = options.taskWorkflowActions;
    var outputSummary = options.outputSummary;
    var taskWorkflowPipeline = options.taskWorkflowPipeline;
    var taskWorkflowArtifacts = options.taskWorkflowArtifacts;
    var taskWorkflowTitle = options.taskWorkflowTitle;
    var taskWorkflowSteps = options.taskWorkflowSteps;
    var escapeHtmlText = options.escapeHtmlText;

    function workflowStep(label, state, detail, targetId) {
      var stateClass = state === "ready" ? "ready" : state === "warn" ? "warn" : "todo";
      var stateLabel = state === "ready" ? "已就绪" : state === "warn" ? "需注意" : "待处理";
      return (
        '<button type="button" class="task-workflow-step task-workflow-step--' +
        stateClass +
        '" data-workflow-target="' +
        escapeHtmlText(targetId || "") +
        '" role="listitem">' +
        '<span class="task-workflow-step__state">' +
        stateLabel +
        "</span>" +
        '<span class="task-workflow-step__label">' +
        escapeHtmlText(label) +
        "</span>" +
        '<span class="task-workflow-step__detail">' +
        escapeHtmlText(detail || "") +
        "</span>" +
        "</button>"
      );
    }

    function workflowPipelineNode(label, state, detail) {
      var stateClass = state === "ready" ? "ready" : state === "warn" ? "warn" : "todo";
      return (
        '<span class="task-pipeline-node task-pipeline-node--' +
        stateClass +
        '">' +
        '<span class="task-pipeline-node__dot"></span>' +
        '<span class="task-pipeline-node__text">' +
        escapeHtmlText(label) +
        "</span>" +
        '<span class="task-pipeline-node__detail">' +
        escapeHtmlText(detail || "") +
        "</span>" +
        "</span>"
      );
    }

    function workflowArtifact(label, value, state) {
      var stateClass = state === "ready" ? "ready" : state === "warn" ? "warn" : "todo";
      return (
        '<div class="task-artifact task-artifact--' +
        stateClass +
        '">' +
        '<span class="task-artifact__label">' +
        escapeHtmlText(label) +
        "</span>" +
        '<code class="task-artifact__value">' +
        escapeHtmlText(value || "待生成") +
        "</code>" +
        "</div>"
      );
    }

    function renderPipelineMeter(data) {
      if (!taskWorkflowMeter) return;
      var pipeline = data && data.pipeline;
      if (!pipeline) {
        taskWorkflowMeter.innerHTML = "";
        return;
      }
      var percent = typeof pipeline.percent === "number" ? pipeline.percent : 0;
      taskWorkflowMeter.innerHTML =
        '<div class="task-meter__copy">' +
        '<span class="task-meter__label">当前链路完成度</span>' +
        '<strong>' +
        escapeHtmlText(String(percent)) +
        "%</strong>" +
        '<span class="task-meter__detail">' +
        escapeHtmlText((pipeline.ready_count || 0) + "/" + (pipeline.stage_count || 0) + " 个阶段就绪") +
        "</span>" +
        "</div>" +
        '<div class="task-meter__bar" aria-hidden="true"><span style="width:' +
        Math.max(0, Math.min(100, percent)) +
        '%"></span></div>';
    }

    function pipelineActionButton(step, label) {
      return (
        '<button type="button" class="btn btn-secondary task-workflow-action" data-pipeline-step="' +
        escapeHtmlText(step) +
        '">' +
        escapeHtmlText(label) +
        "</button>"
      );
    }

    function renderPipelineActions(data, currentTaskId) {
      if (!taskWorkflowActions) return;
      if (!currentTaskId || !data) {
        taskWorkflowActions.innerHTML = "";
        return;
      }
      var stages = (data.pipeline && data.pipeline.stages) || [];
      var byKey = {};
      stages.forEach(function (stage) {
        byKey[stage.key] = stage;
      });
      taskWorkflowActions.innerHTML =
        pipelineActionButton("raw_material", byKey.raw_material && byKey.raw_material.ready ? "重建素材底稿" : "生成素材底稿") +
        pipelineActionButton("course_material", byKey.course_material && byKey.course_material.ready ? "刷新素材地图" : "生成素材地图") +
        pipelineActionButton("director", byKey.director && byKey.director.ready ? "重排分镜脚本" : "生成分镜脚本") +
        pipelineActionButton("audio", "检查声音轨") +
        pipelineActionButton("render_plan", byKey.render_plan && byKey.render_plan.ready ? "重新生成成片蓝图" : "生成成片蓝图");
    }

    function renderOutputSummary(data, currentTaskId) {
      if (!outputSummary) return;
      var remotion = data && data.remotion;
      if (!currentTaskId || !remotion) {
        outputSummary.innerHTML =
          '<p class="output-panel__empty">打开作品项目后，这里会显示最终 MP4。</p>';
        return;
      }
      var hasVideo = Boolean(remotion.output_video_exists);
      var videoUrl =
        hasVideo && currentTaskId
          ? "/api/tasks/" + encodeURIComponent(currentTaskId) + "/output-video"
          : "";
      var renderRoute = "#/tasks/" + encodeURIComponent(currentTaskId) + "/render";
      var directorRoute = "#/tasks/" + encodeURIComponent(currentTaskId) + "/director";
      var dealRoute = "#/tasks/" + encodeURIComponent(currentTaskId) + "/deal";
      var duration = remotion.duration_sec ? remotion.duration_sec + " 秒" : "—";
      var filename = (data && data.filename) || "作品项目";
      outputSummary.innerHTML =
        '<div class="output-panel__summary-inner output-panel__summary-inner--' +
        (hasVideo ? "ready" : "todo") +
        '">' +
        '<div class="output-panel__hero">' +
        '<div><strong>' +
        escapeHtmlText(filename) +
        '</strong><p>' +
        (hasVideo ? "最终 MP4 已生成，可以直接预览和演示。" : "还没有检测到 MP4，先回到成片线生成蓝图并执行渲染。") +
        "</p></div>" +
        '<span class="output-panel__badge ' +
        (hasVideo ? "is-ready" : "is-todo") +
        '">' +
        (hasVideo ? "可播放" : "待出片") +
        "</span>" +
        "</div>" +
        (videoUrl
          ? '<video class="output-panel__video" controls preload="metadata" src="' +
            escapeHtmlText(videoUrl) +
            '"></video>'
          : '<div class="output-panel__placeholder">暂无视频文件</div>') +
        '<div class="output-panel__facts">' +
        '<span><b>' +
        escapeHtmlText(duration) +
        "</b>成片时长</span>" +
        '<span><b>' +
        escapeHtmlText(remotion.output_video_size_bytes ? Math.round(remotion.output_video_size_bytes / 1024 / 1024 * 10) / 10 + " MB" : "—") +
        "</b>文件大小</span>" +
        '<span><b>' +
        escapeHtmlText(remotion.render_plan_exists ? "已生成" : "待生成") +
        "</b>成片蓝图</span>" +
        "</div>" +
        '<p class="output-panel__links-title">关联任务</p>' +
        '<div class="output-panel__links">' +
        '<a class="btn btn-secondary" href="' +
        escapeHtmlText(hasVideo ? videoUrl : renderRoute) +
        '"' +
        (hasVideo ? ' target="_blank" rel="noopener noreferrer"' : "") +
        ">" +
        (hasVideo ? "新窗口播放" : "去成片线") +
        "</a>" +
        '<a class="btn btn-text" href="' +
        escapeHtmlText(dealRoute) +
        '">素材台</a>' +
        '<a class="btn btn-text" href="' +
        escapeHtmlText(directorRoute) +
        '">导演台</a>' +
        '<a class="btn btn-text" href="' +
        escapeHtmlText(renderRoute) +
        '">成片线</a>' +
        "</div>" +
        '<details class="output-panel__details"><summary>高级：文件路径与渲染命令</summary>' +
        "<p><strong>视频路径</strong>：" +
        escapeHtmlText(remotion.output_video_path || "—") +
        "</p>" +
        "<p><strong>成片蓝图</strong>：" +
        escapeHtmlText(remotion.render_plan_exists ? remotion.render_plan_path || "已生成" : "待生成") +
        "</p>" +
        '<pre class="output-panel__command">' +
        escapeHtmlText(remotion.render_command || "先生成成片蓝图 / input-props") +
        "</pre></details>" +
        "</div>";
    }

    function renderPipelineState(data, currentTaskId) {
      renderPipelineMeter(data);
      renderPipelineActions(data, currentTaskId);
      renderOutputSummary(data, currentTaskId);
    }

    function renderWorkflowDetails(data, states, currentTaskId) {
      if (taskWorkflowPipeline) {
        if (!currentTaskId || !data) {
          taskWorkflowPipeline.innerHTML = "";
        } else {
          var deal = data.deal || {};
          var audio = data.audio || {};
          var rebuilder = data.rebuilder || {};
          var remotion = data.remotion || {};
          taskWorkflowPipeline.innerHTML =
            workflowPipelineNode(
              "PPT",
              "ready",
              data.slide_count ? data.slide_count + " 页" : "已载入"
            ) +
            workflowPipelineNode(
              "预览切图",
              states.dealState,
              (deal.preview_count || 0) + "/" + (data.slide_count || 0) + " 预览"
            ) +
            workflowPipelineNode(
              "素材地图",
              rebuilder.course_material_exists ? "ready" : rebuilder.raw_manifest_exists ? "warn" : "todo",
              rebuilder.course_material_exists
                ? (rebuilder.course_material_slide_count || 0) + " 页素材"
                : "待规范化"
            ) +
            workflowPipelineNode(
              "分镜脚本",
              states.directorState,
              rebuilder.director_manifest_exists
                ? (rebuilder.scene_count || 0) + " 镜头"
                : "待导演规划"
            ) +
            workflowPipelineNode(
              "成片蓝图",
              remotion.render_plan_exists || remotion.input_props_exists ? "ready" : "todo",
              remotion.render_plan_source || "待生成"
            ) +
            workflowPipelineNode(
              "MP4",
              states.remotionState,
              remotion.output_video_exists ? "已生成" : "待渲染"
            );
          if (!audio.slides_with_audio) {
            taskWorkflowPipeline.innerHTML += workflowPipelineNode(
              "声音轨",
              "warn",
              "暂无口播音频，可用 edge-tts 兜底"
            );
          }
        }
      }
      if (taskWorkflowArtifacts) {
        if (!currentTaskId || !data) {
          taskWorkflowArtifacts.innerHTML = "";
        } else {
          var taskRoot = "ppt_course_data/tasks/" + currentTaskId;
          var r = data.remotion || {};
          taskWorkflowArtifacts.innerHTML =
            workflowArtifact("素材底稿", taskRoot + "/raw_material_manifest.json", data.rebuilder && data.rebuilder.raw_manifest_exists ? "ready" : "todo") +
            workflowArtifact("素材地图", taskRoot + "/course_material.json", data.rebuilder && data.rebuilder.course_material_exists ? "ready" : "todo") +
            workflowArtifact("分镜脚本", taskRoot + "/director_manifest.json", data.rebuilder && data.rebuilder.director_manifest_exists ? "ready" : "todo") +
            workflowArtifact("成片蓝图", r.render_plan_path || "", r.render_plan_exists ? "ready" : "todo") +
            workflowArtifact("Input Props", r.input_props_path || "", r.input_props_exists ? "ready" : "todo") +
            workflowArtifact("Output MP4", r.output_video_path || "", r.output_video_exists ? "ready" : "todo");
        }
      }
    }

    function renderWorkspaceStatus(data, currentTaskId) {
      renderPipelineState(data, currentTaskId);
      if (taskWorkflowTitle) {
        taskWorkflowTitle.textContent =
          data && data.filename ? data.filename : currentTaskId ? "作品项目" : "项目工作流";
      }
      if (!taskWorkflowSteps) return;
      if (!currentTaskId || !data) {
        taskWorkflowSteps.innerHTML =
          '<p class="task-workflow__empty">打开作品项目后显示入仓、拆解、导演、声音轨与成片状态。</p>';
        renderWorkflowDetails(data, {}, currentTaskId);
        return;
      }
      var deal = data.deal || {};
      var audio = data.audio || {};
      var rebuilder = data.rebuilder || {};
      var remotion = data.remotion || {};
      var dealState = deal.images_available ? "ready" : "warn";
      var directorState = rebuilder.director_manifest_exists
        ? "ready"
        : rebuilder.course_material_exists || rebuilder.raw_manifest_exists
          ? "warn"
          : "todo";
      var audioState = audio.slides_with_audio > 0 ? "ready" : "todo";
      var remotionState = remotion.output_video_exists
        ? "ready"
        : remotion.input_props_exists
          ? "warn"
          : "todo";
      taskWorkflowSteps.innerHTML =
        workflowStep(
          "素材入仓",
          dealState,
          (data.slide_count || 0) + " 页，预览 " + (deal.preview_count || 0) + " 页",
          "preview-surface",
        ) +
        workflowStep(
          "导演台",
          directorState,
          rebuilder.director_manifest_exists
            ? (rebuilder.scene_count || 0) + " 镜头 · " + (rebuilder.planning_mode || "unknown")
            : rebuilder.course_material_exists
              ? "已有素材地图，待生成分镜脚本"
              : rebuilder.raw_manifest_exists
                ? "已有素材底稿，待生成素材地图"
                : "待生成素材底稿",
          "director-panel",
        ) +
        workflowStep(
          "声音轨",
          audioState,
          (audio.slides_with_audio || 0) + " 页已有音频，" + (audio.generated_segment_count || 0) + " 段",
          "audio-workbench",
        ) +
        workflowStep(
          "成片线",
          remotionState,
          remotion.output_video_exists
            ? "已检测到 MP4"
            : remotion.input_props_exists
              ? (remotion.render_plan_source || "入参已生成") + "，待渲染"
              : "待生成 input-props",
          "remotion-panel",
        );
      renderWorkflowDetails(data, {
        dealState: dealState,
        directorState: directorState,
        audioState: audioState,
        remotionState: remotionState,
      }, currentTaskId);
    }

    return {
      renderPipelineState: renderPipelineState,
      renderWorkspaceStatus: renderWorkspaceStatus,
    };
  }

  window.ZhikeWorkflowUI = {
    create: createWorkflowUI,
  };
})();
