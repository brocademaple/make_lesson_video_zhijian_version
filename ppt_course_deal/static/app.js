(function () {
  const uploadPanel = document.getElementById("upload-panel");
  const workspace = document.getElementById("workspace");
  const appMain = document.getElementById("app-main");
  const slideRail = document.getElementById("slide-rail");
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("file-input");
  const errorUpload = document.getElementById("error-upload");
  const previewSetupBanner = document.getElementById("preview-setup-banner");
  const errorWork = document.getElementById("error-work");
  const slideList = document.getElementById("slide-list");
  const fileLabel = document.getElementById("file-label");
  const btnChangeFile = document.getElementById("btn-change-file");
  const slideCounter = document.getElementById("slide-counter");
  const slideMeta = document.getElementById("slide-meta");
  const pvModeLabel = document.getElementById("pv-mode-label");
  const pvImageWrap = document.getElementById("pv-image-wrap");
  const pvCarousel = document.getElementById("pv-carousel");
  const pvCarouselState = document.getElementById("pv-carousel-state");
  const btnPvCarouselPrev = document.getElementById("pv-carousel-prev");
  const btnPvCarouselNext = document.getElementById("pv-carousel-next");
  const pvImage = document.getElementById("pv-image");
  const pvCarouselImgOuter = document.getElementById("pv-carousel-img-outer");
  const pvPreviewZoomDialog = document.getElementById("pv-preview-zoom-dialog");
  const pvPreviewZoomImg = document.getElementById("pv-preview-zoom-img");
  const pvPreviewZoomTitle = document.getElementById("pv-preview-zoom-title");
  const btnPvPreviewZoomDownload = document.getElementById("btn-pv-preview-zoom-download");
  const pvTitle = document.getElementById("pv-title");
  const helpDialog = document.getElementById("help-dialog");
  const helpDialogTitle = document.getElementById("help-dialog-title");
  const helpDialogBody = document.getElementById("help-dialog-body");
  const btnHelpProduct = document.getElementById("btn-help-product");
  const btnHelpUpload = document.getElementById("btn-help-upload");
  const btnHelpCli = document.getElementById("btn-help-cli");
  const btnHelpPreview = document.getElementById("btn-help-preview");
  const pvBlocks = document.getElementById("pv-blocks");
  const pvNotesWrap = document.getElementById("pv-notes-wrap");
  const pvNotes = document.getElementById("pv-notes");
  const statusLine = document.getElementById("status-line");
  const resultBanner = document.getElementById("result-banner");
  const resultStats = document.getElementById("result-stats");
  const downloadLink = document.getElementById("download-link");
  const imagesBanner = document.getElementById("images-banner");
  const taskList = document.getElementById("task-list");
  const btnWorkspaceTaskDrawer = document.getElementById("btn-workspace-task-drawer");
  const workspaceTaskDrawerBackdrop = document.getElementById("workspace-task-drawer-backdrop");
  const workspaceTaskDrawerPanel = document.getElementById("workspace-task-drawer-panel");
  const workspaceTaskDrawerList = document.getElementById("workspace-task-drawer-list");
  const btnWorkspaceTaskDrawerClose = document.getElementById("btn-workspace-task-drawer-close");
  const btnRefreshTasks = document.getElementById("btn-refresh-tasks");
  const btnHelpTaskList = document.getElementById("btn-help-task-list");
  const btnHelpAudioSegments = document.getElementById("btn-help-audio-segments");
  const btnHelpAudioGenerateConfirm = document.getElementById("btn-help-audio-generate-confirm");
  const btnHelpAudioGenSettings = document.getElementById("btn-help-audio-gen-settings");
  const taskDeletePopconfirm = document.getElementById("task-delete-popconfirm");
  const taskRenamePopover = document.getElementById("task-rename-popover");
  const taskRenameInput = document.getElementById("task-rename-input");
  const taskIdPopover = document.getElementById("task-id-popover");
  const taskIdPopoverCode = document.getElementById("task-id-popover-code");
  const btnTaskIdCopy = document.getElementById("task-id-popover-copy");
  const btnTaskIdClose = document.getElementById("task-id-popover-close");
  const btnTaskDeleteCancel = document.getElementById("task-delete-cancel");
  const btnTaskDeleteConfirm = document.getElementById("task-delete-confirm");
  const btnTaskRenameCancel = document.getElementById("task-rename-cancel");
  const btnTaskRenameSave = document.getElementById("task-rename-save");

  const audioWorkbenchStatus = document.getElementById("audio-workbench-status");
  const audioPlayer = document.getElementById("audio-player");
  const btnAudioSave = document.getElementById("btn-audio-save");
  const audioSegmentsDialog = document.getElementById("audio-segments-dialog");
  /** `true`：标题栏喇叭打开的「仅已生成 mp3」视图；`false`：完整逐字稿与生成 */
  var audioSegmentsDialogListenOnly = false;
  const btnAudioSegmentsToolbar = document.getElementById("btn-audio-segments-toolbar");
  const btnGenerateSlideVisual = document.getElementById("btn-generate-slide-visual");
  const btnAiVisualStock = document.getElementById("btn-ai-visual-stock");
  const aiVisualStockDialog = document.getElementById("ai-visual-stock-dialog");
  const aiVisualStockImg = document.getElementById("ai-visual-stock-img");
  const aiVisualStockEmpty = document.getElementById("ai-visual-stock-empty");
  const aiVisualStockTitle = document.getElementById("ai-visual-stock-title");
  const btnAiVisualStockDownload = document.getElementById("btn-ai-visual-stock-download");
  const pvSourceTabs = document.getElementById("pv-source-tabs");
  const pvTabOriginal = document.getElementById("pv-tab-original");
  const pvTabAi = document.getElementById("pv-tab-ai");
  const generateVisualDialog = document.getElementById("generate-visual-dialog");
  const gvPanelForm = document.getElementById("gv-panel-form");
  const gvPanelResult = document.getElementById("gv-panel-result");
  const gvFooterConfirm = document.getElementById("gv-footer-confirm");
  const gvFooterResult = document.getElementById("gv-footer-result");
  const gvStorageHint = document.getElementById("gv-storage-hint");
  const gvSlideLabel = document.getElementById("gv-slide-label");
  const gvModel = document.getElementById("gv-model");
  const gvSize = document.getElementById("gv-size");
  const gvPrompt = document.getElementById("gv-prompt");
  const gvOpenNewTab = document.getElementById("gv-open-new-tab");
  const gvError = document.getElementById("gv-error");
  const gvResultImg = document.getElementById("gv-result-img");
  const gvResultPathText = document.getElementById("gv-result-path-text");
  const btnGvCancel = document.getElementById("btn-gv-cancel");
  const btnGvSubmit = document.getElementById("btn-gv-submit");
  const btnGvDone = document.getElementById("btn-gv-done");
  const btnAudioOpenSegments = document.getElementById("btn-audio-open-segments");
  const btnAudioSegmentAdd = document.getElementById("btn-audio-segment-add");
  const btnAudioSegmentsSave = document.getElementById("btn-audio-segments-save");
  const audioGenSettingsDialog = document.getElementById("audio-gen-settings-dialog");
  const audioGenerateConfirmDialog = document.getElementById("audio-generate-confirm-dialog");
  const audioGenerateConfirmSegLabel = document.getElementById("audio-generate-confirm-seg-label");
  const transcriptRewriteDialog = document.getElementById("transcript-rewrite-dialog");
  const transcriptRewriteVersionsDialog = document.getElementById("transcript-rewrite-versions-dialog");
  const btnAudioGenSettings = document.getElementById("btn-audio-gen-settings");
  const externalSettingsDialog = document.getElementById("external-settings-dialog");
  const btnExternalSettings = document.getElementById("btn-external-settings");
  /** 服务端 GET /api/settings/external 返回的 transcript_rewrite_defaults.extra_instructions */
  var transcriptRewriteDefaultsExtra = "";
  const btnImportTranscript = document.getElementById("btn-import-transcript");
  const importTranscriptDialog = document.getElementById("import-transcript-dialog");
  const importTranscriptTextarea = document.getElementById("import-transcript-textarea");
  const importTranscriptFile = document.getElementById("import-transcript-file");
  const importTranscriptStep1 = document.getElementById("import-transcript-step1");
  const importTranscriptStep2 = document.getElementById("import-transcript-step2");
  const importTranscriptStep2Summary = document.getElementById("import-transcript-step2-summary");
  const importTranscriptWarnings = document.getElementById("import-transcript-warnings");
  const importTranscriptConflictsWrap = document.getElementById("import-transcript-conflicts-wrap");
  const importTranscriptConflictsList = document.getElementById("import-transcript-conflicts-list");
  const importTranscriptFooterRow1 = document.getElementById("import-transcript-footer-row1");
  const importTranscriptFooterRow2 = document.getElementById("import-transcript-footer-row2");
  const btnImportTranscriptCancel = document.getElementById("btn-import-transcript-cancel");
  const btnImportTranscriptPreview = document.getElementById("btn-import-transcript-preview");
  const btnImportTranscriptBack = document.getElementById("btn-import-transcript-back");
  const btnImportTranscriptApply = document.getElementById("btn-import-transcript-apply");
  const directorSummary = document.getElementById("director-summary");
  const directorScenes = document.getElementById("director-scenes");
  const btnDirectorRawManifest = document.getElementById("btn-director-raw-manifest");
  const btnDirectorRebuild = document.getElementById("btn-director-rebuild");
  const btnDirectorRefresh = document.getElementById("btn-director-refresh");
  const btnDirectorExport = document.getElementById("btn-director-export");
  const remotionSummary = document.getElementById("remotion-summary");
  const remotionCommand = document.getElementById("remotion-command");
  const btnRemotionGenerate = document.getElementById("btn-remotion-generate");
  const btnRemotionRefresh = document.getElementById("btn-remotion-refresh");
  const taskWorkflowTitle = document.getElementById("task-workflow-title");
  const taskWorkflowSteps = document.getElementById("task-workflow-steps");
  const btnWorkflowRefresh = document.getElementById("btn-workflow-refresh");

  var AUDIO_GEN_LS_KEY = "ppt_course_audio_gen_overrides";

  /** @type {{ warnings: string[], conflicts: any[], filled_slides?: number, slide_count?: number } | null} */
  let pendingImportPreview = null;

  /** @type {File | null} */
  let currentFile = null;
  /** @type {any[]} */
  let slides = [];
  let selectedIndex = 0;
  /** @type {string | null} */
  let sessionId = null;
  let imagesAvailable = false;
  /** 与 slides 数量可能不一致（渲染异常时） */
  let previewCount = 0;
  /** @type {"libreoffice" | "placeholder"} */
  let previewSource = "libreoffice";
  /** @type {string | null} */
  let lastObjectUrl = null;
  /** 与当前预览模式对应的说明全文，供「本页预览说明」弹窗使用 */
  let currentPreviewHelpText = "";

  /** @type {string[]} */
  let audioTranscripts = [];
  /** @type {string[][]} */
  let audioTranscriptSegments = [];
  let audioWorkspaceKind = "session";
  /** @type {string} */
  let audioWorkspaceKey = "";
  /** @type {Record<string, string>} */
  let audioGeneratedFiles = {};
  /** @type {Record<string, number>} 键同 segmentFileKey：「页索引-段索引」→ 秒（当前生效音频） */
  let audioSegmentDurations = {};
  /** 每段多次生成的记录列表（键同 segmentFileKey） */
  let audioSegmentVersions = {};
  let pendingAudioGenerateSegmentIndex = 0;
  let pendingRewriteSegmentIndex = 0;
  let pendingVersionsSegmentIndex = 0;
  /** 口播优化返回的、可合并进本机「音频生成参数」的 MiniMax 字段 */
  let lastTranscriptRewriteMinimaxHints = null;
  /** 口播优化返回的 delivery_notes（与 hints 一并写入版本库） */
  let lastTranscriptRewriteDeliveryNotes = null;
  /** 口播版本库「采用此版本」后，下一次「确认生成本段音频」表单强制叠加的 hints（用完清空） */
  let pendingAudioConfirmMinimaxOverlay = null;
  /** @type {string | null} */
  let currentTaskId = null;
  /** @type {any | null} */
  let directorManifestCache = null;
  /** 上传解析会话为 session；从已存任务打开为 stored */
  let previewMode = "session";

  let pvMediaRequestId = 0;
  /** @type {Array<{ url: string, caption: string, kind: string, shapeIndex: number | null }>} */
  let pvCarouselFrames = [];
  let pvCarouselIndex = 0;

  /** 主预览区：原版 LibreOffice/切图 vs 全文生图（仅当各页均有 AI 图时可选） */
  /** @type {'original' | 'ai'} */
  let pvPreviewSourceMode = "original";
  /** @type {{ slide_count: number, slides_with_generated: number[], all_slides_complete: boolean } | null} */
  let genVisualCoverage = null;

  /** 与 /api/health 的 max_upload_mb 一致；默认 50MB 直至拉取到配置 */
  let maxUploadBytes = 50 * 1024 * 1024;
  const maxUploadReady = (async function () {
    try {
      var r = await fetch("/api/health");
      if (!r.ok) return;
      var j = await r.json();
      if (typeof j.max_upload_mb === "number" && j.max_upload_mb > 0) {
        maxUploadBytes = j.max_upload_mb * 1024 * 1024;
      }
      var pr = j.preview_render;
      if (pr && !pr.ready && pr.install_hint_zh && previewSetupBanner) {
        previewSetupBanner.textContent = pr.install_hint_zh;
        previewSetupBanner.classList.remove("hidden");
      }
    } catch (_) {}
  })();

  var HELP_PRODUCT_BODY =
    "上传后解析全文稿；若本机安装了 LibreOffice + Poppler，服务端会将每一页渲染为 PNG，通过临时 URL 预览（类似私有图床）。";
  var HELP_UPLOAD_BODY =
    "主页左侧为**已存任务**列表（可滚动）；点击任务打开预览。上传解析后左侧切换为**幻灯片缩略图**列表；右侧为预览图，「当前页解析文本」可折叠查看抽取文本（默认展开）。";
  var HELP_CLI_BODY =
    "可在终端执行命令行转换：ppt-course transform 输入.pptx（将「输入.pptx」换成你的文件路径）。无需打开本页面。";
  var HELP_TASK_LIST_BODY =
    "上传并成功解析后，文件副本与解析结果会保存在项目根目录下的 ppt_course_data/tasks/（每任务一个子文件夹），并出现在主页**左侧已存任务**列表中。点击某条会在主界面打开预览（左侧变为幻灯片缩略图 + 右侧大图）。\n\n列表为空表示尚无记录；可在服务端设置环境变量 PPT_COURSE_DATA 改用其它数据根目录。";
  var HELP_AUDIO_SEGMENTS_BODY =
    "主预览区标题栏喇叭只用于本页已生成各段 MP3：同一段可多次合成，喇叭弹窗内按「记录」列出历次生成，可分别试听、下载或删除（删除会移除服务端文件，并清除本站 IndexedDB 中为自动下载缓存的副本）。逐字稿编辑、口播优化与生成请用音频工作台里的「打开本页逐字稿与音频」。浏览器「下载」文件夹里另行出现的同名文件需自行整理。\n\n每一段口播对应多次可选的 MiniMax 合成。点击某段的「生成」会先弹出确认框（合成参数与文案预览），确认后再请求服务端调用 T2A；成功后通常会触发一条 mp3 的本地下载，服务端写入任务目录且不覆盖同段旧文件。\n\n「口播稿优化」在服务端调用 OpenAI 兼容大模型，按 MiniMax 官方文档白名单优化停顿与插入语；需先在顶栏「外部 API 配置」→「口播稿优化 API」启用并填写密钥。左右对比确认后再「采用改写稿」。「口播版本库」将多版改写稿存在浏览器本地，可按段选用。\n\n切换幻灯片后，若本弹窗保持打开，列表会随当前页刷新。\n\n「保存到服务端」会把当前内存中的全部逐字稿（含每一页的多段结构 transcript_segments）通过 PUT /api/audio/workspace 写入服务端工作区元数据，用于持久化与下次打开任务恢复；仅保存文本，不会在未点「生成」时调用 MiniMax。";
  var HELP_AUDIO_GENERATE_CONFIRM_BODY =
    "弹窗内「合成参数」为可编辑表单：打开时已填入「外部 API 配置」中的 MiniMax 默认值 + 本机「进入音频生成设置」保存的偏好之合并结果；你可在本次生成前临时改模型、音色、语速、情绪、音量等。修改不会自动写回 localStorage；若希望长期默认，请仍到「进入音频生成设置」点「保存合成参数」。\n\n下方为待合成该段口播稿预览。点击「开始生成」才向服务端发起 POST /api/audio/workspace/generate，请求体中的 minimax_overrides 为当前表单值，仅针对当前选中的这一段。";
  var HELP_AUDIO_GEN_SETTINGS_BODY =
    "本弹窗中的选项对应 MiniMax 语音合成 HTTP 接口 /v1/t2a_v2 的请求体字段（不含 API Key 与 API Base）。此处点击「保存合成参数」后，偏好写入本机浏览器 localStorage；在「本页逐字稿与音频」里对某段点击「生成」时，会以 minimax_overrides 与顶栏「外部 API 配置」中的服务端默认值合并，再向本机服务发起单次合成。\n\n官方文档（Speech T2A HTTP）：https://platform.minimax.io/docs/api-reference/speech-t2a-http\n\n为何这里没有 API Key：密钥属于账户凭证，必须由服务端读取并保存在数据目录下的配置文件（例如 ppt_course_data/config/external_apis.json），供 POST /api/audio/workspace/generate 统一使用；若把密钥放进仅存在于浏览器的「音频生成参数」，既存在泄露风险，服务端也无法在合成时使用。填写位置：点击顶栏「外部 API 配置」，在同一界面设置 MiniMax API Key、API Base、可选 Group ID，并可做连通测试；本弹窗只负责模型、音色、采样等与单次合成偏好相关的字段。";

  var SVG_TASK_PENCIL =
    '<svg class="task-row-icon-btn__svg" viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>';

  var SVG_TASK_INFO =
    '<svg class="task-row-icon-btn__svg" viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M6 2c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6H6zm7 7V3.5L18.5 9H13z"/></svg>';

  /** @type {string | null} */
  var pendingDeleteId = null;
  /** @type {HTMLElement | null} */
  var deletePopoverAnchor = null;
  /** @type {string | null} */
  var pendingRenameId = null;
  /** @type {HTMLElement | null} */
  var renamePopoverAnchor = null;
  /** @type {HTMLElement | null} */
  var taskIdPopoverAnchor = null;

  function closeTaskIdPopover() {
    taskIdPopoverAnchor = null;
    if (taskIdPopover) {
      taskIdPopover.classList.add("hidden");
      taskIdPopover.setAttribute("aria-hidden", "true");
    }
  }

  function closeDeletePopconfirm() {
    pendingDeleteId = null;
    deletePopoverAnchor = null;
    if (taskDeletePopconfirm) {
      taskDeletePopconfirm.classList.add("hidden");
      taskDeletePopconfirm.setAttribute("aria-hidden", "true");
    }
  }

  function closeRenamePopover() {
    pendingRenameId = null;
    renamePopoverAnchor = null;
    if (taskRenamePopover) {
      taskRenamePopover.classList.add("hidden");
      taskRenamePopover.setAttribute("aria-hidden", "true");
    }
    if (taskRenameInput) taskRenameInput.value = "";
  }

  function closeAllTaskPopovers() {
    closeDeletePopconfirm();
    closeRenamePopover();
    closeTaskIdPopover();
  }

  function positionTaskPopover(anchor, popEl) {
    if (!anchor || !popEl) return;
    requestAnimationFrame(function () {
      var r = anchor.getBoundingClientRect();
      var pw = popEl.offsetWidth || 200;
      var ph = popEl.offsetHeight || 80;
      var left = r.right - pw;
      if (left < 8) left = 8;
      if (left + pw > window.innerWidth - 8) left = window.innerWidth - pw - 8;
      var top = r.bottom + 6;
      if (top + ph > window.innerHeight - 8) top = r.top - ph - 6;
      if (top < 8) top = 8;
      popEl.style.left = left + "px";
      popEl.style.top = top + "px";
    });
  }

  function openDeletePopconfirm(anchorBtn, taskId) {
    closeRenamePopover();
    closeTaskIdPopover();
    pendingDeleteId = taskId;
    deletePopoverAnchor = anchorBtn;
    if (taskDeletePopconfirm) {
      taskDeletePopconfirm.classList.remove("hidden");
      taskDeletePopconfirm.setAttribute("aria-hidden", "false");
      positionTaskPopover(anchorBtn, taskDeletePopconfirm);
    }
  }

  function openRenamePopover(anchorBtn, taskId, currentName) {
    closeDeletePopconfirm();
    closeTaskIdPopover();
    pendingRenameId = taskId;
    renamePopoverAnchor = anchorBtn;
    if (taskRenamePopover && taskRenameInput) {
      taskRenameInput.value = currentName || "";
      taskRenamePopover.classList.remove("hidden");
      taskRenamePopover.setAttribute("aria-hidden", "false");
      positionTaskPopover(anchorBtn, taskRenamePopover);
      setTimeout(function () {
        taskRenameInput.focus();
        taskRenameInput.select();
      }, 0);
    }
  }

  document.addEventListener(
    "mousedown",
    function (e) {
      if (taskDeletePopconfirm && !taskDeletePopconfirm.classList.contains("hidden")) {
        if (
          taskDeletePopconfirm.contains(/** @type {Node} */ (e.target)) ||
          (deletePopoverAnchor && deletePopoverAnchor.contains(/** @type {Node} */ (e.target)))
        ) {
          return;
        }
        closeDeletePopconfirm();
      }
      if (taskRenamePopover && !taskRenamePopover.classList.contains("hidden")) {
        if (
          taskRenamePopover.contains(/** @type {Node} */ (e.target)) ||
          (renamePopoverAnchor && renamePopoverAnchor.contains(/** @type {Node} */ (e.target)))
        ) {
          return;
        }
        closeRenamePopover();
      }
      if (taskIdPopover && !taskIdPopover.classList.contains("hidden")) {
        if (
          taskIdPopover.contains(/** @type {Node} */ (e.target)) ||
          (taskIdPopoverAnchor && taskIdPopoverAnchor.contains(/** @type {Node} */ (e.target)))
        ) {
          return;
        }
        closeTaskIdPopover();
      }
    },
    true
  );

  function openTaskIdPopover(anchorBtn, taskId) {
    closeDeletePopconfirm();
    closeRenamePopover();
    taskIdPopoverAnchor = anchorBtn;
    if (taskIdPopover && taskIdPopoverCode) {
      taskIdPopoverCode.textContent = taskId || "";
      taskIdPopover.classList.remove("hidden");
      taskIdPopover.setAttribute("aria-hidden", "false");
      positionTaskPopover(anchorBtn, taskIdPopover);
    }
  }

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    closeAllTaskPopovers();
  });

  window.addEventListener("resize", function () {
    if (
      deletePopoverAnchor &&
      taskDeletePopconfirm &&
      !taskDeletePopconfirm.classList.contains("hidden")
    ) {
      positionTaskPopover(deletePopoverAnchor, taskDeletePopconfirm);
    }
    if (
      renamePopoverAnchor &&
      taskRenamePopover &&
      !taskRenamePopover.classList.contains("hidden")
    ) {
      positionTaskPopover(renamePopoverAnchor, taskRenamePopover);
    }
    if (
      taskIdPopoverAnchor &&
      taskIdPopover &&
      !taskIdPopover.classList.contains("hidden")
    ) {
      positionTaskPopover(taskIdPopoverAnchor, taskIdPopover);
    }
  });

  function openHelp(title, bodyText) {
    if (!helpDialog || !helpDialogTitle || !helpDialogBody) return;
    helpDialogTitle.textContent = title;
    helpDialogBody.innerHTML = "";
    bodyText.split(/\n\n+/).forEach(function (chunk) {
      var t = chunk.trim();
      if (!t) return;
      var p = document.createElement("p");
      p.className = "help-dialog__para";
      p.textContent = t;
      helpDialogBody.appendChild(p);
    });
    helpDialog.showModal();
  }

  if (helpDialog) {
    helpDialog.addEventListener("click", function (e) {
      if (e.target === helpDialog) helpDialog.close();
    });
  }

  if (btnHelpProduct) {
    btnHelpProduct.addEventListener("click", function () {
      openHelp("使用说明", HELP_PRODUCT_BODY);
    });
  }
  if (btnHelpUpload) {
    btnHelpUpload.addEventListener("click", function (e) {
      e.stopPropagation();
      e.preventDefault();
      openHelp("上传与解析", HELP_UPLOAD_BODY);
    });
  }
  if (btnHelpCli) {
    btnHelpCli.addEventListener("click", function () {
      openHelp("命令行", HELP_CLI_BODY);
    });
  }
  if (btnHelpPreview) {
    btnHelpPreview.addEventListener("click", function () {
      openHelp("本页预览说明", currentPreviewHelpText || "（暂无说明）");
    });
  }
  if (btnHelpTaskList) {
    btnHelpTaskList.addEventListener("click", function () {
      openHelp("已存任务", HELP_TASK_LIST_BODY);
    });
  }
  if (btnHelpAudioSegments) {
    btnHelpAudioSegments.addEventListener("click", function (e) {
      e.stopPropagation();
      e.preventDefault();
      openHelp("本页逐字稿与音频", HELP_AUDIO_SEGMENTS_BODY);
    });
  }
  if (btnHelpAudioGenerateConfirm) {
    btnHelpAudioGenerateConfirm.addEventListener("click", function (e) {
      e.stopPropagation();
      e.preventDefault();
      openHelp("确认生成本段音频", HELP_AUDIO_GENERATE_CONFIRM_BODY);
    });
  }
  if (btnHelpAudioGenSettings) {
    btnHelpAudioGenSettings.addEventListener("click", function (e) {
      e.stopPropagation();
      e.preventDefault();
      openHelp("音频生成参数（MiniMax T2A）", HELP_AUDIO_GEN_SETTINGS_BODY);
    });
  }

  const btnThemeToggle = document.getElementById("btn-theme-toggle");
  const themeSun = document.querySelector(".theme-toggle__icon--sun");
  const themeMoon = document.querySelector(".theme-toggle__icon--moon");

  function applyTheme(theme) {
    var isLight = theme === "light";
    document.documentElement.setAttribute("data-theme", isLight ? "light" : "dark");
    try {
      localStorage.setItem("ppt-theme", isLight ? "light" : "dark");
    } catch (e) {}
    if (themeSun && themeMoon) {
      themeSun.classList.toggle("hidden", isLight);
      themeMoon.classList.toggle("hidden", !isLight);
    }
    if (btnThemeToggle) {
      btnThemeToggle.setAttribute(
        "aria-label",
        isLight ? "切换为深色模式" : "切换为浅色模式"
      );
      btnThemeToggle.title = isLight ? "切换深色" : "切换浅色";
    }
  }

  function syncThemeFromDocument() {
    var raw = document.documentElement.getAttribute("data-theme");
    applyTheme(raw === "light" ? "light" : "dark");
  }

  syncThemeFromDocument();

  if (btnThemeToggle) {
    btnThemeToggle.addEventListener("click", function () {
      var cur = document.documentElement.getAttribute("data-theme") || "dark";
      applyTheme(cur === "light" ? "dark" : "light");
    });
  }

  function showErr(el, msg) {
    el.textContent = msg;
    el.classList.remove("hidden");
  }

  function clearErr(el) {
    el.classList.add("hidden");
    el.textContent = "";
  }

  function resetDownload() {
    resultBanner.classList.add("hidden");
    resultStats.textContent = "";
    downloadLink.removeAttribute("href");
    downloadLink.removeAttribute("download");
    if (lastObjectUrl) {
      URL.revokeObjectURL(lastObjectUrl);
      lastObjectUrl = null;
    }
  }

  function formatSize(n) {
    if (n < 1024) return n + " B";
    if (n < 1024 * 1024) return (n / 1024).toFixed(1) + " KB";
    return (n / (1024 * 1024)).toFixed(1) + " MB";
  }

  function previewUrl(index) {
    if (!sessionId) return "";
    return "/api/preview/" + encodeURIComponent(sessionId) + "/" + index;
  }

  function storedPreviewUrl(taskId, index) {
    return "/api/tasks/" + encodeURIComponent(taskId) + "/preview/" + index;
  }

  function formatTaskTime(iso) {
    if (!iso || typeof iso !== "string") return "";
    var d = new Date(iso);
    if (Number.isNaN(d.getTime())) {
      return iso.replace("T", " ").replace(/\+00:00$/, "").slice(0, 19);
    }
    try {
      return d.toLocaleString(undefined, {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false,
        timeZoneName: "short",
      });
    } catch (_) {
      return d.toLocaleString();
    }
  }

  function makeTaskInfoButton(taskId) {
    var btnInfo = document.createElement("button");
    btnInfo.type = "button";
    btnInfo.className = "task-row-icon-btn";
    btnInfo.setAttribute("aria-label", "查看任务 ID");
    btnInfo.title = "任务 ID";
    btnInfo.innerHTML = SVG_TASK_INFO;
    btnInfo.addEventListener("click", function (e) {
      e.stopPropagation();
      openTaskIdPopover(btnInfo, taskId);
    });
    return btnInfo;
  }

  function buildTaskListItem(t, options) {
    var navOnly = options && options.navOnly;
    var li = document.createElement("li");
    li.className = "task-li" + (navOnly ? " task-li--nav" : "");
    var main = document.createElement("button");
    main.type = "button";
    main.className = "task-row-main";
    if (navOnly && currentTaskId && t.id === currentTaskId) {
      main.classList.add("is-current");
    }
    main.innerHTML =
      '<span class="task-row-name">' +
      escapeHtml(t.filename || "") +
      '</span><span class="task-row-meta">' +
      (t.slide_count || 0) +
      " 页" +
      (t.images_available ? " · 含整页预览图" : "") +
      " · " +
      escapeHtml(formatTaskTime(t.created_at)) +
      "</span>";
    main.addEventListener("click", function () {
      if (navOnly) closeWorkspaceTaskDrawer();
      openStoredTask(t.id);
    });

    li.appendChild(main);
    if (navOnly) {
      li.appendChild(makeTaskInfoButton(t.id));
    } else {
      var actions = document.createElement("div");
      actions.className = "task-row-actions";

      actions.appendChild(makeTaskInfoButton(t.id));

      var btnEdit = document.createElement("button");
      btnEdit.type = "button";
      btnEdit.className = "task-row-icon-btn";
      btnEdit.setAttribute("aria-label", "编辑任务名称");
      btnEdit.innerHTML = SVG_TASK_PENCIL;
      btnEdit.addEventListener("click", function (e) {
        e.stopPropagation();
        openRenamePopover(btnEdit, t.id, t.filename || "");
      });

      var del = document.createElement("button");
      del.type = "button";
      del.className = "task-row-icon-btn task-row-icon-btn--danger";
      del.setAttribute("aria-label", "删除该任务");
      del.textContent = "×";
      del.addEventListener("click", function (e) {
        e.stopPropagation();
        openDeletePopconfirm(del, t.id);
      });

      actions.appendChild(btnEdit);
      actions.appendChild(del);
      li.appendChild(actions);
    }
    return li;
  }

  function renderTaskListFromData(tasks, listEl, options) {
    if (!listEl) return;
    listEl.innerHTML = "";
    tasks.forEach(function (t) {
      listEl.appendChild(buildTaskListItem(t, options));
    });
    listEl.setAttribute("aria-label", tasks.length ? "已存任务列表" : "暂无任务");
  }

  function setWorkspaceTaskDrawerTabVisible(show) {
    if (!btnWorkspaceTaskDrawer) return;
    btnWorkspaceTaskDrawer.classList.toggle("hidden", !show);
  }

  function closeWorkspaceTaskDrawer() {
    if (workspaceTaskDrawerBackdrop) {
      workspaceTaskDrawerBackdrop.classList.remove("is-open");
      workspaceTaskDrawerBackdrop.setAttribute("aria-hidden", "true");
    }
    if (workspaceTaskDrawerPanel) {
      workspaceTaskDrawerPanel.classList.remove("is-open");
      workspaceTaskDrawerPanel.setAttribute("aria-hidden", "true");
      workspaceTaskDrawerPanel.setAttribute("aria-modal", "false");
    }
    if (btnWorkspaceTaskDrawer) {
      btnWorkspaceTaskDrawer.setAttribute("aria-expanded", "false");
      btnWorkspaceTaskDrawer.setAttribute("aria-label", "展开已存任务列表");
    }
  }

  function workspaceTaskDrawerIsOpen() {
    return !!(workspaceTaskDrawerPanel && workspaceTaskDrawerPanel.classList.contains("is-open"));
  }

  async function openWorkspaceTaskDrawer() {
    if (!workspaceTaskDrawerPanel) return;
    await refreshTaskList();
    if (workspaceTaskDrawerBackdrop) {
      workspaceTaskDrawerBackdrop.classList.add("is-open");
      workspaceTaskDrawerBackdrop.setAttribute("aria-hidden", "false");
    }
    workspaceTaskDrawerPanel.classList.add("is-open");
    workspaceTaskDrawerPanel.setAttribute("aria-hidden", "false");
    workspaceTaskDrawerPanel.setAttribute("aria-modal", "true");
    if (btnWorkspaceTaskDrawer) {
      btnWorkspaceTaskDrawer.setAttribute("aria-expanded", "true");
      btnWorkspaceTaskDrawer.setAttribute("aria-label", "收起已存任务列表");
    }
  }

  function toggleWorkspaceTaskDrawer() {
    if (workspaceTaskDrawerIsOpen()) closeWorkspaceTaskDrawer();
    else void openWorkspaceTaskDrawer();
  }

  async function refreshTaskList() {
    if (!taskList) return;
    closeAllTaskPopovers();
    try {
      var res = await fetch("/api/tasks");
      if (!res.ok) return;
      var data = await res.json();
      var tasks = data.tasks || [];
      renderTaskListFromData(tasks, taskList, { navOnly: false });
      if (workspaceTaskDrawerList) {
        renderTaskListFromData(tasks, workspaceTaskDrawerList, { navOnly: true });
      }
    } catch (_) {}
  }

  async function executeDeleteStoredTask(id) {
    if (!id) return;
    try {
      var res = await fetch("/api/tasks/" + encodeURIComponent(id), { method: "DELETE" });
      if (!res.ok) return;
      closeDeletePopconfirm();
      refreshTaskList();
      if (currentTaskId === id) backToUpload();
    } catch (_) {}
  }

  async function executeRenameTask() {
    var id = pendingRenameId;
    if (!id || !taskRenameInput) return;
    var name = taskRenameInput.value.trim();
    if (!name) return;
    try {
      var res = await fetch("/api/tasks/" + encodeURIComponent(id), {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: name }),
      });
      if (!res.ok) return;
      if (currentTaskId === id && fileLabel) fileLabel.textContent = name + " · 已存任务";
      closeRenamePopover();
      refreshTaskList();
    } catch (_) {}
  }

  function slideSnippetText(s) {
    return (
      (s.title && s.title !== "（无标题）" ? s.title : "") ||
      (s.text_blocks && s.text_blocks[0]) ||
      (s.text ? s.text.slice(0, 80) : "") ||
      "（空白页）"
    );
  }

  function refreshGenerateSlideVisualEnabled() {
    if (!btnGenerateSlideVisual) return;
    var ok = !!currentTaskId && slides.length > 0;
    btnGenerateSlideVisual.disabled = !ok;
    btnGenerateSlideVisual.title = ok
      ? "打开确认框：核对存储路径、模型与提示词后再调用文生图（消耗网关额度）"
      : "需任务已持久化（解析返回 task_id，或从左侧打开已存任务）";
  }

  async function refreshGenVisualCoverage() {
    if (!currentTaskId) {
      genVisualCoverage = null;
      updatePvSourceTabsUi();
      updateAiVisualToolbarBtn();
      return;
    }
    try {
      var res = await fetch(
        "/api/tasks/" + encodeURIComponent(currentTaskId) + "/generated-visual-coverage",
      );
      if (!res.ok) genVisualCoverage = null;
      else genVisualCoverage = await res.json();
    } catch (_) {
      genVisualCoverage = null;
    }
    if (pvPreviewSourceMode === "ai" && (!genVisualCoverage || !genVisualCoverage.all_slides_complete)) {
      pvPreviewSourceMode = "original";
    }
    updatePvSourceTabsUi();
    updateAiVisualToolbarBtn();
  }

  function updatePvSourceTabsUi() {
    if (!pvSourceTabs || !pvTabOriginal || !pvTabAi) return;
    var show =
      !!currentTaskId &&
      !!genVisualCoverage &&
      !!genVisualCoverage.all_slides_complete &&
      slides.length > 0 &&
      genVisualCoverage.slide_count === slides.length;
    if (show) {
      pvSourceTabs.classList.remove("hidden");
      pvTabOriginal.setAttribute("aria-selected", pvPreviewSourceMode === "original" ? "true" : "false");
      pvTabAi.setAttribute("aria-selected", pvPreviewSourceMode === "ai" ? "true" : "false");
    } else {
      pvSourceTabs.classList.add("hidden");
      pvTabOriginal.setAttribute("aria-selected", "true");
      pvTabAi.setAttribute("aria-selected", "false");
    }
  }

  function updateAiVisualToolbarBtn() {
    if (!btnAiVisualStock) return;
    if (!currentTaskId || !slides.length) {
      btnAiVisualStock.disabled = true;
      btnAiVisualStock.classList.remove("has-file");
      return;
    }
    btnAiVisualStock.disabled = false;
    var has = false;
    if (genVisualCoverage && Array.isArray(genVisualCoverage.slides_with_generated)) {
      has = genVisualCoverage.slides_with_generated.indexOf(selectedIndex) >= 0;
    }
    if (has) btnAiVisualStock.classList.add("has-file");
    else btnAiVisualStock.classList.remove("has-file");
  }

  function openAiVisualStockDialog() {
    if (!aiVisualStockDialog || !currentTaskId) return;
    var base =
      "/api/tasks/" +
      encodeURIComponent(currentTaskId) +
      "/slide/" +
      selectedIndex +
      "/generated-visual";
    var url = base + (base.indexOf("?") >= 0 ? "&" : "?") + "zbust=" + Date.now();
    if (aiVisualStockTitle) {
      aiVisualStockTitle.textContent = "第 " + (selectedIndex + 1) + " 页 · AI 配图";
    }
    if (aiVisualStockImg) {
      aiVisualStockImg.classList.add("hidden");
      aiVisualStockImg.removeAttribute("src");
    }
    if (aiVisualStockEmpty) aiVisualStockEmpty.classList.add("hidden");
    if (btnAiVisualStockDownload) btnAiVisualStockDownload.disabled = true;
    aiVisualStockDialog.showModal();
    void (async function () {
      try {
        var res = await fetch(base, { method: "GET" });
        if (!res.ok) {
          if (aiVisualStockEmpty) aiVisualStockEmpty.classList.remove("hidden");
          return;
        }
        if (aiVisualStockEmpty) aiVisualStockEmpty.classList.add("hidden");
        if (aiVisualStockImg) {
          aiVisualStockImg.classList.remove("hidden");
          aiVisualStockImg.alt = aiVisualStockTitle ? aiVisualStockTitle.textContent : "AI 配图";
          aiVisualStockImg.src = url;
        }
        if (btnAiVisualStockDownload) btnAiVisualStockDownload.disabled = false;
      } catch (_) {
        if (aiVisualStockEmpty) aiVisualStockEmpty.classList.remove("hidden");
      }
    })();
  }

  async function downloadAiVisualStockImage() {
    if (!currentTaskId || !btnAiVisualStockDownload || btnAiVisualStockDownload.disabled) return;
    var base =
      "/api/tasks/" +
      encodeURIComponent(currentTaskId) +
      "/slide/" +
      selectedIndex +
      "/generated-visual";
    var name = "slide-" + String(selectedIndex + 1).padStart(4, "0") + "-ai-remake.png";
    var origLabel = "下载本图";
    btnAiVisualStockDownload.disabled = true;
    btnAiVisualStockDownload.textContent = "下载中…";
    try {
      var res = await fetch(base);
      if (!res.ok) throw new Error("fetch failed");
      var blob = await res.blob();
      var cd = res.headers.get("Content-Disposition");
      if (cd) {
        var m = /filename\*=UTF-8''([^;\s]+)|filename="([^"]+)"/i.exec(cd);
        var raw = m ? m[1] || m[2] : "";
        if (raw) {
          try {
            name = decodeURIComponent(raw.replace(/"/g, "").trim());
          } catch (_) {
            name = raw.replace(/"/g, "").trim();
          }
        }
      }
      var url = URL.createObjectURL(blob);
      var a = document.createElement("a");
      a.href = url;
      a.download = name || "ai-remake.png";
      a.rel = "noopener";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (_) {
      window.open(base, "_blank", "noopener,noreferrer");
    } finally {
      btnAiVisualStockDownload.disabled = false;
      btnAiVisualStockDownload.textContent = origLabel;
    }
  }

  /** 与服务端 ``build_slide_visual_prompt`` 对齐，便于用户在确认框内预览默认提示词 */
  function buildDefaultVisualPrompt(slide) {
    var title = slide && slide.title ? String(slide.title).trim() : "";
    var text = slide && slide.text ? String(slide.text).trim().replace(/\r\n/g, "\n") : "";
    if (text.length > 1200) text = text.slice(0, 1200) + "…";
    var parts = [
      "生成一张 16:9 横版教学课件配图，风格清晰专业、适合中文在线课程，配色稳重，避免低俗或与课件无关的装饰。",
      "画面中可适当包含简洁图示或排版感，但不要生成密密麻麻的小字正文。",
    ];
    if (title) parts.push("本页主题标题：" + title);
    if (text) parts.push("内容要点摘录（供理解语境）：\n" + text);
    var raw = parts.join("\n");
    if (raw.length > 4000) return raw.slice(0, 3999) + "…";
    return raw;
  }

  function resetGenerateVisualDialogToForm() {
    if (gvPanelForm) gvPanelForm.classList.remove("hidden");
    if (gvPanelResult) gvPanelResult.classList.add("hidden");
    if (gvFooterConfirm) gvFooterConfirm.classList.remove("hidden");
    if (gvFooterResult) gvFooterResult.classList.add("hidden");
    if (gvError) {
      gvError.classList.add("hidden");
      gvError.textContent = "";
    }
    if (gvResultImg) {
      gvResultImg.removeAttribute("src");
    }
    if (gvResultPathText) gvResultPathText.textContent = "";
  }

  function openGenerateVisualDialog() {
    if (!generateVisualDialog || !currentTaskId || !slides.length) return;
    resetGenerateVisualDialogToForm();
    var si = selectedIndex;
    var sid = String(si + 1).padStart(4, "0");
    if (gvStorageHint) {
      gvStorageHint.textContent =
        "tasks/" +
        currentTaskId +
        "/generated_visuals/slide-" +
        sid +
        "/<时间戳>-<模型简写>.png";
    }
    var s = slides[si] || {};
    if (gvSlideLabel) {
      gvSlideLabel.textContent =
        "第 " + (si + 1) + " / " + slides.length + " 页 · " + slideSnippetText(s);
    }
    if (gvModel) gvModel.value = "gpt-image-2";
    if (gvSize) gvSize.value = "1792x1024";
    if (gvPrompt) gvPrompt.value = buildDefaultVisualPrompt(s);
    if (gvOpenNewTab) gvOpenNewTab.checked = true;
    if (btnGvSubmit) {
      btnGvSubmit.disabled = false;
      btnGvSubmit.textContent = "确认生成（消耗额度）";
    }
    generateVisualDialog.showModal();
  }

  function closeGenerateVisualDialog() {
    if (generateVisualDialog && generateVisualDialog.open) generateVisualDialog.close();
    resetGenerateVisualDialogToForm();
  }

  async function submitGenerateVisualFromDialog() {
    if (!currentTaskId || !btnGvSubmit) return;
    if (gvError) {
      gvError.classList.add("hidden");
      gvError.textContent = "";
    }
    var model = gvModel ? gvModel.value.trim() : "gpt-image-2";
    var size = gvSize ? gvSize.value : "1792x1024";
    var promptVal = gvPrompt ? gvPrompt.value.trim() : "";
    var body = { model: model || "gpt-image-2", size: size || "1792x1024" };
    if (promptVal) body.prompt = promptVal;

    btnGvSubmit.disabled = true;
    var prevSubmitText = btnGvSubmit.textContent;
    btnGvSubmit.textContent = "正在请求网关…";
    try {
      var res = await fetch(
        "/api/tasks/" +
          encodeURIComponent(currentTaskId) +
          "/slide/" +
          selectedIndex +
          "/generate-visual",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        }
      );
      var j = {};
      try {
        j = await res.json();
      } catch (_) {}
      if (!res.ok) {
        var det = j.detail;
        var errMsg =
          typeof det === "string"
            ? det
            : det && typeof det === "object"
              ? JSON.stringify(det)
              : "生成失败（HTTP " + res.status + "）";
        throw new Error(errMsg);
      }

      if (gvPanelForm) gvPanelForm.classList.add("hidden");
      if (gvFooterConfirm) gvFooterConfirm.classList.add("hidden");
      if (gvPanelResult) gvPanelResult.classList.remove("hidden");
      if (gvFooterResult) gvFooterResult.classList.remove("hidden");
      var pathTxt = j.path_under_course_data || "—";
      if (gvResultPathText) {
        gvResultPathText.textContent = "已保存（相对课件数据根）：" + pathTxt;
      }
      var pu = j.preview_url || "";
      if (gvResultImg && pu) {
        gvResultImg.src = pu + "?t=" + Date.now();
      }
      if (gvOpenNewTab && gvOpenNewTab.checked && pu) {
        window.open(pu + "?t=" + Date.now(), "_blank", "noopener,noreferrer");
      }
      if (statusLine) {
        statusLine.textContent =
          "AI 配图已生成：" + pathTxt + (gvOpenNewTab && gvOpenNewTab.checked ? " · 已打开新标签预览" : " · 见上方对话框内预览");
      }
      await refreshGenVisualCoverage();
      void updatePreviewMedia();
    } catch (e) {
      var msg = e instanceof Error ? e.message : String(e);
      if (gvError) {
        gvError.textContent = msg;
        gvError.classList.remove("hidden");
      }
      if (statusLine) statusLine.textContent = "文生图失败：" + msg;
    } finally {
      btnGvSubmit.disabled = false;
      btnGvSubmit.textContent = prevSubmitText;
    }
  }

  async function openStoredTask(taskId) {
    try {
      var res = await fetch("/api/tasks/" + encodeURIComponent(taskId));
      if (!res.ok) return;
      var data = await res.json();
      previewMode = "stored";
      slides = data.slides || [];
      selectedIndex = 0;
      currentTaskId = taskId;
      sessionId = null;
      currentFile = null;
      imagesAvailable = !!data.images_available;
      previewCount = typeof data.preview_count === "number" ? data.preview_count : 0;
      previewSource = data.preview_source === "placeholder" ? "placeholder" : "libreoffice";
      audioTranscripts = slides.map(function () {
        return "";
      });
      audioTranscriptSegments = slides.map(function () {
        return [""];
      });
      fileLabel.textContent = (data.filename || "已存任务") + " · 已存任务";
      if (imagesAvailable) {
        imagesBanner.classList.add("hidden");
        imagesBanner.textContent = "";
      } else {
        imagesBanner.textContent =
          data.images_error ||
          "未生成 PNG 预览：请在本机安装 LibreOffice 与 Poppler（pdftoppm），并重启 Web 服务。";
        imagesBanner.classList.remove("hidden");
      }
      uploadPanel.classList.add("hidden");
      workspace.classList.remove("hidden");
      if (appMain) appMain.classList.add("app-main--workspace");
      if (slideRail) slideRail.classList.remove("hidden");
      setWorkspaceTaskDrawerTabVisible(true);
      await refreshGenVisualCoverage();
      renderSlideList();
      renderPreview();
      await loadAudioWorkspaceMeta();
      var msg =
        "已打开已存任务（" +
        slides.length +
        " 页）。左侧为缩略图列表，可滚动选择页面。";
      if (!imagesAvailable) {
        msg += " 当前仅显示解析文本。";
      }
      statusLine.textContent = msg;
      setImportTranscriptButtonVisible();
      refreshGenerateSlideVisualEnabled();
      void refreshDirectorManifest(true);
      void refreshRemotionStatus(true);
      void refreshWorkspaceStatus(true);
    } catch (_) {}
  }

  function setImportTranscriptButtonVisible() {
    if (!btnImportTranscript) return;
    if (currentTaskId) {
      btnImportTranscript.classList.remove("hidden");
    } else {
      btnImportTranscript.classList.add("hidden");
    }
  }

  function escapeHtmlText(s) {
    if (s == null || s === "") return "";
    var d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  function renderDirectorManifest(dm) {
    directorManifestCache = dm;
    if (directorSummary) {
      var course = (dm && dm.course) || {};
      var assets = (dm && dm.assets) || [];
      var scenes = (dm && dm.scenes) || [];
      var generation = (dm && dm.generation) || {};
      var llmError = generation.llm_error || "";
      var outline = (dm && dm.course_outline) || [];
      var checks = (dm && dm.quality_checks) || {};
      directorSummary.innerHTML =
        '<div class="director-panel__summary-inner">' +
        "<p><strong>课程标题</strong>：" +
        escapeHtmlText(course.title || "—") +
        "</p>" +
        "<p><strong>课程目标</strong>：" +
        escapeHtmlText(course.goal || "—") +
        "</p>" +
        "<p><strong>素材数量</strong>：" +
        assets.length +
        "　<strong>镜头数量</strong>：" +
        scenes.length +
        "　<strong>大纲项</strong>：" +
        outline.length +
        "</p>" +
        "<p><strong>质量检查</strong>：" +
        escapeHtmlText(
          (checks.error_count || 0) +
            " 个错误，" +
            (checks.warning_count || 0) +
            " 个提醒"
        ) +
        "</p>" +
        "<p><strong>规划模式</strong>：" +
        escapeHtmlText(generation.planning_mode || "—") +
        (generation.llm_model ? "　<strong>模型</strong>：" + escapeHtmlText(generation.llm_model) : "") +
        "</p>" +
        (llmError
          ? "<p><strong>LLM 回退原因</strong>：" + escapeHtmlText(llmError) + "</p>"
          : "") +
        "</div>";
    }
    if (!directorScenes) return;
    var list = (dm && dm.scenes) || [];
    if (!list.length) {
      directorScenes.innerHTML =
        '<p class="director-panel__empty">暂无镜头。请先生成课程化导演脚本。</p>';
      return;
    }
    var buf = [];
    for (var i = 0; i < list.length; i++) {
      var sc = list[i];
      var sd = sc.screen_design || {};
      var vs = sd.visual_strategy || "";
      var layout = sd.layout || (sc.render_intent && sc.render_intent.layout) || "";
      var rf = (sc.risk_flags || []).join("、");
      var ev = (sc.source_evidence || [])
        .map(function (item) {
          return (item && item.slide_id ? item.slide_id + "：" : "") + ((item && item.quote) || "");
        })
        .filter(Boolean)
        .join("\n");
      buf.push(
        '<article class="director-scene-card" data-scene-id="' +
          escapeHtmlText(sc.scene_id || "") +
          '">' +
          '<header class="director-scene-card__head">' +
          '<span class="director-scene-card__id">' +
          escapeHtmlText(sc.scene_id || "") +
          "</span>" +
          '<span class="director-scene-card__type">' +
          escapeHtmlText(sc.scene_type || "") +
          "</span>" +
          '<span class="director-scene-card__review">' +
          escapeHtmlText(sc.review_status || "") +
          "</span>" +
          "</header>" +
          "<p><strong>标题</strong>：" +
          escapeHtmlText(sc.title || "") +
          "</p>" +
          "<p><strong>来源页</strong>：" +
          escapeHtmlText(JSON.stringify(sc.source_slide_ids || [])) +
          "</p>" +
          "<p><strong>学习目标</strong>：" +
          escapeHtmlText(sc.learning_goal || "") +
          "</p>" +
          '<pre class="director-scene-card__block">' +
          escapeHtmlText(sc.onscreen_text || "") +
          "</pre>" +
          '<pre class="director-scene-card__block">' +
          escapeHtmlText(sc.narration || "") +
          "</pre>" +
          '<pre class="director-scene-card__block">' +
          escapeHtmlText(sc.tts_text || "") +
          "</pre>" +
          '<pre class="director-scene-card__block">' +
          escapeHtmlText(sc.subtitle_text || "") +
          "</pre>" +
          "<p><strong>画面策略</strong>：" +
          escapeHtmlText((layout ? layout + " · " : "") + vs) +
          "</p>" +
          "<p><strong>风险标记</strong>：" +
          escapeHtmlText(rf || "—") +
          "</p>" +
          (ev
            ? "<p><strong>原文证据</strong></p>" +
              '<pre class="director-scene-card__block">' +
              escapeHtmlText(ev) +
              "</pre>"
            : "") +
          '<div class="director-scene-card__actions">' +
          '<button type="button" class="btn btn-text director-scene-approve">审核通过</button>' +
          '<button type="button" class="btn btn-text director-scene-reject">驳回</button>' +
          "</div>" +
          "</article>"
      );
    }
    directorScenes.innerHTML = buf.join("");
  }

  async function refreshDirectorManifest(silent) {
    if (!currentTaskId) {
      if (directorSummary) {
        directorSummary.innerHTML =
          '<p class="director-panel__empty">需任务已持久化（解析返回 task_id，或从已存任务打开）。</p>';
      }
      if (directorScenes) directorScenes.innerHTML = "";
      directorManifestCache = null;
      return;
    }
    try {
      var res = await fetch(
        "/api/tasks/" + encodeURIComponent(currentTaskId) + "/director-manifest"
      );
      if (res.status === 404) {
        if (!silent && statusLine) {
          statusLine.textContent = "尚未生成导演脚本，可先点击「生成课程化导演脚本」。";
        }
        if (directorSummary) {
          directorSummary.innerHTML =
            '<p class="director-panel__empty">尚未生成导演脚本。</p>';
        }
        if (directorScenes) directorScenes.innerHTML = "";
        directorManifestCache = null;
        return;
      }
      if (!res.ok) throw new Error("HTTP " + res.status);
      var dm = await res.json();
      renderDirectorManifest(dm);
    } catch (e) {
      if (!silent && statusLine) {
        statusLine.textContent =
          "刷新导演脚本失败：" + (e instanceof Error ? e.message : String(e));
      }
    }
  }

  async function postDirectorRawManifest() {
    if (!currentTaskId) return;
    try {
      if (btnDirectorRawManifest) btnDirectorRawManifest.disabled = true;
      var res = await fetch(
        "/api/tasks/" + encodeURIComponent(currentTaskId) + "/raw-material-manifest",
        { method: "POST" }
      );
      var j = await res.json().catch(function () {
        return {};
      });
      if (!res.ok) throw new Error(j.detail || "请求失败");
      if (statusLine) {
        statusLine.textContent =
          "已生成 raw_material_manifest.json（" +
          (j.slide_count || 0) +
          " 页，" +
          (j.shapes_total || 0) +
          " 个 shape 素材）。";
      }
    } catch (e) {
      if (statusLine) {
        statusLine.textContent =
          "生成原始素材清单失败：" + (e instanceof Error ? e.message : String(e));
      }
    } finally {
      if (btnDirectorRawManifest) btnDirectorRawManifest.disabled = false;
    }
  }

  async function postDirectorRebuild() {
    if (!currentTaskId) return;
    try {
      if (btnDirectorRebuild) btnDirectorRebuild.disabled = true;
      var res = await fetch(
        "/api/tasks/" + encodeURIComponent(currentTaskId) + "/rebuild-course",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ use_llm: true }),
        }
      );
      var j = await res.json().catch(function () {
        return {};
      });
      if (!res.ok) throw new Error(j.detail || "请求失败");
      if (statusLine) {
        statusLine.textContent =
          "已生成导演脚本：镜头 " +
          (j.scene_count || 0) +
          "，素材 " +
          (j.asset_count || 0) +
          "；规划模式 " +
          (j.planning_mode || "unknown") +
          (j.llm_error ? "（已回退）" : "") +
          "。";
      }
      await refreshDirectorManifest(true);
      void refreshWorkspaceStatus(true);
    } catch (e) {
      if (statusLine) {
        statusLine.textContent =
          "生成导演脚本失败：" + (e instanceof Error ? e.message : String(e));
      }
    } finally {
      if (btnDirectorRebuild) btnDirectorRebuild.disabled = false;
    }
  }

  async function postDirectorExport() {
    if (!currentTaskId) return;
    try {
      if (btnDirectorExport) btnDirectorExport.disabled = true;
      var res = await fetch(
        "/api/tasks/" +
          encodeURIComponent(currentTaskId) +
          "/export-approved-director-manifest",
        { method: "POST" }
      );
      var j = await res.json().catch(function () {
        return {};
      });
      if (!res.ok) throw new Error(j.detail || "请求失败");
      if (statusLine) {
        statusLine.textContent =
          "已导出 approved_director_manifest.json（审核通过 " +
          (j.approved_scene_count || 0) +
          " 条，驳回项 " +
          (j.rejected_item_count || 0) +
          "）。";
      }
    } catch (e) {
      if (statusLine) {
        statusLine.textContent =
          "导出失败：" + (e instanceof Error ? e.message : String(e));
      }
    } finally {
      if (btnDirectorExport) btnDirectorExport.disabled = false;
    }
  }

  async function directorApproveScene(sceneId) {
    if (!currentTaskId || !sceneId) return;
    try {
      var res = await fetch(
        "/api/tasks/" +
          encodeURIComponent(currentTaskId) +
          "/approve-scene/" +
          encodeURIComponent(sceneId),
        { method: "POST" }
      );
      var j = await res.json().catch(function () {
        return {};
      });
      if (!res.ok) throw new Error(j.detail || "请求失败");
      if (statusLine) statusLine.textContent = "镜头 " + sceneId + " 已标记为审核通过。";
      await refreshDirectorManifest(true);
      void refreshWorkspaceStatus(true);
    } catch (e) {
      if (statusLine) {
        statusLine.textContent =
          "审核失败：" + (e instanceof Error ? e.message : String(e));
      }
    }
  }

  async function directorRejectScene(sceneId) {
    if (!currentTaskId || !sceneId) return;
    var reason = window.prompt("驳回原因（可留空）", "");
    if (reason === null) return;
    try {
      var res = await fetch(
        "/api/tasks/" +
          encodeURIComponent(currentTaskId) +
          "/reject-scene/" +
          encodeURIComponent(sceneId),
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ reason: reason || "" }),
        }
      );
      var j = await res.json().catch(function () {
        return {};
      });
      if (!res.ok) throw new Error(j.detail || "请求失败");
      if (statusLine) statusLine.textContent = "镜头 " + sceneId + " 已驳回。";
      await refreshDirectorManifest(true);
      void refreshWorkspaceStatus(true);
    } catch (e) {
      if (statusLine) {
        statusLine.textContent =
          "驳回失败：" + (e instanceof Error ? e.message : String(e));
      }
    }
  }

  function renderRemotionStatus(data) {
    if (!remotionSummary) return;
    if (!currentTaskId) {
      remotionSummary.innerHTML =
        '<p class="remotion-panel__empty">需任务已持久化后才能生成 Remotion 渲染任务。</p>';
      if (remotionCommand) {
        remotionCommand.classList.add("hidden");
        remotionCommand.textContent = "";
      }
      return;
    }
    var inputReady = Boolean(data && data.input_props_exists);
    var outputReady = Boolean(data && data.output_video_exists);
    var missing = (data && data.missing_audio_slide_indexes) || [];
    var missingText = missing.length
      ? "缺音频页：" + missing.map(function (i) { return i + 1; }).join("、")
      : "所有导出页均有音频";
    remotionSummary.innerHTML =
      '<div class="remotion-panel__summary-inner">' +
      "<p><strong>入参</strong>：" +
      (inputReady ? "已生成" : "未生成") +
      "</p>" +
      "<p><strong>成片</strong>：" +
      (outputReady ? "已存在" : "未检测到") +
      "</p>" +
      "<p><strong>页数</strong>：" +
      escapeHtmlText((data && data.slide_count) || "—") +
      "　<strong>总帧数</strong>：" +
      escapeHtmlText((data && data.total_frames) || "—") +
      "　<strong>时长</strong>：" +
      escapeHtmlText((data && data.duration_sec) || "—") +
      " 秒</p>" +
      "<p><strong>音频覆盖</strong>：" +
      escapeHtmlText(missingText) +
      "</p>" +
      "<p><strong>Render Plan</strong>：" +
      escapeHtmlText(
        data && data.render_plan_exists
          ? (data.render_plan_source || "director") + " · " + (data.render_plan_path || "")
          : "未生成"
      ) +
      "</p>" +
      "<p><strong>input-props</strong>：" +
      escapeHtmlText((data && data.input_props_path) || "—") +
      "</p>" +
      "<p><strong>输出文件</strong>：" +
      escapeHtmlText((data && data.output_video_path) || "—") +
      "</p>" +
      "</div>";
    if (remotionCommand) {
      var cmd = (data && data.render_command) || "";
      remotionCommand.textContent = cmd;
      remotionCommand.classList.toggle("hidden", !cmd);
    }
  }

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

  function renderWorkspaceStatus(data) {
    if (taskWorkflowTitle) {
      taskWorkflowTitle.textContent =
        data && data.filename ? data.filename : currentTaskId ? "已存任务" : "任务流";
    }
    if (!taskWorkflowSteps) return;
    if (!currentTaskId || !data) {
      taskWorkflowSteps.innerHTML =
        '<p class="task-workflow__empty">打开已存任务后显示 Deal / Rebuilder / Remotion 状态。</p>';
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
        "Deal 素材",
        dealState,
        (data.slide_count || 0) + " 页，预览 " + (deal.preview_count || 0) + " 页",
        "preview-surface",
      ) +
      workflowStep(
        "Rebuilder 导演",
        directorState,
        rebuilder.director_manifest_exists
          ? (rebuilder.scene_count || 0) + " 镜头 · " + (rebuilder.planning_mode || "unknown")
          : rebuilder.course_material_exists
            ? "已有 course_material，待生成导演脚本"
            : rebuilder.raw_manifest_exists
              ? "已有 raw manifest，待规范化素材"
            : "待生成素材清单",
        "director-panel",
      ) +
      workflowStep(
        "Audio 口播",
        audioState,
        (audio.slides_with_audio || 0) + " 页已有音频，" + (audio.generated_segment_count || 0) + " 段",
        "audio-workbench",
      ) +
      workflowStep(
        "Remotion 成片",
        remotionState,
        remotion.output_video_exists
          ? "已检测到 MP4"
          : remotion.input_props_exists
            ? (remotion.render_plan_source || "入参已生成") + "，待渲染"
            : "待生成 input-props",
        "remotion-panel",
      );
  }

  async function refreshWorkspaceStatus(silent) {
    if (!currentTaskId) {
      renderWorkspaceStatus(null);
      return;
    }
    try {
      var res = await fetch(
        "/api/tasks/" + encodeURIComponent(currentTaskId) + "/workspace-status"
      );
      var j = await res.json().catch(function () {
        return {};
      });
      if (!res.ok) throw new Error(j.detail || "请求失败");
      renderWorkspaceStatus(j);
    } catch (e) {
      if (!silent && statusLine) {
        statusLine.textContent =
          "刷新任务流状态失败：" + (e instanceof Error ? e.message : String(e));
      }
      renderWorkspaceStatus(null);
    }
  }

  async function refreshRemotionStatus(silent) {
    if (!currentTaskId) {
      renderRemotionStatus(null);
      return;
    }
    try {
      var res = await fetch(
        "/api/tasks/" + encodeURIComponent(currentTaskId) + "/remotion-render-task"
      );
      var j = await res.json().catch(function () {
        return {};
      });
      if (!res.ok) throw new Error(j.detail || "请求失败");
      renderRemotionStatus(j);
    } catch (e) {
      if (!silent && statusLine) {
        statusLine.textContent =
          "刷新 Remotion 状态失败：" + (e instanceof Error ? e.message : String(e));
      }
      renderRemotionStatus(null);
    }
  }

  async function postRemotionRenderTask() {
    if (!currentTaskId) return;
    try {
      if (btnRemotionGenerate) btnRemotionGenerate.disabled = true;
      var res = await fetch(
        "/api/tasks/" + encodeURIComponent(currentTaskId) + "/remotion-render-plan",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            fps: 30,
            no_audio_frames: 90,
            bundle_audio: false,
          }),
        }
      );
      var j = await res.json().catch(function () {
        return {};
      });
      if (!res.ok) throw new Error(j.detail || "请求失败");
      renderRemotionStatus(j);
      void refreshWorkspaceStatus(true);
      if (statusLine) {
        statusLine.textContent =
          "已生成 Remotion 渲染任务：" +
          (j.slide_count || 0) +
          " 个镜头/页面，" +
          (j.audio_slide_count || 0) +
          " 项含音频。来源：" +
          (j.source || "fallback") +
          "。";
      }
    } catch (e) {
      if (statusLine) {
        statusLine.textContent =
          "生成 Remotion 渲染任务失败：" + (e instanceof Error ? e.message : String(e));
      }
    } finally {
      if (btnRemotionGenerate) btnRemotionGenerate.disabled = false;
    }
  }

  function resetImportTranscriptDialog() {
    pendingImportPreview = null;
    if (importTranscriptTextarea) importTranscriptTextarea.value = "";
    if (importTranscriptFile) importTranscriptFile.value = "";
    if (importTranscriptStep1) importTranscriptStep1.classList.remove("hidden");
    if (importTranscriptStep2) importTranscriptStep2.classList.add("hidden");
    if (importTranscriptFooterRow1) importTranscriptFooterRow1.classList.remove("hidden");
    if (importTranscriptFooterRow2) importTranscriptFooterRow2.classList.add("hidden");
    if (importTranscriptWarnings) importTranscriptWarnings.innerHTML = "";
    if (importTranscriptConflictsList) importTranscriptConflictsList.innerHTML = "";
    if (importTranscriptConflictsWrap) importTranscriptConflictsWrap.classList.add("hidden");
  }

  function showImportTranscriptStep2() {
    if (importTranscriptStep1) importTranscriptStep1.classList.add("hidden");
    if (importTranscriptStep2) importTranscriptStep2.classList.remove("hidden");
    if (importTranscriptFooterRow1) importTranscriptFooterRow1.classList.add("hidden");
    if (importTranscriptFooterRow2) importTranscriptFooterRow2.classList.remove("hidden");
  }

  function showImportTranscriptStep1() {
    if (importTranscriptStep1) importTranscriptStep1.classList.remove("hidden");
    if (importTranscriptStep2) importTranscriptStep2.classList.add("hidden");
    if (importTranscriptFooterRow1) importTranscriptFooterRow1.classList.remove("hidden");
    if (importTranscriptFooterRow2) importTranscriptFooterRow2.classList.add("hidden");
  }

  async function runImportPreview() {
    if (!currentTaskId || !importTranscriptTextarea) return;
    var raw = importTranscriptTextarea.value || "";
    if (!raw.trim()) {
      alert("请先粘贴文稿或选择 .txt 文件。");
      return;
    }
    try {
      var res = await fetch("/api/audio/workspace/import-transcript/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task_id: currentTaskId, text: raw }),
      });
      var j = await res.json().catch(function () {
        return {};
      });
      if (!res.ok) {
        var detail =
          (j.detail && (typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail))) ||
          "解析失败";
        alert(detail);
        return;
      }
      pendingImportPreview = j;
      var slideCount = typeof j.slide_count === "number" ? j.slide_count : 0;
      var filled = typeof j.filled_slides === "number" ? j.filled_slides : 0;
      var conflicts = j.conflicts || [];
      var cc =
        typeof j.conflict_count === "number" ? j.conflict_count : conflicts.length;
      if (importTranscriptStep2Summary) {
        importTranscriptStep2Summary.textContent =
          "课件共 " +
          slideCount +
          " 页；文稿可写入其中 " +
          filled +
          " 页。" +
          (cc > 0
            ? " 有 " + cc + " 页与已有逐字稿冲突，请在下方逐页选择。"
            : " 无冲突，确认后将写入服务端。");
      }
      if (importTranscriptWarnings) {
        importTranscriptWarnings.innerHTML = "";
        var warns = j.warnings || [];
        if (warns.length) {
          warns.forEach(function (w) {
            var li = document.createElement("li");
            li.textContent = w;
            importTranscriptWarnings.appendChild(li);
          });
        }
      }
      if (importTranscriptConflictsWrap && importTranscriptConflictsList) {
        importTranscriptConflictsList.innerHTML = "";
        if (conflicts.length) {
          importTranscriptConflictsWrap.classList.remove("hidden");
          conflicts.forEach(function (c) {
            var si = c.slide_index;
            var card = document.createElement("div");
            card.className = "import-transcript-conflict-card";
            var title = document.createElement("p");
            title.className = "import-transcript-conflict-card__title";
            title.textContent =
              "第 " + (c.slide_page_number != null ? c.slide_page_number : si + 1) + " 页";
            card.appendChild(title);
            var exl = document.createElement("p");
            exl.style.fontSize = "0.78rem";
            exl.style.margin = "0.35rem 0 0.15rem";
            exl.style.color = "var(--muted)";
            exl.textContent = "当前已有";
            card.appendChild(exl);
            var preE = document.createElement("pre");
            preE.className = "import-transcript-conflict-card__pre";
            preE.innerHTML = escapeHtmlText(c.existing_preview || "");
            card.appendChild(preE);
            var iml = document.createElement("p");
            iml.style.fontSize = "0.78rem";
            iml.style.margin = "0.35rem 0 0.15rem";
            iml.style.color = "var(--muted)";
            iml.textContent = "导入稿";
            card.appendChild(iml);
            var preI = document.createElement("pre");
            preI.className = "import-transcript-conflict-card__pre";
            preI.innerHTML = escapeHtmlText(c.imported_preview || "");
            card.appendChild(preI);
            var ch = document.createElement("div");
            ch.className = "import-transcript-conflict-card__choices";
            ch.innerHTML =
              '<label><input type="radio" name="import-res-' +
              si +
              '" value="import" checked /> 采用导入稿</label>' +
              '<label><input type="radio" name="import-res-' +
              si +
              '" value="keep" /> 保留已有</label>';
            card.appendChild(ch);
            importTranscriptConflictsList.appendChild(card);
          });
        } else {
          importTranscriptConflictsWrap.classList.add("hidden");
        }
      }
      showImportTranscriptStep2();
    } catch (e) {
      alert("网络错误");
    }
  }

  async function runImportApply() {
    if (!currentTaskId || !importTranscriptTextarea || !pendingImportPreview) return;
    var raw = importTranscriptTextarea.value || "";
    var conflicts = pendingImportPreview.conflicts || [];
    var body = {
      task_id: currentTaskId,
      text: raw,
    };
    if (conflicts.length) {
      var resolutions = {};
      conflicts.forEach(function (c) {
        var si = c.slide_index;
        var inp = document.querySelector(
          'input[name="import-res-' + si + '"]:checked'
        );
        var v = inp && inp.value === "keep" ? "keep" : "import";
        resolutions[String(si)] = v;
      });
      body.resolutions = resolutions;
    }
    try {
      var res = await fetch("/api/audio/workspace/import-transcript/apply", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      var j = await res.json().catch(function () {
        return {};
      });
      if (!res.ok) {
        var detail =
          (j.detail && (typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail))) ||
          "写入失败";
        alert(detail);
        return;
      }
      if (importTranscriptDialog && importTranscriptDialog.open) importTranscriptDialog.close();
      resetImportTranscriptDialog();
      await loadAudioWorkspaceMeta();
      var ws = j.warnings || [];
      statusLine.textContent =
        "整稿逐字稿已写入。" + (ws.length ? "（解析过程含提示，请留意警告列表）" : "");
      if (audioSegmentsDialog && audioSegmentsDialog.open) {
        renderAudioSegmentRows();
      }
    } catch (e) {
      alert("网络错误");
    }
  }

  if (btnImportTranscript) {
    btnImportTranscript.addEventListener("click", function () {
      resetImportTranscriptDialog();
      showImportTranscriptStep1();
      if (importTranscriptDialog) importTranscriptDialog.showModal();
    });
  }
  if (btnImportTranscriptCancel) {
    btnImportTranscriptCancel.addEventListener("click", function () {
      if (importTranscriptDialog && importTranscriptDialog.open) importTranscriptDialog.close();
      resetImportTranscriptDialog();
    });
  }
  if (btnImportTranscriptPreview) {
    btnImportTranscriptPreview.addEventListener("click", function () {
      void runImportPreview();
    });
  }
  if (btnImportTranscriptBack) {
    btnImportTranscriptBack.addEventListener("click", function () {
      pendingImportPreview = null;
      showImportTranscriptStep1();
    });
  }
  if (btnImportTranscriptApply) {
    btnImportTranscriptApply.addEventListener("click", function () {
      void runImportApply();
    });
  }
  if (importTranscriptFile) {
    importTranscriptFile.addEventListener("change", function () {
      var f = importTranscriptFile.files && importTranscriptFile.files[0];
      if (!f || !importTranscriptTextarea) return;
      var r = new FileReader();
      r.onload = function () {
        importTranscriptTextarea.value = typeof r.result === "string" ? r.result : "";
      };
      r.readAsText(f, "UTF-8");
    });
  }
  if (importTranscriptDialog) {
    importTranscriptDialog.addEventListener("close", function () {
      resetImportTranscriptDialog();
      showImportTranscriptStep1();
    });
  }

  function thumbSrcForSlideIndex(i) {
    if (!imagesAvailable || i >= previewCount) return null;
    if (previewMode === "stored" && currentTaskId) return storedPreviewUrl(currentTaskId, i);
    if (previewMode === "session" && sessionId) return previewUrl(i);
    return null;
  }

  function mainPreviewImageSrc() {
    if (!imagesAvailable || selectedIndex >= previewCount) return null;
    if (previewMode === "stored" && currentTaskId) return storedPreviewUrl(currentTaskId, selectedIndex);
    if (previewMode === "session" && sessionId) return previewUrl(selectedIndex);
    return null;
  }

  function renderSlideList() {
    if (!slideList) return;
    slideList.innerHTML = "";
    slides.forEach(function (s, i) {
      var li = document.createElement("li");
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "slide-row" + (i === selectedIndex ? " active" : "");
      var snippet = slideSnippetText(s);

      var thumbSrc = thumbSrcForSlideIndex(i);
      var thumbHtml = "";
      if (thumbSrc) {
        thumbHtml =
          '<img class="slide-thumb" src="' +
          thumbSrc +
          '" alt="" loading="lazy" width="72" height="40" />';
      } else {
        thumbHtml = '<span class="slide-thumb slide-thumb--placeholder">' + (i + 1) + "</span>";
      }

      btn.innerHTML =
        thumbHtml +
        '<span class="slide-col"><span class="slide-idx">第 ' +
        (i + 1) +
        " / " +
        slides.length +
        ' 页</span><span class="slide-snippet">' +
        escapeHtml(snippet) +
        "</span></span>";

      btn.addEventListener("click", function () {
        flushAudioTranscript();
        selectedIndex = i;
        updateSelectionClasses();
        renderPreview();
      });
      li.appendChild(btn);
      slideList.appendChild(li);
    });
  }

  function updateSelectionClasses() {
    var buttons = slideList.querySelectorAll("button.slide-row");
    buttons.forEach(function (b, i) {
      if (i === selectedIndex) b.classList.add("active");
      else b.classList.remove("active");
    });
    var activeBtn = slideList.querySelector("button.slide-row.active");
    if (activeBtn) activeBtn.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }

  function escapeHtml(str) {
    const d = document.createElement("div");
    d.textContent = str;
    return d.innerHTML;
  }

  function syncPvCarouselChrome() {
    if (!pvCarousel || !pvCarouselState || !btnPvCarouselPrev || !btnPvCarouselNext) return;
    var n = pvCarouselFrames.length;
    if (n <= 1) {
      pvCarousel.classList.add("pv-carousel--single");
      btnPvCarouselPrev.disabled = true;
      btnPvCarouselNext.disabled = true;
    } else {
      pvCarousel.classList.remove("pv-carousel--single");
      btnPvCarouselPrev.disabled = pvCarouselIndex <= 0;
      btnPvCarouselNext.disabled = pvCarouselIndex >= n - 1;
    }
    var cur = pvCarouselFrames[pvCarouselIndex];
    if (n <= 1) {
      pvCarouselState.textContent = cur ? cur.caption : "";
    } else {
      pvCarouselState.textContent = cur ? cur.caption + " · " + (pvCarouselIndex + 1) + "/" + n : "";
    }
  }

  function applyPvCarouselFrame() {
    var cur = pvCarouselFrames[pvCarouselIndex];
    if (!cur || !pvImage) return;
    pvImage.onerror = function () {
      pvImage.alt = "预览图加载失败";
    };
    pvImage.src = cur.url;
    pvImage.onload = function () {
      pvImage.alt = cur.caption || "第 " + (selectedIndex + 1) + " 页";
    };
    syncPvCarouselChrome();
  }

  function buildPvPreviewDownloadFilename(frame) {
    var p = String(selectedIndex + 1).padStart(4, "0");
    if (frame && frame.kind === "shape" && frame.shapeIndex != null) {
      return (
        "slide-" + p + "-shape-" + String(frame.shapeIndex + 1).padStart(2, "0") + ".png"
      );
    }
    if (frame && frame.kind === "generated") {
      return "slide-" + p + "-ai-remake.png";
    }
    return "slide-" + p + "-full.png";
  }

  function openPvPreviewZoomDialog() {
    if (!pvPreviewZoomDialog || !pvPreviewZoomImg || !pvPreviewZoomTitle) return;
    var frame = pvCarouselFrames[pvCarouselIndex];
    if (!frame || !frame.url) return;
    pvPreviewZoomTitle.textContent =
      "第 " + (selectedIndex + 1) + " 页 · " + (frame.caption || "预览");
    pvPreviewZoomImg.alt = pvPreviewZoomTitle.textContent;
    pvPreviewZoomImg.src =
      frame.url + (frame.url.indexOf("?") >= 0 ? "&" : "?") + "zbust=" + Date.now();
    pvPreviewZoomDialog.showModal();
  }

  async function downloadPvPreviewZoomImage() {
    var frame = pvCarouselFrames[pvCarouselIndex];
    if (!frame || !frame.url || !btnPvPreviewZoomDownload) return;
    var origLabel = "下载本图";
    btnPvPreviewZoomDownload.disabled = true;
    btnPvPreviewZoomDownload.textContent = "下载中…";
    var name = buildPvPreviewDownloadFilename(frame);
    try {
      var res = await fetch(frame.url);
      if (!res.ok) throw new Error("fetch failed");
      var blob = await res.blob();
      var cd = res.headers.get("Content-Disposition");
      if (cd) {
        var m = /filename\*=UTF-8''([^;\s]+)|filename="([^"]+)"/i.exec(cd);
        var raw = m ? m[1] || m[2] : "";
        if (raw) {
          try {
            name = decodeURIComponent(raw.replace(/"/g, "").trim());
          } catch (_) {
            name = raw.replace(/"/g, "").trim();
          }
        }
      }
      var url = URL.createObjectURL(blob);
      var a = document.createElement("a");
      a.href = url;
      a.download = name || "preview.png";
      a.rel = "noopener";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (_) {
      window.open(frame.url, "_blank", "noopener,noreferrer");
    } finally {
      btnPvPreviewZoomDownload.disabled = false;
      btnPvPreviewZoomDownload.textContent = origLabel;
    }
  }

  function goPvCarousel(delta) {
    var n = pvCarouselFrames.length;
    if (n <= 1) return;
    pvCarouselIndex = Math.max(0, Math.min(n - 1, pvCarouselIndex + delta));
    applyPvCarouselFrame();
  }

  async function updatePreviewMedia() {
    if (!slides.length || !pvImageWrap) return;
    var req = ++pvMediaRequestId;
    var tid = currentTaskId || null;

    if (
      pvPreviewSourceMode === "ai" &&
      genVisualCoverage &&
      genVisualCoverage.all_slides_complete &&
      tid
    ) {
      var aiUrl =
        "/api/tasks/" +
        encodeURIComponent(tid) +
        "/slide/" +
        selectedIndex +
        "/generated-visual?t=" +
        Date.now();
      /** @type {Array<{ url: string, caption: string, kind: string, shapeIndex: number | null }>} */
      var framesAi = [
        {
          url: aiUrl,
          caption: "AI 重制",
          kind: "generated",
          shapeIndex: null,
        },
      ];
      if (req !== pvMediaRequestId) return;
      pvModeLabel.textContent = "AI 重制版预览（文生图）";
      currentPreviewHelpText =
        "每一页均已生成 AI 画面时可在此切换「原版」与「AI 重制版」。当前为文生图结果；「原版」为 LibreOffice 整页与页内切图。";
      pvCarouselFrames = framesAi;
      pvCarouselIndex = 0;
      pvImageWrap.classList.remove("hidden");
      applyPvCarouselFrame();
      return;
    }

    var fullSrc = mainPreviewImageSrc();
    var shapeCount = 0;
    if (tid) {
      try {
        var res = await fetch(
          "/api/tasks/" + encodeURIComponent(tid) + "/slide/" + selectedIndex + "/shapes",
        );
        if (res.ok) {
          var j = await res.json();
          shapeCount =
            typeof j.count === "number"
              ? j.count
              : j.filenames && j.filenames.length
                ? j.filenames.length
                : 0;
        }
      } catch (_) {}
    }
    if (req !== pvMediaRequestId) return;

    /** @type {Array<{ url: string, caption: string, kind: string, shapeIndex: number | null }>} */
    var frames = [];
    if (fullSrc) {
      frames.push({ url: fullSrc, caption: "整页", kind: "full", shapeIndex: null });
    }
    var si;
    if (tid && shapeCount > 0) {
      for (si = 0; si < shapeCount; si++) {
        frames.push({
          url:
            "/api/tasks/" +
            encodeURIComponent(tid) +
            "/slide/" +
            selectedIndex +
            "/shape/" +
            si,
          caption: "切图 " + (si + 1),
          kind: "shape",
          shapeIndex: si,
        });
      }
    }

    if (frames.length === 0) {
      pvImageWrap.classList.add("hidden");
      pvImage.removeAttribute("src");
      if (pvCarouselState) pvCarouselState.textContent = "";
      var hasPreviewBinding = previewMode === "stored" ? !!currentTaskId : !!sessionId;
      if (imagesAvailable && hasPreviewBinding && selectedIndex >= previewCount) {
        pvModeLabel.textContent = "本页暂无整页渲染图";
        currentPreviewHelpText =
          "渲染得到的 PNG 页数少于幻灯片页数，请仅参考下方文本；或检查 LibreOffice 导出是否完整。";
      } else {
        pvModeLabel.textContent = "文本解析预览（未生成整页渲染图）";
        currentPreviewHelpText =
          "无法生成整页预览图时仅显示抽取文本。若已安装 LibreOffice + Poppler 仍如此，请查看服务端日志。";
      }
      return;
    }

    var hasFull = !!fullSrc;
    var nShapes = shapeCount;

    if (hasFull && nShapes > 0) {
      if (previewSource === "placeholder") {
        pvModeLabel.textContent = "幻灯片预览（占位整页 · 可切换页内切图）";
        currentPreviewHelpText =
          "以下为 python-pptx 抽取的文本；整页图为服务端文本占位示意图。两侧箭头可切换到本页扣出的图片素材。安装 LibreOffice + Poppler 后可显示真实整页渲染图。";
      } else {
        pvModeLabel.textContent = "幻灯片预览（整页渲染 · 可切换页内切图）";
        currentPreviewHelpText =
          "以下为 python-pptx 抽取的文本。整页图为 LibreOffice 导出；页内切图为从文稿中抽出的内嵌图。使用两侧箭头可切换。";
      }
    } else if (hasFull) {
      if (previewSource === "placeholder") {
        pvModeLabel.textContent = "文本占位整页预览（Pillow 排版示意）";
        currentPreviewHelpText =
          "以下为 python-pptx 抽取的文本；上图由服务端根据文本生成的示意图，非像素级还原。安装 LibreOffice + Poppler 后可显示真实幻灯片渲染图。";
      } else {
        pvModeLabel.textContent = "幻灯片渲染图（服务端 LibreOffice → PNG）";
        currentPreviewHelpText =
          "以下为 python-pptx 抽取的文本，可与上图对照（复杂排版可能略有差异）。";
      }
    } else {
      pvModeLabel.textContent = "页内切图预览（本页无整页 PNG）";
      currentPreviewHelpText =
        "本页没有整页 PNG 时仍可显示从文稿中扣出的图片素材。解析文本见下方。";
    }

    if (
      frames.length > 1 &&
      currentPreviewHelpText.indexOf("箭头") === -1 &&
      currentPreviewHelpText.indexOf("切换") === -1
    ) {
      currentPreviewHelpText += " 使用两侧箭头在多条预览之间切换。点击图片可放大查看或下载。";
    } else if (frames.length > 0 && currentPreviewHelpText.indexOf("放大") === -1) {
      currentPreviewHelpText += " 点击图片可放大查看或下载。";
    }

    pvCarouselFrames = frames;
    pvCarouselIndex = 0;
    pvImageWrap.classList.remove("hidden");
    applyPvCarouselFrame();
  }

  function renderPreview() {
    if (!slides.length) return;
    const s = slides[selectedIndex];
    slideCounter.textContent =
      "第 " + (selectedIndex + 1) + " / " + slides.length + " 页";
    var metaParts = [];
    if (s.layout) metaParts.push("版式：" + s.layout);
    metaParts.push("形状内图 " + (s.image_count || 0));
    metaParts.push("表 " + (s.table_count || 0));
    slideMeta.textContent = metaParts.join(" · ");

    void updatePreviewMedia();

    pvTitle.textContent = s.title || "（无标题）";

    pvBlocks.innerHTML = "";
    var blocks =
      s.text_blocks && s.text_blocks.length
        ? s.text_blocks
        : [s.text || "（本页未识别到正文文本）"];
    blocks.forEach(function (line) {
      var div = document.createElement("div");
      div.className = "block";
      div.textContent = line;
      pvBlocks.appendChild(div);
    });

    if (s.notes) {
      pvNotes.textContent = s.notes;
      pvNotesWrap.classList.remove("hidden");
    } else {
      pvNotesWrap.classList.add("hidden");
    }

    refreshAudioWorkbench();
    updateAiVisualToolbarBtn();
  }

  function ensureAudioSegmentsShape() {
    if (!slides.length) return;
    while (audioTranscriptSegments.length < slides.length) {
      audioTranscriptSegments.push([""]);
    }
    if (audioTranscriptSegments.length > slides.length) {
      audioTranscriptSegments.length = slides.length;
    }
    for (var i = 0; i < slides.length; i++) {
      if (!audioTranscriptSegments[i] || !audioTranscriptSegments[i].length) {
        audioTranscriptSegments[i] = [""];
      }
    }
  }

  function syncAudioTranscriptsFromSegments() {
    ensureAudioSegmentsShape();
    while (audioTranscripts.length < slides.length) {
      audioTranscripts.push("");
    }
    audioTranscripts.length = slides.length;
    for (var i = 0; i < slides.length; i++) {
      var rows = audioTranscriptSegments[i] || [""];
      audioTranscripts[i] = rows.join("\n\n").trim();
    }
  }

  function flushAudioSegmentsFromDom() {
    var list = document.getElementById("audio-segments-list");
    if (!list || !slides.length) return;
    ensureAudioSegmentsShape();
    var si = selectedIndex;
    var textareas = list.querySelectorAll("[data-audio-seg-text]");
    if (!textareas.length) return;
    var next = [];
    textareas.forEach(function (ta) {
      next.push(ta.value);
    });
    if (next.length) {
      audioTranscriptSegments[si] = next;
    }
    syncAudioTranscriptsFromSegments();
  }

  /** 将第 segIdx 段写为 txt，并保证该页段数组足够长（与 pending* 解耦，供口播版本库等使用） */
  function setAudioTranscriptSegmentText(si, segIdx, txt) {
    ensureAudioSegmentsShape();
    if (!audioTranscriptSegments[si]) audioTranscriptSegments[si] = [""];
    while (audioTranscriptSegments[si].length <= segIdx) {
      audioTranscriptSegments[si].push("");
    }
    audioTranscriptSegments[si][segIdx] = txt;
    syncAudioTranscriptsFromSegments();
  }

  function flushAudioTranscript() {
    if (audioSegmentsDialog && audioSegmentsDialog.open) {
      flushAudioSegmentsFromDom();
    }
    if (!slides.length) return;
    syncAudioTranscriptsFromSegments();
  }

  /** 当前页是否存在至少一段已生成音频（用于主工作台试听条） */
  function getFirstGeneratedAudioUrlForCurrentSlide() {
    if (!audioWorkspaceKey || !slides.length) return null;
    var si = selectedIndex;
    ensureAudioSegmentsShape();
    var rows = audioTranscriptSegments[si] || [""];
    for (var j = 0; j < rows.length; j++) {
      var gk = segmentFileKey(si, j);
      var vs = audioSegmentVersions[gk];
      if (vs && vs.length) {
        return buildSegmentFileUrl(j);
      }
      if (audioGeneratedFiles[gk]) {
        return buildSegmentFileUrl(j);
      }
    }
    return null;
  }

  function updateAudioWorkbenchPlayer() {
    if (!audioPlayer) return;
    var u = getFirstGeneratedAudioUrlForCurrentSlide();
    if (u) {
      audioPlayer.classList.remove("hidden");
      audioPlayer.src = u + (u.indexOf("?") >= 0 ? "&" : "?") + "t=" + Date.now();
    } else {
      audioPlayer.classList.add("hidden");
      audioPlayer.removeAttribute("src");
      try {
        audioPlayer.load();
      } catch (_) {}
    }
  }

  function refreshAudioWorkbench() {
    if (!slides.length) return;
    syncAudioTranscriptsFromSegments();
    if (audioWorkbenchStatus) audioWorkbenchStatus.textContent = "";
    updateAudioWorkbenchPlayer();
    if (audioSegmentsDialog && audioSegmentsDialog.open) {
      renderAudioSegmentRows();
    }
  }

  function segmentFileKey(slideIdx, segIdx) {
    return String(slideIdx) + "-" + String(segIdx);
  }

  /** MP3 另存为默认文件名：当前段逐字稿前 10 个字（Unicode），再去除路径非法字符 */
  function mp3DownloadFilenameFromTranscript(text) {
    var raw = typeof text === "string" ? text : "";
    var chars = Array.from(raw.trim());
    var prefix = chars.slice(0, 10).join("");
    var safe = prefix
      .replace(/[\\/:*?"<>|]/g, "")
      .replace(/[\u0000-\u001f]/g, "")
      .trim();
    if (!safe) {
      safe = "audio";
    }
    if (!/\.mp3$/i.test(safe)) {
      safe = safe + ".mp3";
    }
    return safe;
  }

  var audioBlobDbPromise = null;
  function openAudioBlobDb() {
    if (!audioBlobDbPromise) {
      audioBlobDbPromise = new Promise(function (resolve, reject) {
        var req = indexedDB.open("ppt_course_audio_blobs", 1);
        req.onerror = function () {
          reject(req.error);
        };
        req.onsuccess = function () {
          resolve(req.result);
        };
        req.onupgradeneeded = function () {
          var db = req.result;
          if (!db.objectStoreNames.contains("blobs")) {
            db.createObjectStore("blobs", { keyPath: "key" });
          }
        };
      });
    }
    return audioBlobDbPromise;
  }

  function audioBlobCacheKey(slideIdx, segIdx, versionId) {
    var scope = currentTaskId || sessionId;
    if (!scope || !versionId) return null;
    return scope + "|" + segmentFileKey(slideIdx, segIdx) + "|" + String(versionId);
  }

  async function putAudioBlobCache(slideIdx, segIdx, versionId, blob, filename) {
    var k = audioBlobCacheKey(slideIdx, segIdx, versionId);
    if (!k || !blob) return;
    try {
      var db = await openAudioBlobDb();
      var tx = db.transaction("blobs", "readwrite");
      tx.objectStore("blobs").put({
        key: k,
        blob: blob,
        filename: filename || "audio.mp3",
      });
    } catch (_) {}
  }

  async function deleteAudioBlobCache(slideIdx, segIdx, versionId) {
    var k = audioBlobCacheKey(slideIdx, segIdx, versionId);
    if (!k) return;
    try {
      var db = await openAudioBlobDb();
      var tx = db.transaction("blobs", "readwrite");
      tx.objectStore("blobs").delete(k);
    } catch (_) {}
  }

  async function autoDownloadWorkspaceAudio(url, filename, slideIdx, segIdx, versionId) {
    if (!url || !versionId) return;
    try {
      var res = await fetch(url);
      if (!res.ok) return;
      var blob = await res.blob();
      var baseName =
        (filename && String(filename).split("/").pop()) ||
        (filename && String(filename).split("\\").pop()) ||
        "audio.mp3";
      var a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = baseName;
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(function () {
        try {
          URL.revokeObjectURL(a.href);
        } catch (_) {}
      }, 4000);
      await putAudioBlobCache(slideIdx, segIdx, versionId, blob, baseName);
    } catch (_) {}
  }

  /** 当前页各段已有时长之和（秒）；任一段无记录则为 null */
  function sumSlideAudioDuration(slideIdx) {
    var rows = audioTranscriptSegments[slideIdx] || [""];
    var t = 0;
    var any = false;
    for (var j = 0; j < rows.length; j++) {
      var v = audioSegmentDurations[segmentFileKey(slideIdx, j)];
      if (typeof v === "number" && v > 0) {
        t += v;
        any = true;
      }
    }
    return any ? t : null;
  }

  function buildSegmentFileUrl(segIdx, versionId) {
    if (!audioWorkspaceKey || !slides.length) return "";
    var params = new URLSearchParams();
    params.set("kind", audioWorkspaceKind);
    params.set("key", audioWorkspaceKey);
    params.set("slide_index", String(selectedIndex));
    params.set("segment_index", String(segIdx));
    if (versionId != null && String(versionId).trim() !== "") {
      params.set("version_id", String(versionId).trim());
    }
    return "/api/audio/workspace/file?" + params.toString();
  }

  function transcriptVersionsStorageKey(segIdx) {
    var scope = currentTaskId || sessionId;
    if (!scope) return null;
    return "ppt_tr_ver_v1_" + scope + "_" + selectedIndex + "_" + segIdx;
  }

  function loadTranscriptVersions(segIdx) {
    var k = transcriptVersionsStorageKey(segIdx);
    if (!k) return [];
    try {
      var raw = localStorage.getItem(k);
      if (!raw) return [];
      var arr = JSON.parse(raw);
      return Array.isArray(arr) ? arr : [];
    } catch (_) {
      return [];
    }
  }

  function saveTranscriptVersions(segIdx, versions) {
    var k = transcriptVersionsStorageKey(segIdx);
    if (!k) return;
    localStorage.setItem(k, JSON.stringify(versions.slice(-25)));
  }

  function removeTranscriptVersionById(segIdx, versionId) {
    var vid = String(versionId || "").trim();
    if (!vid) return;
    var v = loadTranscriptVersions(segIdx);
    var next = v.filter(function (x) {
      return String(x.id || "") !== vid;
    });
    if (next.length === v.length) return;
    saveTranscriptVersions(segIdx, next);
    renderTranscriptVersionsList(segIdx);
  }

  function pushTranscriptVersion(segIdx, text, meta) {
    var v = loadTranscriptVersions(segIdx);
    var entry = {
      id: "v_" + Date.now() + "_" + Math.random().toString(36).slice(2, 9),
      text: text,
      createdAt: new Date().toISOString(),
    };
    if (meta && typeof meta === "object") {
      var mh = meta.minimax_hints;
      if (mh && typeof mh === "object" && Object.keys(mh).length > 0) {
        entry.minimax_hints = mh;
      }
      var dn = meta.delivery_notes;
      if (dn != null && String(dn).trim() !== "") {
        entry.delivery_notes = String(dn).trim();
      }
    }
    v.push(entry);
    saveTranscriptVersions(segIdx, v);
  }

  function formatMinimaxHintsReadable(hints) {
    if (!hints || typeof hints !== "object") return "";
    var labels = {
      model: "合成模型",
      voice_id: "音色 voice_id",
      language_boost: "语言增强",
      speed: "语速",
      vol: "音量",
      pitch: "音高",
      emotion: "情绪",
    };
    var lines = [];
    Object.keys(labels).forEach(function (k) {
      if (hints[k] === undefined || hints[k] === null || hints[k] === "") return;
      lines.push(labels[k] + "：" + String(hints[k]));
    });
    return lines.join("\n");
  }

  /** 清空「MiniMax 合成参数建议」展示区与本轮缓存（每次开始改写前 / 请求失败时也应调用，避免沿用上一轮） */
  function clearTranscriptRewriteMinimaxSuggestionUi() {
    lastTranscriptRewriteMinimaxHints = null;
    lastTranscriptRewriteDeliveryNotes = null;
    var mmSec = document.getElementById("tr-rewrite-minimax-section");
    var mmPre = document.getElementById("tr-rewrite-minimax-hints");
    var mmNotes = document.getElementById("tr-rewrite-delivery-notes");
    var mmBtn = document.getElementById("btn-tr-rewrite-apply-minimax");
    if (mmSec) mmSec.classList.add("hidden");
    if (mmPre) mmPre.textContent = "";
    if (mmNotes) {
      mmNotes.textContent = "";
      mmNotes.classList.add("hidden");
    }
    if (mmBtn) mmBtn.disabled = true;
  }

  function resetTranscriptRewriteDialogUi() {
    var run = document.getElementById("btn-tr-rewrite-run");
    var adopt = document.getElementById("btn-tr-rewrite-adopt");
    var warn = document.getElementById("tr-rewrite-warnings");
    if (run) {
      run.disabled = false;
      run.textContent = "开始改写";
    }
    if (adopt) adopt.disabled = true;
    if (warn) {
      warn.textContent = "";
      warn.classList.add("hidden");
    }
    var res = document.getElementById("tr-rewrite-result");
    if (res) res.value = "";
    clearTranscriptRewriteMinimaxSuggestionUi();
  }

  function openTranscriptRewriteDialog(segIdx) {
    if (!transcriptRewriteDialog || !slides.length) return;
    if (!currentTaskId && !sessionId) {
      if (audioWorkbenchStatus) audioWorkbenchStatus.textContent = "缺少会话或任务标识";
      return;
    }
    flushAudioSegmentsFromDom();
    pendingRewriteSegmentIndex = segIdx;
    resetTranscriptRewriteDialogUi();
    var si = selectedIndex;
    var rows = audioTranscriptSegments[si] || [""];
    var orig = typeof rows[segIdx] === "string" ? rows[segIdx] : "";
    var oel = document.getElementById("tr-rewrite-original");
    if (oel) oel.value = orig;
    transcriptRewriteDialog.showModal();
  }

  /** 将版本库/API 返回的 hints 规范为可写入的最小对象（支持历史上误存的 JSON 字符串） */
  function coerceMinimaxHintsObject(hints) {
    if (hints == null) return null;
    var o = hints;
    if (typeof hints === "string") {
      try {
        o = JSON.parse(hints);
      } catch (_) {
        return null;
      }
    }
    if (!o || typeof o !== "object") return null;
    var keys = ["model", "voice_id", "language_boost", "speed", "vol", "pitch", "emotion"];
    var out = {};
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i];
      if (o[k] === undefined || o[k] === null) continue;
      if (k === "emotion") {
        var em = String(o[k]).trim().toLowerCase();
        if (!em) continue;
        out[k] = em;
        continue;
      }
      out[k] = o[k];
    }
    return Object.keys(out).length ? out : null;
  }

  /** 将口播优化 / 版本库卡片上的 minimax_hints 合并进本机「音频生成参数」（与确认生成弹窗同源） */
  function mergeMinimaxHintsIntoStoredOverrides(hints) {
    var coerced = coerceMinimaxHintsObject(hints);
    if (!coerced) return false;
    var cur = readStoredAudioGenOverrides();
    var merged = Object.assign({}, cur);
    var keys = ["model", "voice_id", "language_boost", "speed", "vol", "pitch", "emotion"];
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i];
      if (coerced[k] === undefined || coerced[k] === null) continue;
      if (k === "emotion" && String(coerced[k]).trim() === "") continue;
      merged[k] = coerced[k];
    }
    writeStoredAudioGenOverrides(merged);
    return true;
  }

  function applyTranscriptRewriteMinimaxHints() {
    var h = lastTranscriptRewriteMinimaxHints;
    if (!h || typeof h !== "object" || !Object.keys(h).length) return;
    pendingAudioConfirmMinimaxOverlay = coerceMinimaxHintsObject(h);
    mergeMinimaxHintsIntoStoredOverrides(h);
    if (audioWorkbenchStatus) {
      audioWorkbenchStatus.textContent = "已合并口播优化建议到本机「音频生成参数」";
    }
  }

  /** 口播优化请求附带的全课语境最大字符数（须小于服务端 Field max_length） */
  var TRANSCRIPT_REWRITE_CONTEXT_MAX_CHARS = 42000;

  /** 拼当前任务各页各段逐字稿，供模型统筹语气；与本段「待优化原文」区分 */
  function buildCourseTranscriptContextForRewrite() {
    if (!slides.length) return "";
    ensureAudioSegmentsShape();
    var parts = [];
    for (var si = 0; si < slides.length; si++) {
      var rows = audioTranscriptSegments[si] || [""];
      var segs = [];
      for (var j = 0; j < rows.length; j++) {
        var t = typeof rows[j] === "string" ? rows[j].trim() : "";
        segs.push("段 " + (j + 1) + "：" + (t || "（空）"));
      }
      parts.push("【第 " + (si + 1) + " 页】\n" + segs.join("\n\n"));
    }
    var s = parts.join("\n\n---\n\n");
    if (s.length > TRANSCRIPT_REWRITE_CONTEXT_MAX_CHARS) {
      s =
        s.slice(0, TRANSCRIPT_REWRITE_CONTEXT_MAX_CHARS - 120) +
        "\n\n……（全课语境过长已截断；请以已给出的页面把握整体基调）";
    }
    return s;
  }

  async function runTranscriptRewriteRequest() {
    var run = document.getElementById("btn-tr-rewrite-run");
    var adopt = document.getElementById("btn-tr-rewrite-adopt");
    var warn = document.getElementById("tr-rewrite-warnings");
    var resTa = document.getElementById("tr-rewrite-result");
    var origTa = document.getElementById("tr-rewrite-original");
    var text = origTa ? String(origTa.value || "").trim() : "";
    if (!text) {
      alert("原文为空");
      return;
    }
    var trProvInit = document.getElementById("cfg-tr-provider");
    if (trProvInit && trProvInit.value === "none") {
      try {
        await fillExternalSettingsForm();
      } catch (_) {}
    }
    if (run) {
      run.disabled = true;
      run.textContent = "改写中…";
    }
    if (adopt) adopt.disabled = true;
    if (warn) {
      warn.textContent = "";
      warn.classList.add("hidden");
    }
    clearTranscriptRewriteMinimaxSuggestionUi();
    if (resTa) resTa.value = "";
    try {
      var res = await fetch("/api/transcript/rewrite", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: text,
          transcript_rewrite: collectTranscriptRewritePayload(),
          course_transcript_context: buildCourseTranscriptContextForRewrite(),
          context_slide_index: selectedIndex,
          context_segment_index: pendingRewriteSegmentIndex,
        }),
      });
      var j = await res.json().catch(function () {
        return {};
      });
      if (!res.ok) {
        clearTranscriptRewriteMinimaxSuggestionUi();
        var detail = j.detail ? (typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail)) : "改写失败";
        alert(detail);
        return;
      }
      if (resTa) resTa.value = j.rewritten_text || "";
      if (adopt) adopt.disabled = !(j.rewritten_text && String(j.rewritten_text).trim());
      if (warn && j.sanitize_warnings && j.sanitize_warnings.length) {
        warn.textContent = j.sanitize_warnings.join("\n");
        warn.classList.remove("hidden");
      }
      var hints = j.minimax_hints;
      lastTranscriptRewriteMinimaxHints =
        hints && typeof hints === "object" ? hints : null;
      lastTranscriptRewriteDeliveryNotes =
        j.delivery_notes != null && String(j.delivery_notes).trim() !== ""
          ? String(j.delivery_notes).trim()
          : null;
      var mmSec = document.getElementById("tr-rewrite-minimax-section");
      var mmPre = document.getElementById("tr-rewrite-minimax-hints");
      var mmNotes = document.getElementById("tr-rewrite-delivery-notes");
      var mmBtn = document.getElementById("btn-tr-rewrite-apply-minimax");
      var hasHintFields =
        lastTranscriptRewriteMinimaxHints && Object.keys(lastTranscriptRewriteMinimaxHints).length > 0;
      var dn = j.delivery_notes != null ? String(j.delivery_notes).trim() : "";
      if (mmSec && mmPre && mmNotes && mmBtn) {
        if (hasHintFields || dn) {
          mmSec.classList.remove("hidden");
          var readableHints =
            hasHintFields && formatMinimaxHintsReadable(lastTranscriptRewriteMinimaxHints);
          mmPre.textContent = hasHintFields
            ? readableHints ||
              JSON.stringify(lastTranscriptRewriteMinimaxHints, null, 2)
            : "（无可自动写入的参数字段；若下方有说明，请手动在「音频生成参数」中调整。）";
          if (dn) {
            mmNotes.textContent = dn;
            mmNotes.classList.remove("hidden");
          } else {
            mmNotes.textContent = "";
            mmNotes.classList.add("hidden");
          }
          mmBtn.disabled = !hasHintFields;
        } else {
          mmSec.classList.add("hidden");
          mmPre.textContent = "";
          mmNotes.textContent = "";
          mmNotes.classList.add("hidden");
          mmBtn.disabled = true;
        }
      }
    } catch (_) {
      alert("改写请求失败（网络）");
    } finally {
      if (run) {
        run.disabled = false;
        run.textContent = "开始改写";
      }
    }
  }

  function adoptTranscriptRewriteFromDialog() {
    var resTa = document.getElementById("tr-rewrite-result");
    var chk = document.getElementById("tr-rewrite-save-version");
    var next = resTa ? String(resTa.value || "").trim() : "";
    if (!next) return;
    var segIdx = pendingRewriteSegmentIndex;
    if (transcriptRewriteDialog) transcriptRewriteDialog.close();
    flushAudioSegmentsFromDom();
    var si = selectedIndex;
    setAudioTranscriptSegmentText(si, segIdx, next);
    if (chk && chk.checked) {
      pushTranscriptVersion(segIdx, next, {
        minimax_hints: lastTranscriptRewriteMinimaxHints || undefined,
        delivery_notes: lastTranscriptRewriteDeliveryNotes || undefined,
      });
    }
    renderAudioSegmentRows();
  }

  function openTranscriptVersionsDialog(segIdx) {
    if (!transcriptRewriteVersionsDialog || !slides.length) return;
    if (!currentTaskId && !sessionId) {
      if (audioWorkbenchStatus) audioWorkbenchStatus.textContent = "缺少会话或任务标识";
      return;
    }
    pendingVersionsSegmentIndex = segIdx;
    var sub = document.getElementById("tr-versions-subtitle");
    if (sub)
      sub.textContent =
        "第 " + (selectedIndex + 1) + " 页 · 段 " + (segIdx + 1) + "（仅存本机浏览器）";
    renderTranscriptVersionsList(segIdx);
    transcriptRewriteVersionsDialog.showModal();
  }

  function snippetPreview(t, n) {
    var s = (t || "").replace(/\s+/g, " ").trim();
    if (s.length <= n) return s;
    return s.slice(0, n) + "…";
  }

  function renderTranscriptVersionsList(segIdx) {
    var list = document.getElementById("tr-versions-list");
    var empty = document.getElementById("tr-versions-empty");
    if (!list) return;
    list.innerHTML = "";
    var rows = loadTranscriptVersions(segIdx);
    var mig = false;
    rows.forEach(function (x) {
      if (!x.id) {
        x.id = "v_mig_" + Date.now() + "_" + Math.random().toString(36).slice(2, 10);
        mig = true;
      }
    });
    if (mig) saveTranscriptVersions(segIdx, rows);
    if (!rows.length) {
      if (empty) empty.classList.remove("hidden");
      return;
    }
    if (empty) empty.classList.add("hidden");
    rows
      .slice()
      .reverse()
      .forEach(function (row) {
        var card = document.createElement("div");
        card.className = "tr-version-card";
        var headRow = document.createElement("div");
        headRow.className = "tr-version-card__head";
        var meta = document.createElement("div");
        meta.className = "tr-version-card__meta";
        try {
          meta.textContent = new Date(row.createdAt).toLocaleString();
        } catch (_) {
          meta.textContent = row.createdAt || "";
        }
        var btnRmVer = document.createElement("button");
        btnRmVer.type = "button";
        btnRmVer.className = "btn btn-text tr-version-card__delete";
        btnRmVer.textContent = "删除";
        btnRmVer.setAttribute("aria-label", "从口播版本库删除此条");
        (function (vid) {
          btnRmVer.addEventListener("click", function () {
            if (!confirm("确定删除本条口播版本记录？（仅清除本机浏览器中的保存，不影响已生成的音频文件。）")) return;
            removeTranscriptVersionById(segIdx, vid);
          });
        })(row.id);
        headRow.appendChild(meta);
        headRow.appendChild(btnRmVer);
        var sn = document.createElement("div");
        sn.className = "tr-version-card__snippet";
        sn.textContent = snippetPreview(row.text, 220);
        var hasHints =
          row.minimax_hints &&
          typeof row.minimax_hints === "object" &&
          Object.keys(row.minimax_hints).length > 0;
        var hasNotes = row.delivery_notes && String(row.delivery_notes).trim() !== "";
        if (hasHints || hasNotes) {
          var hintWrap = document.createElement("div");
          hintWrap.className = "tr-version-card__hints";
          var hintTitle = document.createElement("div");
          hintTitle.className = "tr-version-card__hints-title";
          hintTitle.textContent = "AI 建议的合成参数（仅供参考，生成音频时仍可修改）";
          hintWrap.appendChild(hintTitle);
          if (hasHints) {
            var pre = document.createElement("pre");
            pre.className = "tr-version-card__hints-pre";
            var readable = formatMinimaxHintsReadable(row.minimax_hints);
            pre.textContent =
              readable ||
              JSON.stringify(row.minimax_hints, null, 2);
            hintWrap.appendChild(pre);
          }
          if (hasNotes) {
            var note = document.createElement("p");
            note.className = "tr-version-card__hints-note muted";
            note.textContent = String(row.delivery_notes).trim();
            hintWrap.appendChild(note);
          }
        }
        var act = document.createElement("div");
        act.className = "tr-version-card__actions";
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "btn btn-secondary";
        btn.textContent = "采用此版本";
        (function (txt, segIdxForRow, hints) {
          btn.addEventListener("click", function () {
            if (transcriptRewriteVersionsDialog) transcriptRewriteVersionsDialog.close();
            flushAudioSegmentsFromDom();
            var si = selectedIndex;
            setAudioTranscriptSegmentText(si, segIdxForRow, txt);
            var coercedHints = coerceMinimaxHintsObject(hints);
            pendingAudioConfirmMinimaxOverlay = coercedHints;
            if (mergeMinimaxHintsIntoStoredOverrides(hints)) {
              if (audioWorkbenchStatus) {
                audioWorkbenchStatus.textContent =
                  "已采用该版本逐字稿，并已合并其中的合成参数建议（语速/情绪等）到本机「音频生成参数」。生成前可在确认弹窗中再改。";
              }
            }
            renderAudioSegmentRows();
          });
        })(row.text, segIdx, row.minimax_hints);
        act.appendChild(btn);
        card.appendChild(headRow);
        card.appendChild(sn);
        if (hasHints || hasNotes) {
          card.appendChild(hintWrap);
        }
        card.appendChild(act);
        list.appendChild(card);
      });
  }

  function setAudioSegmentsDialogMode(listenOnly) {
    audioSegmentsDialogListenOnly = !!listenOnly;
    var dlg = audioSegmentsDialog;
    if (dlg) {
      dlg.classList.toggle("audio-segments-dialog--listen-only", audioSegmentsDialogListenOnly);
    }
    var titleEl = document.getElementById("audio-segments-title");
    if (titleEl) {
      titleEl.textContent = audioSegmentsDialogListenOnly
        ? "本页已生成音频"
        : "本页逐字稿与音频";
    }
    var addBtn = document.getElementById("btn-audio-segment-add");
    if (addBtn) addBtn.classList.toggle("hidden", audioSegmentsDialogListenOnly);
    var saveBtn = document.getElementById("btn-audio-segments-save");
    if (saveBtn && saveBtn.parentElement) {
      saveBtn.parentElement.classList.toggle("hidden", audioSegmentsDialogListenOnly);
    }
    var helpBtn = document.getElementById("btn-help-audio-segments");
    if (helpBtn) helpBtn.classList.toggle("hidden", audioSegmentsDialogListenOnly);
  }

  async function deleteSegmentAudioVersion(segIdx, versionId) {
    if (!versionId || (!currentTaskId && !sessionId)) return;
    if (!confirm("确定删除该条生成记录？将删除服务器上的音频文件，并清除本页面对应的本地缓存。")) return;
    var body = {
      slide_index: selectedIndex,
      segment_index: segIdx,
      version_id: String(versionId),
    };
    if (currentTaskId) body.task_id = currentTaskId;
    else body.session_id = sessionId;
    try {
      var res = await fetch("/api/audio/workspace/segment-version", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      var j = await res.json().catch(function () {
        return {};
      });
      if (!res.ok) {
        var d = j.detail != null ? j.detail : "删除失败";
        alert(typeof d === "string" ? d : JSON.stringify(d));
        return;
      }
      await deleteAudioBlobCache(selectedIndex, segIdx, versionId);
      await loadAudioWorkspaceMeta();
      renderAudioSegmentRows();
    } catch (_) {
      alert("删除失败（网络）");
    }
  }

  function renderAudioSegmentRows() {
    var list = document.getElementById("audio-segments-list");
    var slideLabel = document.getElementById("audio-segments-slide-label");
    if (!list || !slides.length) return;
    ensureAudioSegmentsShape();
    var si = selectedIndex;
    var rows = audioTranscriptSegments[si] || [""];
    if (slideLabel) {
      var sd = sumSlideAudioDuration(si);
      var durHint = sd != null ? " · 本页合计 " + sd.toFixed(1) + "s" : "";
      slideLabel.textContent = "第 " + (si + 1) + " / " + slides.length + " 页" + durHint;
    }
    list.innerHTML = "";
    if (audioSegmentsDialogListenOnly) {
      var indices = [];
      rows.forEach(function (_, segIdx) {
        var gkk = segmentFileKey(si, segIdx);
        var vs = audioSegmentVersions[gkk];
        if (vs && vs.length) indices.push(segIdx);
        else if (audioGeneratedFiles[gkk]) indices.push(segIdx);
      });
      if (!indices.length) {
        var empty = document.createElement("p");
        empty.className = "muted audio-segments-dialog__empty";
        empty.textContent =
          "本页尚无已生成音频。请在音频工作台点击「打开本页逐字稿与音频」编辑逐字稿并生成。";
        list.appendChild(empty);
        return;
      }
      indices.forEach(function (segIdx) {
        var gk = segmentFileKey(si, segIdx);
        var vers = audioSegmentVersions[gk];
        if (!vers || !vers.length) {
          if (audioGeneratedFiles[gk]) {
            vers = [
              {
                id: "legacy",
                rel: audioGeneratedFiles[gk],
                duration_sec: audioSegmentDurations[gk],
                created_at: null,
              },
            ];
          } else {
            vers = [];
          }
        }
        var row = document.createElement("div");
        row.className = "audio-segment-row audio-segment-row--listen-only";
        var head = document.createElement("div");
        head.className = "audio-segment-row__head";
        var title = document.createElement("span");
        title.className = "audio-segment-row__title";
        title.textContent = "段 " + (segIdx + 1);
        head.appendChild(title);
        var segDur = audioSegmentDurations[gk];
        if (typeof segDur === "number" && segDur > 0) {
          var durEl = document.createElement("span");
          durEl.className = "audio-segment-row__dur muted";
          durEl.textContent = " · 当前成片用时长（本段最新一条）约 " + segDur.toFixed(2) + "s";
          head.appendChild(durEl);
        }
        row.appendChild(head);

        var segTextRaw = typeof rows[segIdx] === "string" ? rows[segIdx] : "";
        var listenDownloadName = mp3DownloadFilenameFromTranscript(segTextRaw);

        vers.forEach(function (ver, vi) {
          var vid = ver && ver.id != null ? String(ver.id) : "";
          var verWrap = document.createElement("div");
          verWrap.className = "audio-segment-version";
          var metaLn = document.createElement("div");
          metaLn.className = "audio-segment-version__meta muted";
          var parts = ["记录 " + (vi + 1)];
          if (ver && ver.created_at) {
            try {
              var dt = new Date(ver.created_at);
              if (!isNaN(dt.getTime())) parts.push(dt.toLocaleString());
            } catch (_) {}
          }
          if (typeof ver.duration_sec === "number" && ver.duration_sec > 0) {
            parts.push(ver.duration_sec.toFixed(2) + "s");
          }
          metaLn.textContent = parts.join(" · ");
          verWrap.appendChild(metaLn);

          var actions = document.createElement("div");
          actions.className = "audio-segment-row__actions audio-segment-version__actions";
          var fileUrl =
            vid === "legacy"
              ? buildSegmentFileUrl(segIdx)
              : buildSegmentFileUrl(segIdx, vid);
          var au = document.createElement("audio");
          au.className = "audio-segment-row__player";
          au.controls = true;
          au.preload = "none";
          au.src = fileUrl + (fileUrl.indexOf("?") >= 0 ? "&" : "?") + "t=" + Date.now();
          actions.appendChild(au);
          var dl = document.createElement("a");
          dl.className = "btn btn-text";
          dl.href = fileUrl;
          dl.textContent = "下载";
          dl.setAttribute("download", listenDownloadName);
          actions.appendChild(dl);
          if (vid && vid !== "legacy") {
            var btnDel = document.createElement("button");
            btnDel.type = "button";
            btnDel.className = "btn btn-text";
            btnDel.textContent = "删除";
            (function (sidx, idv) {
              btnDel.addEventListener("click", function () {
                deleteSegmentAudioVersion(sidx, idv);
              });
            })(segIdx, vid);
            actions.appendChild(btnDel);
          }
          verWrap.appendChild(actions);
          row.appendChild(verWrap);
        });

        var tx = document.createElement("div");
        tx.className = "audio-segment-row__listen-transcript";
        tx.setAttribute("role", "region");
        tx.setAttribute("aria-label", "本段口播逐字稿");
        tx.textContent = segTextRaw.trim() || "（暂无该段逐字稿）";
        row.appendChild(tx);
        list.appendChild(row);
      });
      return;
    }
    rows.forEach(function (text, segIdx) {
      var gk = segmentFileKey(si, segIdx);
      var row = document.createElement("div");
      row.className = "audio-segment-row";
      var head = document.createElement("div");
      head.className = "audio-segment-row__head";
      var title = document.createElement("span");
      title.className = "audio-segment-row__title";
      title.textContent = "段 " + (segIdx + 1);
      head.appendChild(title);
      var segDur = audioSegmentDurations[gk];
      if (typeof segDur === "number" && segDur > 0) {
        var durEl = document.createElement("span");
        durEl.className = "audio-segment-row__dur muted";
        durEl.textContent = " · " + segDur.toFixed(2) + "s";
        head.appendChild(durEl);
      }
      if (rows.length > 1) {
        var btnRm = document.createElement("button");
        btnRm.type = "button";
        btnRm.className = "btn btn-text";
        btnRm.textContent = "删除本段";
        (function (idx) {
          btnRm.addEventListener("click", function () {
            flushAudioSegmentsFromDom();
            ensureAudioSegmentsShape();
            audioTranscriptSegments[selectedIndex].splice(idx, 1);
            if (!audioTranscriptSegments[selectedIndex].length) {
              audioTranscriptSegments[selectedIndex] = [""];
            }
            renderAudioSegmentRows();
          });
        })(segIdx);
        head.appendChild(btnRm);
      }
      row.appendChild(head);
      var ta = document.createElement("textarea");
      ta.className = "audio-segment-row__textarea";
      ta.setAttribute("data-audio-seg-text", "1");
      ta.setAttribute("rows", "4");
      ta.value = typeof text === "string" ? text : "";
      row.appendChild(ta);
      var actions = document.createElement("div");
      actions.className = "audio-segment-row__actions";
      var btnGen = document.createElement("button");
      btnGen.type = "button";
      btnGen.className = "btn btn-secondary";
      btnGen.textContent = "生成";
      (function (idx) {
        btnGen.addEventListener("click", function () {
          pendingAudioGenerateSegmentIndex = idx;
          flushAudioSegmentsFromDom();
          openAudioGenerateConfirmDialog();
        });
      })(segIdx);
      actions.appendChild(btnGen);

      var btnRew = document.createElement("button");
      btnRew.type = "button";
      btnRew.className = "btn btn-text";
      btnRew.textContent = "口播稿优化";
      (function (idx) {
        btnRew.addEventListener("click", function () {
          openTranscriptRewriteDialog(idx);
        });
      })(segIdx);
      actions.appendChild(btnRew);

      var btnVer = document.createElement("button");
      btnVer.type = "button";
      btnVer.className = "btn btn-text";
      btnVer.setAttribute("title", "口播版本库");
      btnVer.setAttribute("aria-label", "口播版本库");
      btnVer.innerHTML = '<span aria-hidden="true">📚</span>';
      (function (idx) {
        btnVer.addEventListener("click", function () {
          openTranscriptVersionsDialog(idx);
        });
      })(segIdx);
      actions.appendChild(btnVer);

      if (audioGeneratedFiles[gk]) {
        var au = document.createElement("audio");
        au.className = "audio-segment-row__player";
        au.controls = true;
        au.preload = "none";
        au.src = buildSegmentFileUrl(segIdx) + "&t=" + Date.now();
        actions.appendChild(au);
        var dl = document.createElement("a");
        dl.className = "btn btn-text";
        dl.href = buildSegmentFileUrl(segIdx);
        dl.textContent = "下载";
        dl.setAttribute("download", mp3DownloadFilenameFromTranscript(text));
        actions.appendChild(dl);
      }
      row.appendChild(actions);
      list.appendChild(row);
    });
  }

  async function openAudioSegmentsListenOnly() {
    if (!audioSegmentsDialog || !slides.length) return;
    if (!currentTaskId && !sessionId) {
      if (audioWorkbenchStatus) audioWorkbenchStatus.textContent = "缺少会话或任务标识";
      return;
    }
    await loadAudioWorkspaceMeta();
    setAudioSegmentsDialogMode(true);
    ensureAudioSegmentsShape();
    renderAudioSegmentRows();
    audioSegmentsDialog.showModal();
  }

  function openAudioSegmentsDialog() {
    if (!audioSegmentsDialog || !slides.length) return;
    if (!currentTaskId && !sessionId) {
      if (audioWorkbenchStatus) audioWorkbenchStatus.textContent = "缺少会话或任务标识";
      return;
    }
    setAudioSegmentsDialogMode(false);
    ensureAudioSegmentsShape();
    renderAudioSegmentRows();
    audioSegmentsDialog.showModal();
  }

  async function saveAudioSegmentsDialogRemote() {
    flushAudioTranscript();
    if (!slides.length) return;
    if (audioWorkbenchStatus) audioWorkbenchStatus.textContent = "保存中…";
    var ok = await saveAudioWorkspaceRemote();
    if (audioWorkbenchStatus) audioWorkbenchStatus.textContent = ok ? "已保存逐字稿" : "保存失败";
    if (ok) await loadAudioWorkspaceMeta();
    renderAudioSegmentRows();
  }

  async function loadAudioWorkspaceMeta() {
    if (!slides.length) return;
    var params = new URLSearchParams();
    if (currentTaskId) params.set("task_id", currentTaskId);
    else if (sessionId) params.set("session_id", sessionId);
    else return;
    params.set("slide_count", String(slides.length));
    try {
      var res = await fetch("/api/audio/workspace?" + params.toString());
      if (!res.ok) return;
      var j = await res.json();
      if (j.kind) audioWorkspaceKind = j.kind;
      if (j.key) audioWorkspaceKey = j.key;
      audioGeneratedFiles = j.generated_files && typeof j.generated_files === "object" ? j.generated_files : {};
      audioSegmentVersions = {};
      if (j.segment_versions && typeof j.segment_versions === "object") {
        Object.keys(j.segment_versions).forEach(function (k) {
          var arr = j.segment_versions[k];
          audioSegmentVersions[k] = Array.isArray(arr) ? arr.slice() : [];
        });
      }
      audioSegmentDurations = {};
      if (j.segment_duration_sec && typeof j.segment_duration_sec === "object") {
        Object.keys(j.segment_duration_sec).forEach(function (k) {
          var v = j.segment_duration_sec[k];
          if (typeof v === "number" && v > 0) audioSegmentDurations[k] = v;
        });
      }
      if (j.transcript_segments && j.transcript_segments.length === slides.length) {
        audioTranscriptSegments = j.transcript_segments.map(function (row) {
          if (Array.isArray(row) && row.length) {
            return row.map(function (x) {
              return x != null ? String(x) : "";
            });
          }
          return [""];
        });
      } else if (j.transcripts && j.transcripts.length === slides.length) {
        audioTranscripts = j.transcripts;
        audioTranscriptSegments = j.transcripts.map(function (t) {
          return [typeof t === "string" ? t : ""];
        });
      }
      ensureAudioSegmentsShape();
      syncAudioTranscriptsFromSegments();
      refreshAudioWorkbench();
    } catch (_) {}
  }

  function readStoredAudioGenOverrides() {
    try {
      var s = localStorage.getItem(AUDIO_GEN_LS_KEY);
      if (!s) return {};
      var o = JSON.parse(s);
      if (!o || typeof o !== "object") return {};
      return o;
    } catch (_) {
      return {};
    }
  }

  function writeStoredAudioGenOverrides(obj) {
    try {
      localStorage.setItem(AUDIO_GEN_LS_KEY, JSON.stringify(obj));
    } catch (_) {}
  }

  function ensureSelectHasOption(selectEl, value) {
    if (!selectEl || value == null || value === "") return;
    var v = String(value);
    for (var i = 0; i < selectEl.options.length; i++) {
      if (selectEl.options[i].value === v) return;
    }
    var opt = document.createElement("option");
    opt.value = v;
    opt.textContent = v;
    selectEl.insertBefore(opt, selectEl.firstChild);
    selectEl.value = v;
  }

  /** @param {"audio-gen" | "audio-confirm"} prefix */
  function fillAudioGenFormByPrefix(prefix, mm) {
    var m = mm || {};
    var grp = document.getElementById(prefix + "-group");
    if (grp) grp.value = m.group_id || "";
    var model = document.getElementById(prefix + "-model");
    if (model) {
      var selModel =
        typeof m.model === "string" && m.model.trim() !== ""
          ? m.model
          : "speech-2.8-turbo";
      ensureSelectHasOption(model, selModel);
      model.value = selModel;
    }
    var voice = document.getElementById(prefix + "-voice");
    if (voice) voice.value = m.voice_id || "Chinese (Mandarin)_Lyrical_Voice";
    var lang = document.getElementById(prefix + "-lang");
    if (lang) lang.value = m.language_boost || "Chinese";
    var af = document.getElementById(prefix + "-audio-fmt");
    if (af) af.value = m.audio_format || "mp3";
    var of = document.getElementById(prefix + "-out-fmt");
    if (of) of.value = m.output_format || "url";
    var sr = document.getElementById(prefix + "-sr");
    if (sr) sr.value = String(m.sample_rate != null ? m.sample_rate : 32000);
    var br = document.getElementById(prefix + "-bitrate");
    if (br) br.value = String(m.bitrate != null ? m.bitrate : 128000);
    var sp = document.getElementById(prefix + "-speed");
    if (sp) sp.value = String(m.speed != null ? m.speed : 1);
    var vo = document.getElementById(prefix + "-vol");
    if (vo) vo.value = String(m.vol != null ? m.vol : 1);
    var pi = document.getElementById(prefix + "-pitch");
    if (pi) pi.value = String(m.pitch != null ? m.pitch : 0);
    var em = document.getElementById(prefix + "-emotion");
    if (em) {
      var rawEm = m.emotion;
      if (rawEm != null && rawEm !== undefined && String(rawEm).trim() !== "") {
        var emNorm = String(rawEm).trim().toLowerCase();
        ensureSelectHasOption(em, emNorm);
        em.value = emNorm;
      } else {
        em.value = "";
      }
    }
    var st = document.getElementById(prefix + "-stream");
    if (st) st.checked = !!m.stream;
  }

  function fillAudioGenFormFromMerged(mm) {
    fillAudioGenFormByPrefix("audio-gen", mm);
  }

  /** @param {"audio-gen" | "audio-confirm"} prefix */
  function collectAudioGenOverridesByPrefix(prefix) {
    var modelEl = document.getElementById(prefix + "-model");
    var voiceEl = document.getElementById(prefix + "-voice");
    var langEl = document.getElementById(prefix + "-lang");
    var afEl = document.getElementById(prefix + "-audio-fmt");
    var ofEl = document.getElementById(prefix + "-out-fmt");
    var srEl = document.getElementById(prefix + "-sr");
    var brEl = document.getElementById(prefix + "-bitrate");
    var spEl = document.getElementById(prefix + "-speed");
    var voEl = document.getElementById(prefix + "-vol");
    var piEl = document.getElementById(prefix + "-pitch");
    var stEl = document.getElementById(prefix + "-stream");
    var emEl = document.getElementById(prefix + "-emotion");
    var gidEl = document.getElementById(prefix + "-group");
    if (
      !modelEl ||
      !voiceEl ||
      !langEl ||
      !afEl ||
      !ofEl ||
      !srEl ||
      !brEl ||
      !spEl ||
      !voEl ||
      !piEl ||
      !stEl ||
      !emEl
    ) {
      return {};
    }
    var o = {
      model: modelEl.value,
      voice_id: voiceEl.value.trim(),
      language_boost: langEl.value,
      audio_format: afEl.value,
      output_format: ofEl.value,
      sample_rate: parseInt(srEl.value, 10),
      bitrate: parseInt(brEl.value, 10),
      speed: parseFloat(spEl.value),
      vol: parseFloat(voEl.value),
      pitch: parseInt(piEl.value, 10),
      stream: stEl.checked,
      emotion: emEl.value,
    };
    if (gidEl) {
      var gid = gidEl.value.trim();
      if (gid) o.group_id = gid;
    }
    return o;
  }

  function collectAudioGenOverridesFromForm() {
    return collectAudioGenOverridesByPrefix("audio-gen");
  }

  async function openAudioGenSettingsDialog() {
    try {
      var res = await fetch("/api/settings/external");
      var j = res.ok ? await res.json() : {};
      var mm = j.minimax || {};
      var stored = readStoredAudioGenOverrides();
      var merged = Object.assign({}, mm, stored);
      fillAudioGenFormFromMerged(merged);
      if (audioGenSettingsDialog) audioGenSettingsDialog.showModal();
    } catch (_) {}
  }

  async function openAudioGenerateConfirmDialog() {
    flushAudioTranscript();
    if (!slides.length) {
      if (audioWorkbenchStatus) audioWorkbenchStatus.textContent = "暂无幻灯片";
      return;
    }
    if (!currentTaskId && !sessionId) {
      if (audioWorkbenchStatus) audioWorkbenchStatus.textContent = "缺少会话或任务标识";
      return;
    }
    if (!audioGenerateConfirmDialog) return;
    var merged = {};
    try {
      var res = await fetch("/api/settings/external");
      var j = res.ok ? await res.json() : {};
      var mm = j.minimax || {};
      var stored = readStoredAudioGenOverrides();
      merged = Object.assign({}, mm, stored);
    } catch (_) {
      merged = Object.assign({}, readStoredAudioGenOverrides());
    }
    if (pendingAudioConfirmMinimaxOverlay && Object.keys(pendingAudioConfirmMinimaxOverlay).length) {
      merged = Object.assign({}, merged, pendingAudioConfirmMinimaxOverlay);
      pendingAudioConfirmMinimaxOverlay = null;
    }
    fillAudioGenFormByPrefix("audio-confirm", merged);
    var taEl = document.getElementById("audio-generate-confirm-transcript");
    var rows = audioTranscriptSegments[selectedIndex] || [""];
    var seg = pendingAudioGenerateSegmentIndex;
    if (seg < 0 || seg >= rows.length) seg = 0;
    if (taEl) taEl.textContent = rows[seg] != null ? String(rows[seg]) : "";
    if (audioGenerateConfirmSegLabel) {
      audioGenerateConfirmSegLabel.textContent = "（第 " + (seg + 1) + " 段）";
    }
    audioGenerateConfirmDialog.showModal();
  }

  async function saveAudioWorkspaceRemote() {
    flushAudioTranscript();
    if (!slides.length) return false;
    ensureAudioSegmentsShape();
    syncAudioTranscriptsFromSegments();
    var body = {
      slide_count: slides.length,
      transcripts: audioTranscripts.slice(),
      transcript_segments: audioTranscriptSegments.map(function (row) {
        return row.slice();
      }),
    };
    if (currentTaskId) body.task_id = currentTaskId;
    else if (sessionId) body.session_id = sessionId;
    else return false;
    var res = await fetch("/api/audio/workspace", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return res.ok;
  }

  async function generateAudioForCurrentSlide() {
    flushAudioTranscript();
    if (!slides.length || !audioWorkbenchStatus) return;
    audioWorkbenchStatus.textContent = "保存逐字稿…";
    var okSave = await saveAudioWorkspaceRemote();
    if (!okSave) {
      audioWorkbenchStatus.textContent = "保存失败";
      return;
    }
    audioWorkbenchStatus.textContent = "请求合成…";
    var genBody = {
      slide_index: selectedIndex,
      segment_index: pendingAudioGenerateSegmentIndex,
    };
    if (currentTaskId) genBody.task_id = currentTaskId;
    else if (sessionId) genBody.session_id = sessionId;
    else {
      audioWorkbenchStatus.textContent = "缺少会话或任务标识";
      return;
    }
    var confirmOverrides = collectAudioGenOverridesByPrefix("audio-confirm");
    if (confirmOverrides && Object.keys(confirmOverrides).length > 0) {
      genBody.minimax_overrides = confirmOverrides;
    }
    try {
      var res = await fetch("/api/audio/workspace/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(genBody),
      });
      var j = await res.json().catch(function () {
        return {};
      });
      if (!res.ok) {
        audioWorkbenchStatus.textContent =
          (j.detail && (typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail))) ||
          "生成失败";
        return;
      }
      var seg = pendingAudioGenerateSegmentIndex;
      await loadAudioWorkspaceMeta();
      var url = j.url || "";
      if (url && j.version_id) {
        var rowsAfter = audioTranscriptSegments[selectedIndex] || [""];
        var segTextForName =
          rowsAfter[seg] != null && typeof rowsAfter[seg] === "string"
            ? rowsAfter[seg]
            : "";
        await autoDownloadWorkspaceAudio(
          url,
          mp3DownloadFilenameFromTranscript(segTextForName),
          selectedIndex,
          seg,
          j.version_id
        );
      }
      updateAudioWorkbenchPlayer();
      if (audioWorkbenchStatus) {
        audioWorkbenchStatus.textContent = "第 " + (seg + 1) + " 段已生成并已下载，可试听";
      }
      renderAudioSegmentRows();
    } catch (e) {
      audioWorkbenchStatus.textContent = "网络错误";
    }
  }

  async function parseFile(file) {
    if (!file.name.toLowerCase().endsWith(".pptx")) {
      showErr(errorUpload, "请选择 .pptx 格式的文件（不支持旧版 .ppt）。");
      return;
    }
    await maxUploadReady;
    if (file.size > maxUploadBytes) {
      showErr(
        errorUpload,
        "文件过大（上限 " +
          (maxUploadBytes / (1024 * 1024)).toFixed(0) +
          " MB）。可在启动 Web 服务前设置环境变量 PPT_COURSE_MAX_UPLOAD_MB（例如 200、500），并重启后再上传。",
      );
      return;
    }
    clearErr(errorUpload);
    currentFile = file;
    sessionId = null;
    imagesAvailable = false;
    previewCount = 0;
    previewSource = "libreoffice";
    statusLine.textContent = "";
    resetDownload();
    slideCounter.textContent = "处理中…";
    uploadPanel.querySelector(".drop-title").textContent = "正在解析并生成预览图…";

    var fd = new FormData();
    fd.append("file", file);

    try {
      var res = await fetch("/api/parse", { method: "POST", body: fd });
      if (!res.ok) {
        var detail = "解析失败（" + res.status + "）";
        try {
          var j = await res.json();
          if (j.detail) detail = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail);
        } catch (_) {}
        throw new Error(detail);
      }
      var data = await res.json();
      slides = data.slides || [];
      selectedIndex = 0;
      currentTaskId = data.task_id || null;
      previewMode = "session";
      audioTranscripts = slides.map(function () {
        return "";
      });
      audioTranscriptSegments = slides.map(function () {
        return [""];
      });
      sessionId = data.session_id || null;
      imagesAvailable = !!data.images_available;
      previewCount = typeof data.preview_count === "number" ? data.preview_count : 0;
      previewSource =
        data.preview_source === "placeholder" ? "placeholder" : "libreoffice";
      fileLabel.textContent = data.filename + " · " + formatSize(file.size);
      uploadPanel.querySelector(".drop-title").textContent = "上传培训用 .pptx";

      if (!slides.length) {
        throw new Error("未解析到任何幻灯片。");
      }

      if (imagesAvailable) {
        imagesBanner.classList.add("hidden");
        imagesBanner.textContent = "";
      } else {
        imagesBanner.textContent =
          data.images_error ||
          "未生成 PNG 预览：请在本机安装 LibreOffice 与 Poppler（pdftoppm），并重启 Web 服务。";
        imagesBanner.classList.remove("hidden");
      }

      uploadPanel.classList.add("hidden");
      workspace.classList.remove("hidden");
      if (appMain) appMain.classList.add("app-main--workspace");
      if (slideRail) slideRail.classList.remove("hidden");
      setWorkspaceTaskDrawerTabVisible(true);
      renderSlideList();
      renderPreview();
      await loadAudioWorkspaceMeta();
      var msg = "已解析 " + slides.length + " 页。";
      if (imagesAvailable) {
        if (previewSource === "placeholder") {
          msg +=
            " 已生成文本占位整页预览（临时会话）；安装 LibreOffice + Poppler 后可换为真实渲染图。";
        } else {
          msg +=
            " 已生成整页预览图（临时会话，刷新页面后需重新上传）。左侧为可滚动缩略图列表，右侧为大图。";
        }
      } else {
        msg += " 当前仅显示抽取文本，可按黄条说明安装依赖后重试。";
      }
      statusLine.textContent = msg;
      setImportTranscriptButtonVisible();
      refreshTaskList();
      refreshGenerateSlideVisualEnabled();
      void refreshGenVisualCoverage();
      void refreshDirectorManifest(true);
      void refreshRemotionStatus(true);
      void refreshWorkspaceStatus(true);
    } catch (err) {
      showErr(errorUpload, err instanceof Error ? err.message : String(err));
      uploadPanel.querySelector(".drop-title").textContent = "上传培训用 .pptx";
      slideCounter.textContent = "第 — / — 页";
    }
  }

  function backToUpload() {
    closeWorkspaceTaskDrawer();
    setWorkspaceTaskDrawerTabVisible(false);
    previewMode = "session";
    workspace.classList.add("hidden");
    if (appMain) appMain.classList.remove("app-main--workspace");
    if (slideRail) slideRail.classList.add("hidden");
    uploadPanel.classList.remove("hidden");
    clearErr(errorUpload);
    clearErr(errorWork);
    slides = [];
    currentFile = null;
    currentTaskId = null;
    audioTranscripts = [];
    audioTranscriptSegments = [];
    audioWorkspaceKind = "session";
    audioWorkspaceKey = "";
    audioGeneratedFiles = {};
    audioSegmentVersions = {};
    audioSegmentDurations = {};
    sessionId = null;
    imagesAvailable = false;
    previewCount = 0;
    previewSource = "libreoffice";
    selectedIndex = 0;
    genVisualCoverage = null;
    pvPreviewSourceMode = "original";
    fileInput.value = "";
    imagesBanner.classList.add("hidden");
    imagesBanner.textContent = "";
    uploadPanel.querySelector(".drop-title").textContent = "上传培训用 .pptx";
    statusLine.textContent = "";
    resetDownload();
    setImportTranscriptButtonVisible();
    refreshGenerateSlideVisualEnabled();
    updatePvSourceTabsUi();
    updateAiVisualToolbarBtn();
    directorManifestCache = null;
    if (directorSummary) directorSummary.innerHTML = "";
    if (directorScenes) directorScenes.innerHTML = "";
    if (remotionSummary) remotionSummary.innerHTML = "";
    if (remotionCommand) {
      remotionCommand.textContent = "";
      remotionCommand.classList.add("hidden");
    }
    renderWorkspaceStatus(null);
  }

  dropzone.addEventListener("click", function () {
    fileInput.click();
  });

  dropzone.addEventListener("keydown", function (e) {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      fileInput.click();
    }
  });

  fileInput.addEventListener("change", function () {
    var f = fileInput.files && fileInput.files[0];
    if (f) parseFile(f);
  });

  ["dragenter", "dragover"].forEach(function (ev) {
    dropzone.addEventListener(ev, function (e) {
      e.preventDefault();
      e.stopPropagation();
      dropzone.style.borderColor = "var(--accent)";
    });
  });

  ["dragleave", "drop"].forEach(function (ev) {
    dropzone.addEventListener(ev, function (e) {
      e.preventDefault();
      e.stopPropagation();
      dropzone.style.borderColor = "";
    });
  });

  dropzone.addEventListener("drop", function (e) {
    var f = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
    if (f) parseFile(f);
  });

  btnChangeFile.addEventListener("click", function () {
    backToUpload();
  });

  if (btnWorkspaceTaskDrawer) {
    btnWorkspaceTaskDrawer.addEventListener("click", function (e) {
      e.stopPropagation();
      toggleWorkspaceTaskDrawer();
    });
  }
  if (btnWorkspaceTaskDrawerClose) {
    btnWorkspaceTaskDrawerClose.addEventListener("click", function () {
      closeWorkspaceTaskDrawer();
    });
  }
  if (workspaceTaskDrawerBackdrop) {
    workspaceTaskDrawerBackdrop.addEventListener("click", function () {
      closeWorkspaceTaskDrawer();
    });
  }
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && workspaceTaskDrawerIsOpen()) {
      e.preventDefault();
      closeWorkspaceTaskDrawer();
    }
  });

  if (btnRefreshTasks) {
    btnRefreshTasks.addEventListener("click", function () {
      refreshTaskList();
    });
  }

  function setExternalSettingsTab(name) {
    var tabs = document.querySelectorAll("[data-settings-tab]");
    var panelMini = document.getElementById("panel-minimax");
    var panelTr = document.getElementById("panel-transcript-rewrite");
    var panelDirector = document.getElementById("panel-director-llm");
    var panelAg = document.getElementById("panel-agent");
    tabs.forEach(function (btn) {
      var on = btn.getAttribute("data-settings-tab") === name;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-selected", on ? "true" : "false");
    });
    if (panelMini) panelMini.classList.toggle("hidden", name !== "minimax");
    if (panelTr) panelTr.classList.toggle("hidden", name !== "transcript-rewrite");
    if (panelDirector) panelDirector.classList.toggle("hidden", name !== "director-llm");
    if (panelAg) panelAg.classList.toggle("hidden", name !== "agent");
  }

  function syncApiKeyEyeIcons() {
    var input = document.getElementById("cfg-mm-key");
    var btn = document.getElementById("cfg-mm-key-toggle");
    if (!input || !btn) return;
    var open = btn.querySelector(".api-key-field__eye-open");
    var off = btn.querySelector(".api-key-field__eye-off");
    if (!open || !off) return;
    var isText = input.type === "text";
    open.classList.toggle("hidden", isText);
    off.classList.toggle("hidden", !isText);
    btn.setAttribute("aria-pressed", isText ? "true" : "false");
    btn.setAttribute("aria-label", isText ? "隐藏密钥" : "显示密钥");
  }

  function syncApiKeyToggleDisabled() {
    var input = document.getElementById("cfg-mm-key");
    var btn = document.getElementById("cfg-mm-key-toggle");
    if (!input || !btn) return;
    btn.disabled = !input.value.trim();
  }

  function syncTrApiKeyEyeIcons() {
    var input = document.getElementById("cfg-tr-key");
    var btn = document.getElementById("cfg-tr-key-toggle");
    if (!input || !btn) return;
    var open = btn.querySelector(".api-key-field__eye-open");
    var off = btn.querySelector(".api-key-field__eye-off");
    if (!open || !off) return;
    var isText = input.type === "text";
    open.classList.toggle("hidden", isText);
    off.classList.toggle("hidden", !isText);
    btn.setAttribute("aria-pressed", isText ? "true" : "false");
    btn.setAttribute("aria-label", isText ? "隐藏密钥" : "显示密钥");
  }

  function syncTrApiKeyToggleDisabled() {
    var input = document.getElementById("cfg-tr-key");
    var btn = document.getElementById("cfg-tr-key-toggle");
    if (!input || !btn) return;
    btn.disabled = !input.value.trim();
  }

  function setupApiKeyFieldUi() {
    var input = document.getElementById("cfg-mm-key");
    var btn = document.getElementById("cfg-mm-key-toggle");
    if (!input || !btn || btn.getAttribute("data-bound") === "1") return;
    btn.setAttribute("data-bound", "1");

    input.addEventListener("input", function () {
      syncApiKeyToggleDisabled();
    });

    input.addEventListener("blur", function () {
      syncApiKeyToggleDisabled();
    });

    input.addEventListener("paste", function (e) {
      var cd = e.clipboardData;
      var t = cd && cd.getData("text");
      if (!t) return;
      var trimmed = String(t).trim();
      if (/^bearer\s+/i.test(trimmed)) {
        e.preventDefault();
        input.value = trimmed.replace(/^bearer\s+/i, "").trim();
        syncApiKeyToggleDisabled();
      }
    });

    btn.addEventListener("click", function () {
      if (btn.disabled) return;
      input.type = input.type === "password" ? "text" : "password";
      syncApiKeyEyeIcons();
    });
  }

  function setupTranscriptRewriteApiKeyFieldUi() {
    var input = document.getElementById("cfg-tr-key");
    var btn = document.getElementById("cfg-tr-key-toggle");
    if (!input || !btn || btn.getAttribute("data-bound") === "1") return;
    btn.setAttribute("data-bound", "1");

    input.addEventListener("input", function () {
      syncTrApiKeyToggleDisabled();
    });

    input.addEventListener("blur", function () {
      syncTrApiKeyToggleDisabled();
    });

    input.addEventListener("paste", function (e) {
      var cd = e.clipboardData;
      var t = cd && cd.getData("text");
      if (!t) return;
      var trimmed = String(t).trim();
      if (/^bearer\s+/i.test(trimmed)) {
        e.preventDefault();
        input.value = trimmed.replace(/^bearer\s+/i, "").trim();
        syncTrApiKeyToggleDisabled();
      }
    });

    btn.addEventListener("click", function () {
      if (btn.disabled) return;
      input.type = input.type === "password" ? "text" : "password";
      syncTrApiKeyEyeIcons();
    });
  }

  setupApiKeyFieldUi();
  setupTranscriptRewriteApiKeyFieldUi();

  async function fillExternalSettingsForm() {
    var res = await fetch("/api/settings/external");
    if (!res.ok) return;
    var j = await res.json();
    transcriptRewriteDefaultsExtra =
      j.transcript_rewrite_defaults &&
      typeof j.transcript_rewrite_defaults.extra_instructions === "string"
        ? j.transcript_rewrite_defaults.extra_instructions
        : "";
    var mm = j.minimax || {};
    var selBase = document.getElementById("cfg-mm-base");
    var base = mm.api_base || "https://api.minimaxi.com";
    if (selBase) {
      var found = false;
      for (var i = 0; i < selBase.options.length; i++) {
        if (selBase.options[i].value === base) {
          selBase.selectedIndex = i;
          found = true;
          break;
        }
      }
      if (!found) {
        var opt = document.createElement("option");
        opt.value = base;
        opt.textContent = base;
        selBase.insertBefore(opt, selBase.firstChild);
        selBase.value = base;
      }
    }
    var keyEl = document.getElementById("cfg-mm-key");
    var keyHint = document.getElementById("cfg-mm-key-hint");
    if (keyEl) {
      keyEl.value = typeof mm.api_key === "string" ? mm.api_key : "";
      keyEl.type = "password";
      keyEl.placeholder = "粘贴令牌（不含 Bearer）";
    }
    if (keyHint) {
      keyHint.textContent =
        "密钥仅存本机；保存时以框内为准，清空保存可删除密钥。左侧 Bearer 由服务端写入 Authorization。";
    }
    syncApiKeyToggleDisabled();
    syncApiKeyEyeIcons();
    var gid = document.getElementById("cfg-mm-group");
    if (gid) gid.value = mm.group_id || "";
    var model = document.getElementById("cfg-mm-model");
    if (model) {
      var selCfgModel =
        typeof mm.model === "string" && mm.model.trim() !== ""
          ? mm.model
          : "speech-2.8-turbo";
      ensureSelectHasOption(model, selCfgModel);
      model.value = selCfgModel;
    }
    var voice = document.getElementById("cfg-mm-voice");
    if (voice)
      voice.value =
        mm.voice_id || "Chinese (Mandarin)_Lyrical_Voice";
    var lang = document.getElementById("cfg-mm-lang");
    if (lang) lang.value = mm.language_boost || "Chinese";
    var af = document.getElementById("cfg-mm-audio-fmt");
    if (af) af.value = mm.audio_format || "mp3";
    var of = document.getElementById("cfg-mm-out-fmt");
    if (of) of.value = mm.output_format || "url";
    var sr = document.getElementById("cfg-mm-sr");
    if (sr) sr.value = String(mm.sample_rate || 32000);
    var sp = document.getElementById("cfg-mm-speed");
    if (sp) sp.value = String(mm.speed != null ? mm.speed : 1);
    var vo = document.getElementById("cfg-mm-vol");
    if (vo) vo.value = String(mm.vol != null ? mm.vol : 1);
    var pi = document.getElementById("cfg-mm-pitch");
    if (pi) pi.value = String(mm.pitch != null ? mm.pitch : 0);
    var em = document.getElementById("cfg-mm-emotion");
    if (em) em.value = mm.emotion || "";

    var ag = j.agent || {};
    var note = document.getElementById("cfg-agent-note");
    if (note) note.value = ag.note || "";
    var prov = document.getElementById("cfg-agent-provider");
    if (prov) prov.value = ag.provider || "none";

    var tr = j.transcript_rewrite || {};
    var trProv = document.getElementById("cfg-tr-provider");
    if (trProv) trProv.value = tr.provider || "none";
    var trBase = document.getElementById("cfg-tr-base");
    if (trBase) trBase.value = tr.api_base || "https://api.openai.com/v1";
    var trKey = document.getElementById("cfg-tr-key");
    var trKeyHint = document.getElementById("cfg-tr-key-hint");
    if (trKey) {
      trKey.value = typeof tr.api_key === "string" ? tr.api_key : "";
      trKey.type = "password";
    }
    if (trKeyHint) {
      trKeyHint.textContent =
        "密钥仅存本机；保存以框内为准，清空并保存可删除。请勿暴露公网。";
    }
    syncTrApiKeyToggleDisabled();
    syncTrApiKeyEyeIcons();
    var trModel = document.getElementById("cfg-tr-model");
    if (trModel) {
      var selTr =
        typeof tr.model === "string" && tr.model.trim() !== ""
          ? tr.model.trim()
          : "qwen3.5-flash";
      ensureSelectHasOption(trModel, selTr);
      trModel.value = selTr;
    }
    var trExtra = document.getElementById("cfg-tr-extra");
    if (trExtra) trExtra.value = tr.extra_instructions != null ? String(tr.extra_instructions) : "";

    var director = j.director_llm || {};
    var directorEnabled = document.getElementById("cfg-director-enabled");
    if (directorEnabled) directorEnabled.value = director.enabled ? "true" : "false";
    var directorProvider = document.getElementById("cfg-director-provider");
    if (directorProvider) directorProvider.value = director.provider || "mimo";
    var directorBase = document.getElementById("cfg-director-base");
    if (directorBase) directorBase.value = director.api_base || "https://token-plan-cn.xiaomimimo.com/v1";
    var directorKey = document.getElementById("cfg-director-key");
    if (directorKey) {
      directorKey.value = typeof director.api_key === "string" ? director.api_key : "";
      directorKey.type = "password";
    }
    var directorModel = document.getElementById("cfg-director-model");
    if (directorModel) directorModel.value = director.model || "mimo-v2.5-pro";

    var trTestMsg = document.getElementById("cfg-tr-test-msg");
    if (trTestMsg) trTestMsg.textContent = "";
    var directorTestMsg = document.getElementById("cfg-director-test-msg");
    if (directorTestMsg) directorTestMsg.textContent = "";
    var testMsg = document.getElementById("cfg-mm-test-msg");
    if (testMsg) testMsg.textContent = "";
  }

  function collectTranscriptRewritePayload() {
    var extraEl = document.getElementById("cfg-tr-extra");
    return {
      provider: document.getElementById("cfg-tr-provider").value,
      api_base: document.getElementById("cfg-tr-base").value.trim(),
      api_key: document.getElementById("cfg-tr-key").value.trim(),
      model: document.getElementById("cfg-tr-model").value,
      extra_instructions: extraEl ? extraEl.value : "",
    };
  }

  function collectDirectorLLMPayload() {
    var enabledEl = document.getElementById("cfg-director-enabled");
    return {
      enabled: enabledEl ? enabledEl.value === "true" : false,
      provider: document.getElementById("cfg-director-provider").value,
      api_base: document.getElementById("cfg-director-base").value.trim(),
      api_key: document.getElementById("cfg-director-key").value.trim(),
      model: document.getElementById("cfg-director-model").value.trim() || "mimo-v2.5-pro",
    };
  }

  document.querySelectorAll("[data-settings-tab]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var name = btn.getAttribute("data-settings-tab");
      if (name) setExternalSettingsTab(name);
    });
  });

  var btnTrExtraReset = document.getElementById("btn-tr-extra-reset");
  if (btnTrExtraReset) {
    btnTrExtraReset.addEventListener("click", function () {
      var ta = document.getElementById("cfg-tr-extra");
      if (!ta || !transcriptRewriteDefaultsExtra) return;
      ta.value = transcriptRewriteDefaultsExtra;
      ta.focus();
    });
  }

  if (btnExternalSettings && externalSettingsDialog) {
    btnExternalSettings.addEventListener("click", async function () {
      await fillExternalSettingsForm();
      setExternalSettingsTab("minimax");
      externalSettingsDialog.showModal();
    });
  }

  if (externalSettingsDialog) {
    externalSettingsDialog.addEventListener("click", function (e) {
      if (e.target === externalSettingsDialog) externalSettingsDialog.close();
    });
  }

  var btnSettingsCancel = document.getElementById("btn-settings-cancel");
  if (btnSettingsCancel && externalSettingsDialog) {
    btnSettingsCancel.addEventListener("click", function () {
      externalSettingsDialog.close();
    });
  }

  function collectMinimaxSettingsPayload() {
    var grpEl = document.getElementById("cfg-mm-group");
    var minimax = {
      api_base: document.getElementById("cfg-mm-base").value,
      group_id: grpEl ? grpEl.value.trim() : "",
      model: document.getElementById("cfg-mm-model").value,
      voice_id: document.getElementById("cfg-mm-voice").value.trim(),
      language_boost: document.getElementById("cfg-mm-lang").value,
      audio_format: document.getElementById("cfg-mm-audio-fmt").value,
      output_format: document.getElementById("cfg-mm-out-fmt").value,
      sample_rate: parseInt(document.getElementById("cfg-mm-sr").value, 10),
      speed: parseFloat(document.getElementById("cfg-mm-speed").value),
      vol: parseFloat(document.getElementById("cfg-mm-vol").value),
      pitch: parseInt(document.getElementById("cfg-mm-pitch").value, 10),
    };
    minimax.api_key = document.getElementById("cfg-mm-key").value.trim();
    var emo = document.getElementById("cfg-mm-emotion").value;
    if (emo) minimax.emotion = emo;
    return minimax;
  }

  var btnSettingsSave = document.getElementById("btn-settings-save");
  if (btnSettingsSave) {
    btnSettingsSave.addEventListener("click", async function () {
      var agentNoteEl = document.getElementById("cfg-agent-note");
      var payload = {
        minimax: collectMinimaxSettingsPayload(),
        transcript_rewrite: collectTranscriptRewritePayload(),
        director_llm: collectDirectorLLMPayload(),
        agent: {
          note: agentNoteEl ? agentNoteEl.value : "",
          provider: document.getElementById("cfg-agent-provider").value,
        },
      };

      try {
        var res = await fetch("/api/settings/external", {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (!res.ok) {
          var detail = "保存失败";
          try {
            var ej = await res.json();
            if (ej.detail) detail = typeof ej.detail === "string" ? ej.detail : JSON.stringify(ej.detail);
          } catch (_) {}
          alert(detail);
          return;
        }
        if (externalSettingsDialog) externalSettingsDialog.close();
      } catch (_) {
        alert("保存失败（网络）");
      }
    });
  }

  var btnMmTest = document.getElementById("btn-mm-test");
  if (btnMmTest) {
    btnMmTest.addEventListener("click", async function () {
      var msg = document.getElementById("cfg-mm-test-msg");
      if (msg) msg.textContent = "测试中…";
      try {
        var res = await fetch("/api/settings/external/minimax/test", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
          minimax: collectMinimaxSettingsPayload(),
          persist: true,
        }),
        });
        var j = await res.json().catch(function () {
          return {};
        });
        if (!res.ok) {
          if (msg)
            msg.textContent =
              (j.detail && (typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail))) ||
              "失败";
          return;
        }
        if (msg) {
          var okParts = [];
          if (j.detail) okParts.push(j.detail);
          if (j.persisted) okParts.push("已写入本机 external_apis 配置");
          if (j.archive_path) okParts.push("记录 " + j.archive_path);
          msg.textContent = okParts.length ? okParts.join("；") : "成功";
        }
      } catch (_) {
        if (msg) msg.textContent = "网络错误";
      }
    });
  }

  var btnTrTest = document.getElementById("btn-tr-test");
  if (btnTrTest) {
    btnTrTest.addEventListener("click", async function () {
      var msg = document.getElementById("cfg-tr-test-msg");
      if (msg) msg.textContent = "测试中…";
      try {
        var res = await fetch("/api/settings/external/transcript-rewrite/test", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            transcript_rewrite: collectTranscriptRewritePayload(),
          }),
        });
        var j = await res.json().catch(function () {
          return {};
        });
        if (!res.ok) {
          if (msg)
            msg.textContent =
              (j.detail && (typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail))) ||
              "失败";
          return;
        }
        if (msg) msg.textContent = j.detail || "成功";
      } catch (_) {
        if (msg) msg.textContent = "网络错误";
      }
    });
  }

  var btnDirectorTest = document.getElementById("btn-director-test");
  if (btnDirectorTest) {
    btnDirectorTest.addEventListener("click", async function () {
      var msg = document.getElementById("cfg-director-test-msg");
      if (msg) msg.textContent = "测试中…";
      try {
        var res = await fetch("/api/settings/external/director-llm/test", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            director_llm: collectDirectorLLMPayload(),
          }),
        });
        var j = await res.json().catch(function () {
          return {};
        });
        if (!res.ok) {
          if (msg)
            msg.textContent =
              (j.detail && (typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail))) ||
              "失败";
          return;
        }
        if (msg) msg.textContent = j.detail || "成功";
      } catch (_) {
        if (msg) msg.textContent = "网络错误";
      }
    });
  }

  if (transcriptRewriteDialog) {
    transcriptRewriteDialog.addEventListener("click", function (e) {
      if (e.target === transcriptRewriteDialog) transcriptRewriteDialog.close();
    });
  }

  var btnTrRewriteCancel = document.getElementById("btn-tr-rewrite-cancel");
  if (btnTrRewriteCancel && transcriptRewriteDialog) {
    btnTrRewriteCancel.addEventListener("click", function () {
      transcriptRewriteDialog.close();
    });
  }

  var btnTrRewriteRun = document.getElementById("btn-tr-rewrite-run");
  if (btnTrRewriteRun) {
    btnTrRewriteRun.addEventListener("click", function () {
      runTranscriptRewriteRequest();
    });
  }

  var btnTrRewriteAdopt = document.getElementById("btn-tr-rewrite-adopt");
  if (btnTrRewriteAdopt) {
    btnTrRewriteAdopt.addEventListener("click", function () {
      adoptTranscriptRewriteFromDialog();
    });
  }

  var btnTrRewriteApplyMinimax = document.getElementById("btn-tr-rewrite-apply-minimax");
  if (btnTrRewriteApplyMinimax) {
    btnTrRewriteApplyMinimax.addEventListener("click", function () {
      applyTranscriptRewriteMinimaxHints();
    });
  }

  var btnTrVersionsClose = document.getElementById("btn-tr-versions-close");
  if (btnTrVersionsClose && transcriptRewriteVersionsDialog) {
    btnTrVersionsClose.addEventListener("click", function () {
      transcriptRewriteVersionsDialog.close();
    });
  }

  if (transcriptRewriteVersionsDialog) {
    transcriptRewriteVersionsDialog.addEventListener("click", function (e) {
      if (e.target === transcriptRewriteVersionsDialog) transcriptRewriteVersionsDialog.close();
    });
  }

  if (btnAudioSave) {
    btnAudioSave.addEventListener("click", async function () {
      if (!audioWorkbenchStatus) return;
      audioWorkbenchStatus.textContent = "保存中…";
      var ok = await saveAudioWorkspaceRemote();
      audioWorkbenchStatus.textContent = ok ? "已保存逐字稿" : "保存失败";
    });
  }

  if (directorScenes) {
    directorScenes.addEventListener("click", function (e) {
      var t = e.target;
      if (!(t instanceof HTMLElement)) return;
      var card = t.closest(".director-scene-card");
      if (!card || !(card instanceof HTMLElement)) return;
      var sid = card.getAttribute("data-scene-id") || "";
      if (!sid) return;
      if (t.closest(".director-scene-approve")) {
        void directorApproveScene(sid);
        return;
      }
      if (t.closest(".director-scene-reject")) {
        void directorRejectScene(sid);
      }
    });
  }
  if (btnDirectorRawManifest) {
    btnDirectorRawManifest.addEventListener("click", function () {
      void postDirectorRawManifest();
    });
  }
  if (btnDirectorRebuild) {
    btnDirectorRebuild.addEventListener("click", function () {
      void postDirectorRebuild();
    });
  }
  if (btnDirectorRefresh) {
    btnDirectorRefresh.addEventListener("click", function () {
      void refreshDirectorManifest(true);
    });
  }
  if (btnDirectorExport) {
    btnDirectorExport.addEventListener("click", function () {
      void postDirectorExport();
    });
  }
  if (btnRemotionGenerate) {
    btnRemotionGenerate.addEventListener("click", function () {
      void postRemotionRenderTask();
    });
  }
  if (btnRemotionRefresh) {
    btnRemotionRefresh.addEventListener("click", function () {
      void refreshRemotionStatus(false);
      void refreshWorkspaceStatus(true);
    });
  }
  if (btnWorkflowRefresh) {
    btnWorkflowRefresh.addEventListener("click", function () {
      void refreshWorkspaceStatus(false);
      void refreshDirectorManifest(true);
      void refreshRemotionStatus(true);
    });
  }
  if (taskWorkflowSteps) {
    taskWorkflowSteps.addEventListener("click", function (e) {
      var t = e.target;
      if (!(t instanceof HTMLElement)) return;
      var btn = t.closest("[data-workflow-target]");
      if (!btn || !(btn instanceof HTMLElement)) return;
      var id = btn.getAttribute("data-workflow-target") || "";
      var el = id ? document.getElementById(id) : null;
      if (el) {
        el.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  }

  function bindOpenSegments(el) {
    if (el) {
      el.addEventListener("click", function () {
        openAudioSegmentsDialog();
      });
    }
  }
  bindOpenSegments(btnAudioOpenSegments);

  if (btnAudioSegmentsToolbar) {
    btnAudioSegmentsToolbar.addEventListener("click", function () {
      void openAudioSegmentsListenOnly();
    });
  }

  if (btnAiVisualStock) {
    btnAiVisualStock.addEventListener("click", function () {
      openAiVisualStockDialog();
    });
  }
  if (pvTabOriginal) {
    pvTabOriginal.addEventListener("click", function () {
      if (pvPreviewSourceMode === "original") return;
      pvPreviewSourceMode = "original";
      updatePvSourceTabsUi();
      renderPreview();
    });
  }
  if (pvTabAi) {
    pvTabAi.addEventListener("click", function () {
      if (!genVisualCoverage || !genVisualCoverage.all_slides_complete) return;
      if (pvPreviewSourceMode === "ai") return;
      pvPreviewSourceMode = "ai";
      updatePvSourceTabsUi();
      renderPreview();
    });
  }
  if (btnAiVisualStockDownload) {
    btnAiVisualStockDownload.addEventListener("click", function () {
      void downloadAiVisualStockImage();
    });
  }
  if (aiVisualStockDialog) {
    aiVisualStockDialog.addEventListener("click", function (e) {
      if (e.target === aiVisualStockDialog) aiVisualStockDialog.close();
    });
  }

  if (btnGenerateSlideVisual) {
    btnGenerateSlideVisual.addEventListener("click", function () {
      openGenerateVisualDialog();
    });
  }
  if (btnGvCancel) {
    btnGvCancel.addEventListener("click", function () {
      closeGenerateVisualDialog();
    });
  }
  if (btnGvSubmit) {
    btnGvSubmit.addEventListener("click", function () {
      void submitGenerateVisualFromDialog();
    });
  }
  if (btnGvDone) {
    btnGvDone.addEventListener("click", function () {
      closeGenerateVisualDialog();
    });
  }
  if (generateVisualDialog) {
    generateVisualDialog.addEventListener("close", function () {
      resetGenerateVisualDialogToForm();
    });
  }

  if (btnAudioSegmentAdd) {
    btnAudioSegmentAdd.addEventListener("click", function () {
      flushAudioSegmentsFromDom();
      ensureAudioSegmentsShape();
      audioTranscriptSegments[selectedIndex].push("");
      renderAudioSegmentRows();
    });
  }

  if (btnAudioSegmentsSave) {
    btnAudioSegmentsSave.addEventListener("click", function () {
      void saveAudioSegmentsDialogRemote();
    });
  }

  if (audioSegmentsDialog) {
    audioSegmentsDialog.addEventListener("click", function (e) {
      if (e.target === audioSegmentsDialog) audioSegmentsDialog.close();
    });
    audioSegmentsDialog.addEventListener("close", function () {
      setAudioSegmentsDialogMode(false);
    });
  }

  var btnAudioGenerateConfirmCancel = document.getElementById("btn-audio-generate-confirm-cancel");
  if (btnAudioGenerateConfirmCancel && audioGenerateConfirmDialog) {
    btnAudioGenerateConfirmCancel.addEventListener("click", function () {
      audioGenerateConfirmDialog.close();
    });
  }

  var btnAudioGenerateConfirmOk = document.getElementById("btn-audio-generate-confirm-ok");
  if (btnAudioGenerateConfirmOk && audioGenerateConfirmDialog) {
    btnAudioGenerateConfirmOk.addEventListener("click", function () {
      audioGenerateConfirmDialog.close();
      generateAudioForCurrentSlide();
    });
  }

  if (audioGenerateConfirmDialog) {
    audioGenerateConfirmDialog.addEventListener("click", function (e) {
      if (e.target === audioGenerateConfirmDialog) audioGenerateConfirmDialog.close();
    });
  }

  if (btnAudioGenSettings) {
    btnAudioGenSettings.addEventListener("click", function () {
      openAudioGenSettingsDialog();
    });
  }

  if (audioGenSettingsDialog) {
    audioGenSettingsDialog.addEventListener("click", function (e) {
      if (e.target === audioGenSettingsDialog) audioGenSettingsDialog.close();
    });
  }

  var btnAudioGenCancel = document.getElementById("btn-audio-gen-cancel");
  if (btnAudioGenCancel && audioGenSettingsDialog) {
    btnAudioGenCancel.addEventListener("click", function () {
      audioGenSettingsDialog.close();
    });
  }

  var btnAudioGenSave = document.getElementById("btn-audio-gen-save");
  if (btnAudioGenSave) {
    btnAudioGenSave.addEventListener("click", function () {
      var o = collectAudioGenOverridesFromForm();
      writeStoredAudioGenOverrides(o);
      if (audioGenSettingsDialog) audioGenSettingsDialog.close();
    });
  }

  var btnAudioGenRestore = document.getElementById("btn-audio-gen-restore");
  if (btnAudioGenRestore) {
    btnAudioGenRestore.addEventListener("click", async function () {
      try {
        localStorage.removeItem(AUDIO_GEN_LS_KEY);
        var res = await fetch("/api/settings/external");
        var j = res.ok ? await res.json() : {};
        fillAudioGenFormFromMerged(j.minimax || {});
      } catch (_) {}
    });
  }

  if (btnTaskDeleteCancel) {
    btnTaskDeleteCancel.addEventListener("click", function (e) {
      e.stopPropagation();
      closeDeletePopconfirm();
    });
  }
  if (btnTaskDeleteConfirm) {
    btnTaskDeleteConfirm.addEventListener("click", function (e) {
      e.stopPropagation();
      if (pendingDeleteId) executeDeleteStoredTask(pendingDeleteId);
    });
  }
  if (btnTaskRenameCancel) {
    btnTaskRenameCancel.addEventListener("click", function (e) {
      e.stopPropagation();
      closeRenamePopover();
    });
  }
  if (btnTaskRenameSave) {
    btnTaskRenameSave.addEventListener("click", function (e) {
      e.stopPropagation();
      executeRenameTask();
    });
  }
  if (btnTaskIdClose) {
    btnTaskIdClose.addEventListener("click", function (e) {
      e.stopPropagation();
      closeTaskIdPopover();
    });
  }
  if (btnTaskIdCopy && taskIdPopoverCode) {
    btnTaskIdCopy.addEventListener("click", function (e) {
      e.stopPropagation();
      var text = taskIdPopoverCode.textContent || "";
      if (!text) return;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).catch(function () {});
      }
    });
  }
  if (taskRenameInput) {
    taskRenameInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        executeRenameTask();
      }
    });
  }

  if (btnPvCarouselPrev) {
    btnPvCarouselPrev.addEventListener("click", function () {
      goPvCarousel(-1);
    });
  }
  if (btnPvCarouselNext) {
    btnPvCarouselNext.addEventListener("click", function () {
      goPvCarousel(1);
    });
  }
  if (pvCarousel) {
    pvCarousel.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") {
        e.preventDefault();
        goPvCarousel(-1);
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        goPvCarousel(1);
      }
    });
  }

  if (pvCarouselImgOuter) {
    pvCarouselImgOuter.addEventListener("click", function () {
      if (!pvImage || !pvImage.getAttribute("src")) return;
      openPvPreviewZoomDialog();
    });
    pvCarouselImgOuter.addEventListener("keydown", function (e) {
      if (e.key !== "Enter" && e.key !== " ") return;
      e.preventDefault();
      if (!pvImage || !pvImage.getAttribute("src")) return;
      openPvPreviewZoomDialog();
    });
  }

  if (pvPreviewZoomDialog) {
    pvPreviewZoomDialog.addEventListener("click", function (e) {
      if (e.target === pvPreviewZoomDialog) pvPreviewZoomDialog.close();
    });
  }
  if (btnPvPreviewZoomDownload) {
    btnPvPreviewZoomDownload.addEventListener("click", function () {
      void downloadPvPreviewZoomImage();
    });
  }

  document.querySelectorAll("[data-pv-text-drawer]").forEach(function (root) {
    var btn = root.querySelector("[data-pv-text-drawer-toggle]");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var collapsed = root.classList.toggle("is-collapsed");
      btn.setAttribute("aria-expanded", collapsed ? "false" : "true");
      var region = root.querySelector(".pv-text-drawer__content[role='region']");
      if (region) region.setAttribute("aria-hidden", collapsed ? "true" : "false");
    });
  });

  try {
    var linkApiDocs = document.getElementById("link-api-docs");
    if (linkApiDocs) {
      linkApiDocs.href = new URL("/docs", window.location.origin).href;
    }
  } catch (_) {}

  /** MiniMax 普通话音色：可搜索下拉 + 仍可手动输入任意 voice_id */
  var mandarinVoicesCache = null;
  var mandarinVoicesLoadPromise = null;
  var openVoiceComboboxRoot = null;

  function loadMandarinVoices() {
    if (mandarinVoicesCache) return Promise.resolve(mandarinVoicesCache);
    if (mandarinVoicesLoadPromise) return mandarinVoicesLoadPromise;
    mandarinVoicesLoadPromise = fetch("/assets/minimax-mandarin-voices.json")
      .then(function (res) {
        if (!res.ok) throw new Error("load voices");
        return res.json();
      })
      .then(function (data) {
        mandarinVoicesCache = Array.isArray(data) ? data : [];
        return mandarinVoicesCache;
      })
      .catch(function () {
        mandarinVoicesCache = [];
        return mandarinVoicesCache;
      });
    return mandarinVoicesLoadPromise;
  }

  function filterMandarinVoices(items, q) {
    var s = (q || "").trim().toLowerCase();
    if (!s) return items.slice();
    return items.filter(function (row) {
      var id = String(row.voice_id || "").toLowerCase();
      var nm = String(row.name || "").toLowerCase();
      return id.indexOf(s) !== -1 || nm.indexOf(s) !== -1;
    });
  }

  function positionVoiceComboboxPanel(root) {
    var panel = root.querySelector(".voice-id-combobox__panel");
    var inp = root.querySelector(".voice-id-combobox__input");
    if (!panel || !inp) return;
    var r = inp.getBoundingClientRect();
    var w = Math.max(r.width, 260);
    panel.style.left = Math.min(r.left, window.innerWidth - w - 8) + "px";
    panel.style.top = r.bottom + 4 + "px";
    panel.style.width = w + "px";
    var maxH = Math.max(100, window.innerHeight - r.bottom - 12);
    panel.style.maxHeight = Math.min(300, maxH) + "px";
  }

  function renderVoiceComboboxList(root, query) {
    var list = root.querySelector(".voice-id-combobox__list");
    var inp = root.querySelector(".voice-id-combobox__input");
    if (!list) return;
    list.innerHTML = "";
    var items = filterMandarinVoices(mandarinVoicesCache || [], query);
    if (!items.length) {
      var empty = document.createElement("li");
      empty.className = "voice-id-combobox__empty";
      empty.style.padding = "0.5rem";
      empty.style.fontSize = "0.78rem";
      empty.style.color = "var(--muted)";
      empty.textContent = mandarinVoicesCache && mandarinVoicesCache.length === 0 ? "音色列表加载失败，仍可手动输入 voice_id。" : "无匹配项，可直接在上方输入自定义 ID。";
      list.appendChild(empty);
      return;
    }
    items.forEach(function (row) {
      var li = document.createElement("li");
      li.setAttribute("role", "presentation");
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "voice-id-combobox__item";
      btn.setAttribute("role", "option");
      btn.dataset.voiceId = row.voice_id;
      var nm = document.createElement("span");
      nm.className = "voice-id-combobox__item-name";
      nm.textContent = row.name || row.voice_id;
      var idSpan = document.createElement("span");
      idSpan.className = "voice-id-combobox__item-id";
      idSpan.textContent = row.voice_id;
      btn.appendChild(nm);
      btn.appendChild(idSpan);
      btn.addEventListener("click", function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        if (inp) inp.value = row.voice_id;
        closeVoiceComboboxPanel();
        if (inp) inp.focus();
      });
      li.appendChild(btn);
      list.appendChild(li);
    });
  }

  function closeVoiceComboboxPanel() {
    if (!openVoiceComboboxRoot) return;
    var root = openVoiceComboboxRoot;
    openVoiceComboboxRoot = null;
    var panel = root.querySelector(".voice-id-combobox__panel");
    var toggle = root.querySelector(".voice-id-combobox__toggle");
    var filterInput = root.querySelector(".voice-id-combobox__filter");
    if (panel) {
      panel.hidden = true;
      panel.style.left = "";
      panel.style.top = "";
      panel.style.width = "";
      panel.style.maxHeight = "";
    }
    if (toggle) {
      toggle.setAttribute("aria-expanded", "false");
      toggle.classList.remove("is-open");
    }
    if (filterInput) filterInput.value = "";
  }

  function openVoiceComboboxPanel(root) {
    if (openVoiceComboboxRoot && openVoiceComboboxRoot !== root) closeVoiceComboboxPanel();
    openVoiceComboboxRoot = root;
    var panel = root.querySelector(".voice-id-combobox__panel");
    var toggle = root.querySelector(".voice-id-combobox__toggle");
    var filterInput = root.querySelector(".voice-id-combobox__filter");
    if (!panel) return;
    loadMandarinVoices().then(function () {
      if (openVoiceComboboxRoot !== root) return;
      if (filterInput) filterInput.value = "";
      renderVoiceComboboxList(root, "");
      panel.hidden = false;
      positionVoiceComboboxPanel(root);
      if (toggle) {
        toggle.setAttribute("aria-expanded", "true");
        toggle.classList.add("is-open");
      }
      if (filterInput) {
        filterInput.focus();
        try {
          filterInput.select();
        } catch (_) {}
      }
    });
  }

  function initVoiceIdComboboxes() {
    document.querySelectorAll("[data-voice-combobox]").forEach(function (root) {
      var toggle = root.querySelector(".voice-id-combobox__toggle");
      var filterInput = root.querySelector(".voice-id-combobox__filter");
      if (toggle) {
        toggle.addEventListener("click", function (e) {
          e.preventDefault();
          e.stopPropagation();
          if (openVoiceComboboxRoot === root) closeVoiceComboboxPanel();
          else openVoiceComboboxPanel(root);
        });
      }
      if (filterInput) {
        filterInput.addEventListener("input", function () {
          if (openVoiceComboboxRoot !== root) return;
          renderVoiceComboboxList(root, filterInput.value);
        });
        filterInput.addEventListener("keydown", function (e) {
          if (e.key === "Escape") {
            e.preventDefault();
            closeVoiceComboboxPanel();
            var inp = root.querySelector(".voice-id-combobox__input");
            if (inp) inp.focus();
          }
        });
      }
    });

    document.addEventListener(
      "click",
      function (e) {
        if (!openVoiceComboboxRoot) return;
        if (openVoiceComboboxRoot.contains(e.target)) return;
        closeVoiceComboboxPanel();
      },
      true,
    );

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && openVoiceComboboxRoot) {
        closeVoiceComboboxPanel();
      }
    });

    window.addEventListener("resize", function () {
      if (openVoiceComboboxRoot) positionVoiceComboboxPanel(openVoiceComboboxRoot);
    });

    document.addEventListener(
      "scroll",
      function () {
        if (openVoiceComboboxRoot) positionVoiceComboboxPanel(openVoiceComboboxRoot);
      },
      true,
    );
  }

  initVoiceIdComboboxes();

  refreshTaskList();
  fillExternalSettingsForm().catch(function () {});
})();
