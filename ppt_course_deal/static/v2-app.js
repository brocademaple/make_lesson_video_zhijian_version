(function () {
  "use strict";

  var RAIL_KEY = "any2video.ui.rail-collapsed.v1";
  var compactRailQuery = window.matchMedia ? window.matchMedia("(max-width: 1180px)") : null;

  function initialRailState() {
    if (compactRailQuery && compactRailQuery.matches) return true;
    try {
      var saved = localStorage.getItem(RAIL_KEY);
      if (saved === "1" || saved === "0") return saved === "1";
    } catch (error) {
      // The workbench remains usable when local storage is unavailable.
    }
    return window.matchMedia && window.matchMedia("(max-width: 1180px)").matches;
  }

  var state = {
    projects: [],
    project: null,
    busy: false,
    busyLabel: "",
    railCollapsed: initialRailState(),
    selectedSceneId: "",
    draggedSceneId: "",
    capabilities: null,
  };

  var app = document.getElementById("app");
  if (!app) return;
  document.title = "any2video";

  if (compactRailQuery && compactRailQuery.addEventListener) {
    compactRailQuery.addEventListener("change", function (event) {
      if (!event.matches || state.railCollapsed) return;
      state.railCollapsed = true;
      render();
    });
  }

  function api(path, options) {
    return fetch(path, options || {}).then(function (res) {
      return res.json().catch(function () { return {}; }).then(function (data) {
        if (!res.ok) throw new Error(data.detail || data.message || "请求失败");
        return data;
      });
    });
  }

  function h(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function short(value, limit) {
    var text = String(value || "").replace(/\s+/g, " ").trim();
    return text.length > limit ? text.slice(0, limit - 1).trim() + "…" : text;
  }

  function assets(kind) {
    var list = state.project && Array.isArray(state.project.assets) ? state.project.assets : [];
    return kind ? list.filter(function (item) { return item.type === kind; }) : list;
  }

  function latest(kind) {
    var list = assets(kind);
    return list.length ? list[list.length - 1] : null;
  }

  function scenes() {
    var plan = state.project && state.project.scene_plan;
    return plan && Array.isArray(plan.scenes) ? plan.scenes : [];
  }

  function outputs() {
    return state.project && Array.isArray(state.project.outputs) ? state.project.outputs : [];
  }

  function runs() {
    return state.project && Array.isArray(state.project.runs) ? state.project.runs : [];
  }

  function capability(capabilityId) {
    var list = state.capabilities && Array.isArray(state.capabilities.capabilities) ? state.capabilities.capabilities : [];
    return list.find(function (item) { return item.id === capabilityId; }) || null;
  }

  function engineLabel(engine) {
    return {auto: "自动", remotion: "Remotion", hyperframes: "HyperFrames", hybrid: "双引擎"}[engine] || "自动";
  }

  function engineStatusLabel(status) {
    return {ready: "已就绪", prepared: "已准备", pending: "待执行", fallback: "安全回退", failed: "失败"}[status] || "待路由";
  }

  function assetById(assetId) {
    return assets().find(function (item) { return item.id === assetId; }) || null;
  }

  function sceneImage(scene) {
    var ids = scene && Array.isArray(scene.asset_ids) ? scene.asset_ids : [];
    for (var index = 0; index < ids.length; index += 1) {
      var asset = assetById(ids[index]);
      if (asset && asset.type === "image") return asset;
    }
    return null;
  }

  function selectedScene() {
    var list = scenes();
    if (!list.length) return null;
    var selected = list.find(function (scene) { return scene.id === state.selectedSceneId; });
    if (selected) return selected;
    state.selectedSceneId = list[0].id;
    return list[0];
  }

  function assetUrl(asset) {
    if (!state.project || !asset) return "";
    return "/api/v2/projects/" + encodeURIComponent(state.project.id) + "/assets/" + encodeURIComponent(asset.id) + "/file";
  }

  function statusLabel(status) {
    return {
      draft: "等待素材",
      materials_ready: "素材就绪",
      scene_plan_ready: "编排完成",
      rendering: "生成中",
      render_ready: "成片完成",
      render_failed: "生成失败",
      brief_ready: "素材就绪",
    }[status] || "本地项目";
  }

  function render() {
    app.dataset.ready = "1";
    app.innerHTML = [
      '<div class="workbench' + (state.railCollapsed ? " rail-collapsed" : "") + '">',
      renderTopbar(),
      '<div class="layout">',
      renderRail(),
      renderComposer(),
      renderOutputPanel(),
      "</div>",
      state.busy ? renderBusy() : "",
      '<div id="toast" class="toast" aria-live="polite"></div>',
      "</div>",
    ].join("");
    bind();
    syncDraftState();
  }

  function renderTopbar() {
    var project = state.project;
    return [
      '<header class="topbar">',
      '<div class="brand">',
      '<button class="brand-wordmark" type="button" data-action="toggle-rail" aria-label="打开或收起项目库">any<span>2</span>video</button>',
      "</div>",
      '<div class="project-context">',
      '<span>' + h(project ? "当前项目" : "本地工作台") + '</span>',
      '<strong>' + h(project ? project.title : "从任何素材开始") + '</strong>',
      "</div>",
      '<div class="top-actions">',
      project ? '<span class="project-state">' + h(statusLabel(project.status)) + '</span>' : '',
      '<button class="quiet-button" type="button" data-action="refresh">同步</button>',
      "</div>",
      "</header>",
    ].join("");
  }

  function renderRail() {
    if (state.railCollapsed) {
      return [
        '<aside class="rail rail-mini" aria-label="项目库已收起">',
        '<button class="rail-toggle" type="button" data-action="toggle-rail" aria-label="展开项目库">项目库</button>',
        "</aside>",
      ].join("");
    }
    return [
      '<aside class="rail" aria-label="项目库">',
      '<div class="panel-head"><div><h2>项目</h2><span>' + h(state.projects.length) + '</span></div><button class="rail-toggle" type="button" data-action="toggle-rail">隐藏</button></div>',
      '<div class="rail-scroll">',
      state.projects.length ? renderProjectForm("rail-project-form") : "",
      renderProjectList(),
      "</div>",
      '<div class="rail-foot"><span>本机存储</span><span>不会上传云端</span></div>',
      "</aside>",
    ].join("");
  }

  function renderProjectForm(variant) {
    return [
      '<form id="project-form" class="new-project ' + h(variant || "") + '">',
      '<label for="project-title">' + (variant === "starter-project-form" ? "给这条视频起个名字" : "新建视频") + '</label>',
      '<div class="project-create-row">',
      '<input id="project-title" name="title" placeholder="未命名视频" maxlength="120" autocomplete="off" />',
      '<button class="small-primary" type="submit">创建</button>',
      '</div>',
      "</form>",
    ].join("");
  }

  function renderProjectList() {
    if (!state.projects.length) {
      return '<div class="empty small-empty"><strong>还没有项目</strong><span>从中间的创作区开始第一条视频。</span></div>';
    }
    return '<div class="project-list">' + state.projects.map(function (project) {
      var active = state.project && state.project.id === project.id ? " active" : "";
      return [
        '<button class="project-row' + active + '" type="button" data-project-id="' + h(project.id) + '">',
        '<strong>' + h(project.title) + "</strong>",
        '<span>' + h(project.asset_count || 0) + " 项素材</span>",
        '<span>' + h(project.output_count || 0) + " 个成片版本</span>",
        "</button>",
      ].join("");
    }).join("") + "</div>";
  }

  function rememberProject(project) {
    if (!project) return;
    state.project = project;
    var summary = {
      id: project.id,
      title: project.title,
      status: project.status,
      asset_count: Array.isArray(project.assets) ? project.assets.length : Number(project.asset_count || 0),
      scene_count: project.scene_plan && Array.isArray(project.scene_plan.scenes)
        ? project.scene_plan.scenes.length
        : Number(project.scene_count || 0),
      output_count: Array.isArray(project.outputs) ? project.outputs.length : Number(project.output_count || 0),
    };
    var index = state.projects.findIndex(function (item) { return item.id === project.id; });
    if (index >= 0) state.projects[index] = Object.assign({}, state.projects[index], summary);
    else state.projects.unshift(summary);
  }

  function renderComposer() {
    if (!state.project) {
      return [
        '<main class="composer empty-workspace">',
        '<div class="empty-workspace-inner">',
        '<div class="empty-intro">',
        '<span class="empty-label">新视频</span>',
        '<h2>从任何素材开始</h2>',
        '<p>写下想表达的内容，放入画面和旁白。剩下的交给时间线。</p>',
        renderProjectForm("starter-project-form"),
        '</div>',
        '<div class="material-sequence" aria-label="视频素材组成">',
        '<div><span>文字</span><strong>讲什么</strong></div>',
        '<div><span>画面</span><strong>看什么</strong></div>',
        '<div><span>旁白</span><strong>多长时间</strong></div>',
        '</div>',
        "</div>",
        "</main>",
      ].join("");
    }
    var text = latest("text");
    var audio = latest("audio");
    var images = assets("image");
    var hasScenes = scenes().length > 0;
    return [
      '<main class="composer">',
      '<div class="composer-head">',
      '<div><span class="composer-label">' + (hasScenes ? "导演台" : "创作画布") + '</span><h2>' + h(state.project.title) + '</h2><p>' + (hasScenes ? "逐镜头调整叙事、画面和节奏。" : "整理这条视频需要的内容、画面与声音。") + '</p></div>',
      renderReadiness(text, images, audio),
      "</div>",
      hasScenes ? renderDirectorWorkbench() : "",
      hasScenes ? '<details class="material-drawer"><summary>素材与分镜设置</summary>' : "",
      '<form id="quick-form" class="quick-form">',
      '<div class="material-grid">',
      renderTextInput(text),
      '<div class="media-stack">',
      renderImageInput(images),
      renderAudioInput(audio),
      "</div>",
      "</div>",
      renderGenerateBar(text, images, audio),
      "</form>",
      hasScenes ? "</details>" : "",
      "</main>",
    ].join("");
  }

  function renderReadiness(text, images, audio) {
    return [
      '<div class="readiness" aria-label="素材完整性">',
      readinessItem("文字", Boolean(text), text ? "已保存" : "待添加"),
      readinessItem("画面", images.length > 0 && images.length <= 8, images.length ? images.length + " 张" : "待添加"),
      readinessItem("旁白", Boolean(audio && audio.duration_sec), audio && audio.duration_sec ? audio.duration_sec.toFixed(1) + " 秒" : "待添加"),
      "</div>",
    ].join("");
  }

  function readinessItem(label, ready, detail) {
    return '<div class="readiness-item ' + (ready ? "ready" : "missing") + '"><span>' + h(label) + "</span><strong>" + h(detail) + "</strong></div>";
  }

  function renderTextInput(text) {
    return [
      '<section class="input-section text-section">',
      '<div class="input-heading"><div><span class="material-index">A</span><h3>视频文字</h3><p>标题、观点和字幕内容</p></div><span id="text-count">0 / 300</span></div>',
      '<textarea id="quick-text" name="content" maxlength="300" rows="8" placeholder="写下这条视频想表达的核心内容…"></textarea>',
      '<div class="current-material">',
      text ? '<span>已保存的文字</span><p>' + h(short(text.content || text.summary, 180)) + "</p>" : '<p class="muted">输入的新文字会在生成时保存到项目。</p>',
      "</div>",
      "</section>",
    ].join("");
  }

  function renderImageInput(images) {
    return [
      '<section class="input-section image-section">',
      '<div class="input-heading"><div><span class="material-index">B</span><h3>画面</h3><p>按选择顺序进入时间线</p></div><span id="image-draft-count">' + h(images.length) + " / 8</span></div>",
      '<label class="file-drop" for="quick-images"><strong>选择图片</strong><span>PNG、JPEG、WebP、SVG，最多 8 张</span></label>',
      '<input class="visually-hidden" id="quick-images" name="images" type="file" accept="image/png,image/jpeg,image/webp,image/svg+xml" multiple />',
      '<div class="image-strip">',
      images.length ? images.map(function (image) { return '<img src="' + h(assetUrl(image)) + '" alt="' + h(image.title || "视频画面") + '" />'; }).join("") : '<div class="empty inline-empty">尚未添加画面</div>',
      "</div>",
      "</section>",
    ].join("");
  }

  function renderAudioInput(audio) {
    return [
      '<section class="input-section audio-section">',
      '<div class="input-heading"><div><span class="material-index">C</span><h3>旁白</h3><p>音频时长决定视频长度</p></div><span id="audio-draft-state">' + h(audio && audio.duration_sec ? audio.duration_sec.toFixed(1) + " 秒" : "待添加") + "</span></div>",
      '<label class="file-drop audio-drop" for="quick-audio"><strong>选择音频</strong><span>MP3、WAV 或 M4A</span></label>',
      '<input class="visually-hidden" id="quick-audio" name="audio" type="file" accept="audio/mpeg,audio/wav,audio/x-wav,audio/mp4,audio/x-m4a,.mp3,.wav,.m4a" />',
      audio ? '<audio class="audio-player" controls src="' + h(assetUrl(audio)) + '"></audio>' : '<div class="empty inline-empty audio-empty">尚未添加旁白</div>',
      "</section>",
    ].join("");
  }

  function renderGenerateBar(text, images, audio) {
    var missing = [];
    if (!text) missing.push("文字");
    if (!images.length) missing.push("图片");
    if (!audio || !audio.duration_sec) missing.push("旁白");
    return [
      '<section class="generate-bar">',
      '<div><span class="generate-label">分镜</span><h3>根据素材生成镜头初稿</h3><p id="generate-hint">' + h(missing.length ? "还需要：" + missing.join("、") : (scenes().length ? "重新生成会替换当前导演稿" : "素材已齐，可以生成镜头")) + "</p></div>",
      '<button id="generate-button" class="generate-button" type="submit" ' + (missing.length ? "disabled" : "") + ">" + (scenes().length ? "重新生成镜头" : "生成镜头") + "</button>",
      "</section>",
    ].join("");
  }

  function renderDirectorWorkbench() {
    var list = scenes();
    var scene = selectedScene();
    if (!scene) return "";
    var total = list.reduce(function (sum, item) { return sum + Number(item.duration_sec || 0); }, 0);
    return [
      '<section class="director-workbench">',
      '<div class="director-toolbar">',
      '<div><h3>镜头导演</h3><p>' + h(list.length) + " 个镜头，约 " + h(total.toFixed(1)) + " 秒</p></div>",
      '<div class="director-actions">',
      '<button class="director-button" type="button" data-action="add-scene">新增镜头</button>',
      '<button class="director-button primary" type="button" data-action="render-video">生成成片</button>',
      "</div>",
      "</div>",
      renderExecutionStrip(),
      '<div class="director-main">',
      renderScenePreview(scene),
      renderSceneEditor(scene),
      "</div>",
      renderSceneTimeline(list),
      "</section>",
    ].join("");
  }

  function renderExecutionStrip() {
    var remotion = capability("remotion.render_project");
    var hyperframes = capability("hyperframes.render_scene");
    var recent = runs()[0];
    var completed = recent && Array.isArray(recent.steps) ? recent.steps.filter(function (step) {
      return ["ready", "fallback", "skipped"].indexOf(step.status) >= 0;
    }).length : 0;
    var stepTotal = recent && Array.isArray(recent.steps) ? recent.steps.length : 0;
    return [
      '<div class="execution-strip" aria-label="本地执行能力">',
      '<div><span class="engine-dot ' + h(remotion && remotion.status || "unknown") + '"></span><strong>Remotion</strong><em>' + h(remotion && remotion.status === "ready" ? "本机可用" : "未就绪") + '</em></div>',
      '<div><span class="engine-dot ' + h(hyperframes && hyperframes.status || "unknown") + '"></span><strong>HyperFrames</strong><em>' + h(hyperframes ? (hyperframes.status === "ready" ? "本机可用" : hyperframes.status === "on_demand" ? "可按需启用" : "安全回退") : "检测中") + '</em></div>',
      recent ? '<div class="latest-run"><span>' + h(recent.kind === "render_project" ? "最近成片" : "最近执行") + '</span><strong>' + h(engineStatusLabel(recent.status)) + '</strong><em>' + h(completed + " / " + stepTotal + " 步") + '</em></div>' : '<div class="latest-run"><span>执行账本</span><strong>尚未运行</strong><em>每一步都会保存在本机</em></div>',
      '</div>',
    ].join("");
  }

  function renderScenePreview(scene) {
    var image = sceneImage(scene);
    return [
      '<div class="director-preview-column">',
      '<div class="director-preview">',
      image ? '<img src="' + h(assetUrl(image)) + '" alt="' + h(image.title || "当前镜头画面") + '" />' : '<div class="director-preview-empty">为镜头选择画面</div>',
      '<div class="director-preview-shade"></div>',
      '<div class="director-preview-copy"><span>' + h(short(scene.purpose || "镜头预览", 28)) + '</span><strong>' + h(short(scene.onscreen_text || scene.title, 54)) + '</strong></div>',
      "</div>",
      '<div class="preview-caption"><span>镜头预览</span><strong>' + h(Number(scene.duration_sec || 0).toFixed(1)) + " 秒</strong></div>",
      "</div>",
    ].join("");
  }

  function renderSceneEditor(scene) {
    var image = sceneImage(scene);
    var imageOptions = assets("image").map(function (asset) {
      return '<option value="' + h(asset.id) + '" ' + (image && image.id === asset.id ? "selected" : "") + ">" + h(asset.title || "未命名画面") + "</option>";
    }).join("");
    var engine = scene.engine || {};
    var requested = scene.renderer || engine.requested || "auto";
    var creative = engine.resolved === "hyperframes" || engine.resolved === "hybrid";
    return [
      '<form id="scene-editor-form" class="scene-editor" data-scene-id="' + h(scene.id) + '">',
      '<div class="scene-editor-head"><div><span>当前镜头</span><strong>' + h(scene.title || "未命名镜头") + '</strong></div><span class="scene-id">' + h(scene.id) + "</span></div>",
      '<div class="scene-fields two-column">',
      '<label><span>镜头名称</span><input name="title" maxlength="80" value="' + h(scene.title || "") + '" /></label>',
      '<label><span>时长</span><div class="duration-field"><input name="duration_sec" type="number" min="0.5" max="600" step="0.1" value="' + h(Number(scene.duration_sec || 4).toFixed(1)) + '" /><em>秒</em></div></label>',
      "</div>",
      '<div class="scene-engine-row">',
      '<label class="scene-field"><span>执行引擎</span><select name="renderer"><option value="auto" ' + (requested === "auto" ? "selected" : "") + '>自动路由</option><option value="remotion" ' + (requested === "remotion" ? "selected" : "") + '>Remotion · 稳定模板</option><option value="hyperframes" ' + (requested === "hyperframes" ? "selected" : "") + '>HyperFrames · 创意动效</option><option value="hybrid" ' + (requested === "hybrid" ? "selected" : "") + '>双引擎 · 创意叠加</option></select></label>',
      '<div class="engine-decision"><span>' + h(engineLabel(engine.resolved)) + ' · ' + h(engineStatusLabel(engine.status)) + '</span><p>' + h(engine.reason || "保存后由执行内核选择引擎") + '</p>' + (engine.error ? '<details><summary>回退原因</summary><p>' + h(short(engine.error, 420)) + '</p></details>' : '') + '</div>',
      '</div>',
      '<label class="scene-field"><span>画面素材</span><select name="image_asset_id"><option value="">无画面</option>' + imageOptions + "</select></label>",
      '<label class="scene-field"><span>屏幕文字</span><textarea name="onscreen_text" rows="2" maxlength="220" placeholder="这一镜需要观众看到的文字">' + h(scene.onscreen_text || "") + "</textarea></label>",
      '<label class="scene-field"><span>旁白</span><textarea name="narration" rows="3" maxlength="500" placeholder="这一镜需要说出的内容">' + h(scene.narration || "") + "</textarea></label>",
      '<label class="scene-field"><span>镜头目的</span><input name="purpose" maxlength="120" value="' + h(scene.purpose || "") + '" placeholder="例如：建立问题、展示步骤、收束观点" /></label>',
      '<div class="scene-editor-actions">',
      '<div><button class="text-action" type="button" data-action="duplicate-scene" data-scene-id="' + h(scene.id) + '">复制</button><button class="text-action danger" type="button" data-action="delete-scene" data-scene-id="' + h(scene.id) + '">删除</button>' + (creative ? '<button class="text-action engine-action" type="button" data-action="prepare-scene" data-scene-id="' + h(scene.id) + '">' + (engine.status === "fallback" ? "重试创意镜头" : "执行创意镜头") + '</button>' : '') + '</div>',
      '<button class="director-button primary" type="submit">保存镜头</button>',
      "</div>",
      "</form>",
    ].join("");
  }

  function renderSceneTimeline(list) {
    return [
      '<div class="scene-timeline-head"><div><h3>镜头顺序</h3><p>拖动卡片调整成片顺序</p></div><span>自动保存排序</span></div>',
      '<div class="scene-timeline" role="list">',
      list.map(function (scene, index) {
        var image = sceneImage(scene);
        var selected = scene.id === state.selectedSceneId ? " selected" : "";
        var engine = scene.engine || {};
        return [
          '<article class="scene-card' + selected + '" draggable="true" data-scene-card="' + h(scene.id) + '" role="listitem">',
          '<button class="scene-card-select" type="button" data-action="select-scene" data-scene-id="' + h(scene.id) + '">',
          '<span class="scene-number">' + h(String(index + 1).padStart(2, "0")) + "</span>",
          image ? '<img src="' + h(assetUrl(image)) + '" alt="" />' : '<span class="scene-card-empty">无画面</span>',
          '<strong>' + h(short(scene.onscreen_text || scene.title, 30)) + "</strong>",
          '<span class="scene-duration">' + h(Number(scene.duration_sec || 0).toFixed(1)) + " 秒 · " + h(engineLabel(engine.resolved)) + "</span>",
          "</button>",
          '<div class="scene-card-order"><button type="button" data-action="move-scene-left" data-scene-id="' + h(scene.id) + '" aria-label="前移" ' + (index === 0 ? "disabled" : "") + '>前移</button><button type="button" data-action="move-scene-right" data-scene-id="' + h(scene.id) + '" aria-label="后移" ' + (index === list.length - 1 ? "disabled" : "") + ">后移</button></div>",
          "</article>",
        ].join("");
      }).join(""),
      "</div>",
    ].join("");
  }

  function renderOutputPanel() {
    var list = outputs();
    var current = list[0];
    return [
      '<aside class="output-panel" aria-label="成片预览">',
      '<div class="panel-head output-head"><div><h2>成片预览</h2><span>9:16</span></div>' + (current ? '<span class="output-status ' + h(current.status) + '">' + h(outputStatusLabel(current.status)) + "</span>" : '<span class="output-status empty-status">等待生成</span>') + "</div>",
      '<div class="output-scroll">',
      current ? renderCurrentOutput(current) : renderOutputEmpty(),
      list.length > 1 ? renderOutputHistory(list.slice(1)) : "",
      "</div>",
      "</aside>",
    ].join("");
  }

  function outputStatusLabel(status) {
    return {ready: "已完成", failed: "失败", rendering: "生成中", planned: "待生成"}[status] || status;
  }

  function renderOutputEmpty() {
    return [
      '<div class="output-empty">',
      '<div class="phone-frame"><div class="phone-empty"><div class="preview-guide"><span></span><span></span><span></span></div><strong>等待第一版成片</strong><p>素材齐全后，画面会在这里播放。</p></div></div>',
      '<div class="output-empty-meta"><span>1080 × 1920</span><span>MP4</span></div>',
      "</div>",
    ].join("");
  }

  function renderCurrentOutput(output) {
    var player = output.status === "ready" && output.file_url
      ? '<video class="output-video" controls preload="metadata" src="' + h(output.file_url) + "?v=" + encodeURIComponent(output.created_at || "") + '"></video>'
      : '<div class="render-placeholder"><strong>' + h(outputStatusLabel(output.status)) + "</strong><span>" + h(output.status === "failed" ? "查看日志后重试" : "Remotion 正在处理") + "</span></div>";
    return [
      '<section class="current-output">',
      '<div class="preview-stage">' + player + "</div>",
      '<div class="output-meta">',
      '<div><span>时长</span><strong>' + h(output.duration_sec ? Number(output.duration_sec).toFixed(1) + " 秒" : "待计算") + "</strong></div>",
      '<div><span>画幅</span><strong>1080 × 1920</strong></div>',
      "</div>",
      output.status === "ready" ? '<a class="open-output" href="' + h(output.file_url) + '" target="_blank" rel="noreferrer">打开 MP4</a>' : "",
      output.video_path ? '<details class="output-details"><summary>文件位置</summary><p class="output-path">' + h(output.video_path) + "</p></details>" : "",
      output.log && output.status === "failed" ? '<details class="render-log" open><summary>渲染日志</summary><pre>' + h(short(output.log, 2400)) + "</pre></details>" : "",
      "</section>",
    ].join("");
  }

  function renderOutputHistory(list) {
    return '<section class="output-history"><div class="section-row"><h3>历史版本</h3><span>最近 ' + h(Math.min(list.length, 5)) + " 个</span></div>" + list.slice(0, 5).map(function (output) {
      return '<div class="history-row"><span>' + h(outputStatusLabel(output.status)) + '</span><strong>' + h(output.duration_sec ? Number(output.duration_sec).toFixed(1) + " 秒" : "待计算") + "</strong></div>";
    }).join("") + "</section>";
  }

  function renderBusy() {
    return '<div class="busy-layer" role="status" aria-live="polite"><div class="busy-card"><div class="render-pulse" aria-hidden="true"></div><strong>' + h(state.busyLabel || "正在处理") + '</strong><p>保持页面打开，完成后会自动更新。</p></div></div>';
  }

  function bind() {
    var projectForm = document.getElementById("project-form");
    if (projectForm) projectForm.addEventListener("submit", onCreateProject);
    var quickForm = document.getElementById("quick-form");
    if (quickForm) quickForm.addEventListener("submit", onGenerateScenes);
    var sceneEditor = document.getElementById("scene-editor-form");
    if (sceneEditor) sceneEditor.addEventListener("submit", onSaveScene);

    var text = document.getElementById("quick-text");
    var images = document.getElementById("quick-images");
    var audio = document.getElementById("quick-audio");
    if (text) text.addEventListener("input", syncDraftState);
    if (images) images.addEventListener("change", syncDraftState);
    if (audio) audio.addEventListener("change", syncDraftState);

    document.querySelectorAll("[data-project-id]").forEach(function (button) {
      button.addEventListener("click", function () { loadProject(button.getAttribute("data-project-id")); });
    });
    document.querySelectorAll("[data-action]").forEach(function (button) {
      button.addEventListener("click", function () {
        var action = button.getAttribute("data-action");
        if (action === "refresh") loadProjects(true);
        if (action === "toggle-rail") toggleRail();
        if (action === "select-scene") selectScene(button.getAttribute("data-scene-id"));
        if (action === "add-scene") addScene();
        if (action === "duplicate-scene") duplicateScene(button.getAttribute("data-scene-id"));
        if (action === "delete-scene") deleteScene(button.getAttribute("data-scene-id"));
        if (action === "move-scene-left") moveScene(button.getAttribute("data-scene-id"), -1);
        if (action === "move-scene-right") moveScene(button.getAttribute("data-scene-id"), 1);
        if (action === "render-video") renderVideo();
        if (action === "prepare-scene") prepareScene(button.getAttribute("data-scene-id"));
      });
    });
    document.querySelectorAll("[data-scene-card]").forEach(function (card) {
      card.addEventListener("dragstart", function () {
        state.draggedSceneId = card.getAttribute("data-scene-card") || "";
        card.classList.add("dragging");
      });
      card.addEventListener("dragend", function () {
        state.draggedSceneId = "";
        card.classList.remove("dragging");
      });
      card.addEventListener("dragover", function (event) { event.preventDefault(); });
      card.addEventListener("drop", function (event) {
        event.preventDefault();
        reorderSceneBefore(state.draggedSceneId, card.getAttribute("data-scene-card"));
      });
    });
  }

  function toggleRail() {
    state.railCollapsed = !state.railCollapsed;
    try {
      localStorage.setItem(RAIL_KEY, state.railCollapsed ? "1" : "0");
    } catch (error) {
      // Persistence is optional.
    }
    render();
  }

  function syncDraftState() {
    if (!state.project) return;
    var textInput = document.getElementById("quick-text");
    var imageInput = document.getElementById("quick-images");
    var audioInput = document.getElementById("quick-audio");
    var button = document.getElementById("generate-button");
    var hint = document.getElementById("generate-hint");
    var textCount = document.getElementById("text-count");
    var imageCount = document.getElementById("image-draft-count");
    var audioState = document.getElementById("audio-draft-state");
    var draftText = textInput ? textInput.value.trim() : "";
    var draftImages = imageInput && imageInput.files ? imageInput.files.length : 0;
    var draftAudio = audioInput && audioInput.files ? audioInput.files.length : 0;
    var totalImages = assets("image").length + draftImages;
    var hasText = Boolean(latest("text") || draftText);
    var hasImages = totalImages > 0 && totalImages <= 8;
    var hasAudio = Boolean((latest("audio") && latest("audio").duration_sec) || draftAudio);

    if (textCount) textCount.textContent = draftText.length + " / 300";
    if (imageCount) imageCount.textContent = totalImages + " / 8";
    if (audioState && draftAudio) audioState.textContent = audioInput.files[0].name;
    if (button) button.disabled = state.busy || !hasText || !hasImages || !hasAudio;
    if (hint) {
      var missing = [];
      if (!hasText) missing.push("文字");
      if (!hasImages) missing.push(totalImages > 8 ? "图片超过 8 张" : "图片");
      if (!hasAudio) missing.push("旁白");
      hint.textContent = missing.length ? "还需要：" + missing.join("、") : "素材已齐，可以开始生成";
    }
  }

  function onCreateProject(event) {
    event.preventDefault();
    var title = new FormData(event.currentTarget).get("title") || "未命名视频";
    setBusy(true, "正在创建项目");
    api("/api/v2/projects", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({title: title, aspect_ratio: "9:16", platform: "短视频", style: "clean", target_duration_sec: 30}),
    }).then(function (project) {
      rememberProject(project);
      return loadProjects(false);
    }).then(function () {
      toast("项目已创建");
    }).catch(showError).finally(function () { setBusy(false); });
  }

  function uploadAsset(kind, file, content, title) {
    var form = new FormData();
    form.append("asset_type", kind);
    form.append("title", title || (file && file.name) || kind);
    form.append("role", kind === "audio" ? "narration" : kind);
    if (content) form.append("content", content);
    if (file) form.append("file", file);
    return api("/api/v2/projects/" + encodeURIComponent(state.project.id) + "/assets", {method: "POST", body: form}).then(function (data) {
      rememberProject(data.project);
      return data.asset;
    });
  }

  function onGenerateScenes(event) {
    event.preventDefault();
    if (!state.project || state.busy) return;
    if (scenes().length && !window.confirm("重新生成会替换当前导演稿，继续吗？")) return;
    var textInput = document.getElementById("quick-text");
    var imageInput = document.getElementById("quick-images");
    var audioInput = document.getElementById("quick-audio");
    var draftText = textInput ? textInput.value.trim() : "";
    var imageFiles = imageInput && imageInput.files ? Array.prototype.slice.call(imageInput.files) : [];
    var audioFile = audioInput && audioInput.files && audioInput.files[0] ? audioInput.files[0] : null;

    setBusy(true, "正在整理素材");
    var chain = Promise.resolve();
    if (draftText) chain = chain.then(function () { return uploadAsset("text", null, draftText, "视频文字"); });
    imageFiles.forEach(function (file, index) {
      chain = chain.then(function () {
        state.busyLabel = "正在导入图片 " + (index + 1) + " / " + imageFiles.length;
        updateBusyLabel();
        return uploadAsset("image", file, "", file.name);
      });
    });
    if (audioFile) chain = chain.then(function () { return uploadAsset("audio", audioFile, "", audioFile.name); });

    chain.then(function () {
      state.busyLabel = "正在生成镜头初稿";
      updateBusyLabel();
      return api("/api/v2/projects/" + encodeURIComponent(state.project.id) + "/scene-plan/quick", {method: "POST"});
    }).then(function (data) {
      rememberProject(data.project);
      state.selectedSceneId = scenes().length ? scenes()[0].id : "";
      toast("镜头初稿已生成");
    }).catch(showError).finally(function () { setBusy(false); });
  }

  function selectScene(sceneId) {
    if (!sceneId || state.selectedSceneId === sceneId) return;
    state.selectedSceneId = sceneId;
    render();
  }

  function onSaveScene(event) {
    event.preventDefault();
    if (!state.project || state.busy) return;
    var form = event.currentTarget;
    var sceneId = form.getAttribute("data-scene-id");
    var scene = scenes().find(function (item) { return item.id === sceneId; });
    if (!scene) return;
    var data = new FormData(form);
    var imageId = String(data.get("image_asset_id") || "");
    var preservedIds = (scene.asset_ids || []).filter(function (assetId) {
      var asset = assetById(assetId);
      return asset && asset.type !== "image";
    });
    if (imageId) preservedIds.push(imageId);
    var payload = {
      title: String(data.get("title") || "").trim(),
      duration_sec: Number(data.get("duration_sec") || 4),
      onscreen_text: String(data.get("onscreen_text") || "").trim(),
      narration: String(data.get("narration") || "").trim(),
      subtitle: String(data.get("onscreen_text") || "").trim(),
      purpose: String(data.get("purpose") || "").trim(),
      renderer: String(data.get("renderer") || "auto"),
      asset_ids: preservedIds,
      status: "approved",
    };
    setBusy(true, "正在保存镜头");
    api("/api/v2/projects/" + encodeURIComponent(state.project.id) + "/scenes/" + encodeURIComponent(sceneId), {
      method: "PUT",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload),
    }).then(function (response) {
      rememberProject(response.project);
      state.selectedSceneId = sceneId;
      toast("镜头已保存");
    }).catch(showError).finally(function () { setBusy(false); });
  }

  function addScene() {
    if (!state.project || state.busy) return;
    setBusy(true, "正在新增镜头");
    api("/api/v2/projects/" + encodeURIComponent(state.project.id) + "/scenes", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({after_scene_id: state.selectedSceneId || null}),
    }).then(function (response) {
      rememberProject(response.project);
      state.selectedSceneId = response.scene.id;
      toast("已新增镜头");
    }).catch(showError).finally(function () { setBusy(false); });
  }

  function duplicateScene(sceneId) {
    if (!state.project || !sceneId || state.busy) return;
    setBusy(true, "正在复制镜头");
    api("/api/v2/projects/" + encodeURIComponent(state.project.id) + "/scenes/" + encodeURIComponent(sceneId) + "/duplicate", {method: "POST"})
      .then(function (response) {
        rememberProject(response.project);
        state.selectedSceneId = response.scene.id;
        toast("镜头已复制");
      }).catch(showError).finally(function () { setBusy(false); });
  }

  function deleteScene(sceneId) {
    if (!state.project || !sceneId || state.busy) return;
    if (!window.confirm("删除这个镜头吗？")) return;
    var list = scenes();
    var index = list.findIndex(function (scene) { return scene.id === sceneId; });
    setBusy(true, "正在删除镜头");
    api("/api/v2/projects/" + encodeURIComponent(state.project.id) + "/scenes/" + encodeURIComponent(sceneId), {method: "DELETE"})
      .then(function (response) {
        rememberProject(response.project);
        var next = scenes()[Math.min(index, Math.max(0, scenes().length - 1))];
        state.selectedSceneId = next ? next.id : "";
        toast("镜头已删除");
      }).catch(showError).finally(function () { setBusy(false); });
  }

  function persistSceneOrder(ids) {
    if (!state.project || !ids.length || state.busy) return;
    var projectId = state.project.id;
    setBusy(true, "正在保存镜头顺序");
    api("/api/v2/projects/" + encodeURIComponent(projectId) + "/scene-order", {
      method: "PUT",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({scene_ids: ids}),
    }).then(function (response) {
      rememberProject(response.project);
      toast("镜头顺序已保存");
    }).catch(showError).finally(function () { setBusy(false); });
  }

  function moveScene(sceneId, offset) {
    var ids = scenes().map(function (scene) { return scene.id; });
    var index = ids.indexOf(sceneId);
    var nextIndex = index + offset;
    if (index < 0 || nextIndex < 0 || nextIndex >= ids.length) return;
    ids.splice(index, 1);
    ids.splice(nextIndex, 0, sceneId);
    persistSceneOrder(ids);
  }

  function reorderSceneBefore(draggedId, targetId) {
    if (!draggedId || !targetId || draggedId === targetId) return;
    var ids = scenes().map(function (scene) { return scene.id; });
    var from = ids.indexOf(draggedId);
    var to = ids.indexOf(targetId);
    if (from < 0 || to < 0) return;
    ids.splice(from, 1);
    ids.splice(to, 0, draggedId);
    persistSceneOrder(ids);
  }

  function renderVideo() {
    if (!state.project || !scenes().length || state.busy) return;
    setBusy(true, "双引擎正在编排成片");
    api("/api/v2/projects/" + encodeURIComponent(state.project.id) + "/render", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({execute: true, timeout_sec: 300}),
    }).then(function (data) {
      rememberProject(data.project);
      if (data.output && data.output.status === "failed") throw new Error("视频生成失败，请查看渲染日志");
      toast("成片已生成");
    }).catch(showError).finally(function () { setBusy(false); });
  }

  function prepareScene(sceneId) {
    if (!state.project || !sceneId || state.busy) return;
    setBusy(true, "正在执行创意镜头");
    api("/api/v2/projects/" + encodeURIComponent(state.project.id) + "/scenes/" + encodeURIComponent(sceneId) + "/prepare", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({execute: true, allow_on_demand: false, timeout_sec: 180}),
    }).then(function (data) {
      rememberProject(data.project);
      state.capabilities = data.capabilities || state.capabilities;
      var task = data.tasks && data.tasks[0];
      toast(task && task.status === "fallback" ? "创意引擎未就绪，已安全回退" : "创意镜头已准备");
    }).catch(showError).finally(function () { setBusy(false); });
  }

  function updateBusyLabel() {
    var label = document.querySelector(".busy-card strong");
    if (label) label.textContent = state.busyLabel;
  }

  function setBusy(value, label) {
    state.busy = value;
    state.busyLabel = label || "";
    render();
  }

  function loadProjects(selectFirst) {
    return api("/api/v2/projects").then(function (data) {
      state.projects = data.projects || [];
      if (selectFirst && !state.project && state.projects.length) return loadProject(state.projects[0].id);
      render();
      return null;
    });
  }

  function loadCapabilities() {
    return api("/api/v2/capabilities").then(function (registry) {
      state.capabilities = registry;
      render();
      return registry;
    });
  }

  function loadProject(projectId) {
    if (!projectId) return Promise.resolve();
    setBusy(true, "正在打开项目");
    return api("/api/v2/projects/" + encodeURIComponent(projectId)).then(function (project) {
      rememberProject(project);
      state.selectedSceneId = project.scene_plan && project.scene_plan.scenes && project.scene_plan.scenes.length ? project.scene_plan.scenes[0].id : "";
    }).catch(showError).finally(function () { setBusy(false); });
  }

  function toast(message) {
    window.setTimeout(function () {
      var node = document.getElementById("toast");
      if (!node) return;
      node.textContent = message;
      node.classList.add("show");
      window.setTimeout(function () { node.classList.remove("show"); }, 2400);
    }, 20);
  }

  function showError(error) {
    toast(error && error.message ? error.message : "操作失败");
  }

  Promise.all([loadCapabilities(), loadProjects(true)]).catch(showError);
})();
