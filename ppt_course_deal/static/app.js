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
  /** @type {Record<string, number>} 键同 segmentFileKey：「页索引-段索引」→ 秒 */
  let audioSegmentDurations = {};
  let pendingAudioGenerateSegmentIndex = 0;
  let pendingRewriteSegmentIndex = 0;
  let pendingVersionsSegmentIndex = 0;
  /** @type {string | null} */
  let currentTaskId = null;
  /** 上传解析会话为 session；从已存任务打开为 stored */
  let previewMode = "session";

  let pvMediaRequestId = 0;
  /** @type {Array<{ url: string, caption: string, kind: string, shapeIndex: number | null }>} */
  let pvCarouselFrames = [];
  let pvCarouselIndex = 0;

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
    "主预览区标题栏 **喇叭**只用于本页**已生成**各段 MP3 的试听与下载；**逐字稿编辑、口播优化与生成**请用音频工作台里的「打开本页逐字稿与音频」。\n\n每一段口播对应一次 MiniMax 合成。点击某段的「生成」会先弹出确认框（合成参数与文案预览），确认后再请求服务端调用 T2A；返回的音频写入本机任务数据目录。\n\n「口播稿优化」在服务端调用 OpenAI 兼容大模型，按 MiniMax 官方文档白名单优化停顿与插入语；需先在顶栏「外部 API 配置」→「口播稿优化 API」启用并填写密钥。左右对比确认后再「采用改写稿」。「口播版本库」将多版改写稿存在浏览器本地，可按段选用。\n\n切换幻灯片后，若本弹窗保持打开，列表会随当前页刷新。\n\n「保存到服务端」会把当前内存中的全部逐字稿（含每一页的多段结构 transcript_segments）通过 PUT /api/audio/workspace 写入服务端工作区元数据，用于持久化与下次打开任务恢复；仅保存文本，不会在未点「生成」时调用 MiniMax。";
  var HELP_AUDIO_GENERATE_CONFIRM_BODY =
    "以下为当前合成参数（服务端「外部 API 配置」中的 MiniMax 默认值，与本机「进入音频生成设置」里保存的合成偏好合并后的预览）以及待合成的该段口播稿。\n\n确认无误后点击「开始生成」才会向服务端发起 POST /api/audio/workspace/generate，仅针对当前选中的这一段。";
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

  function flushAudioTranscript() {
    if (audioSegmentsDialog && audioSegmentsDialog.open) {
      flushAudioSegmentsFromDom();
    }
    if (!slides.length) return;
    syncAudioTranscriptsFromSegments();
  }

  function refreshAudioWorkbench() {
    if (!slides.length) return;
    syncAudioTranscriptsFromSegments();
    if (audioWorkbenchStatus) audioWorkbenchStatus.textContent = "";
    if (audioSegmentsDialog && audioSegmentsDialog.open) {
      renderAudioSegmentRows();
    }
  }

  function segmentFileKey(slideIdx, segIdx) {
    return String(slideIdx) + "-" + String(segIdx);
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

  function buildSegmentFileUrl(segIdx) {
    if (!audioWorkspaceKey || !slides.length) return "";
    var params = new URLSearchParams();
    params.set("kind", audioWorkspaceKind);
    params.set("key", audioWorkspaceKey);
    params.set("slide_index", String(selectedIndex));
    params.set("segment_index", String(segIdx));
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

  function pushTranscriptVersion(segIdx, text) {
    var v = loadTranscriptVersions(segIdx);
    v.push({
      id: "v_" + Date.now() + "_" + Math.random().toString(36).slice(2, 9),
      text: text,
      createdAt: new Date().toISOString(),
    });
    saveTranscriptVersions(segIdx, v);
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
    if (resTa) resTa.value = "";
    try {
      var res = await fetch("/api/transcript/rewrite", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: text,
          transcript_rewrite: collectTranscriptRewritePayload(),
        }),
      });
      var j = await res.json().catch(function () {
        return {};
      });
      if (!res.ok) {
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
    flushAudioSegmentsFromDom();
    ensureAudioSegmentsShape();
    var si = selectedIndex;
    var segIdx = pendingRewriteSegmentIndex;
    if (!audioTranscriptSegments[si]) audioTranscriptSegments[si] = [""];
    audioTranscriptSegments[si][segIdx] = next;
    syncAudioTranscriptsFromSegments();
    if (chk && chk.checked) pushTranscriptVersion(segIdx, next);
    if (transcriptRewriteDialog) transcriptRewriteDialog.close();
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
        var meta = document.createElement("div");
        meta.className = "tr-version-card__meta";
        try {
          meta.textContent = new Date(row.createdAt).toLocaleString();
        } catch (_) {
          meta.textContent = row.createdAt || "";
        }
        var sn = document.createElement("div");
        sn.className = "tr-version-card__snippet";
        sn.textContent = snippetPreview(row.text, 220);
        var act = document.createElement("div");
        act.className = "tr-version-card__actions";
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "btn btn-secondary";
        btn.textContent = "采用此版本";
        (function (txt) {
          btn.addEventListener("click", function () {
            flushAudioSegmentsFromDom();
            ensureAudioSegmentsShape();
            var si = selectedIndex;
            if (!audioTranscriptSegments[si]) audioTranscriptSegments[si] = [""];
            audioTranscriptSegments[si][pendingVersionsSegmentIndex] = txt;
            syncAudioTranscriptsFromSegments();
            if (transcriptRewriteVersionsDialog) transcriptRewriteVersionsDialog.close();
            renderAudioSegmentRows();
          });
        })(row.text);
        act.appendChild(btn);
        card.appendChild(meta);
        card.appendChild(sn);
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
        if (audioGeneratedFiles[gkk]) indices.push(segIdx);
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
          durEl.textContent = " · " + segDur.toFixed(2) + "s";
          head.appendChild(durEl);
        }
        row.appendChild(head);
        var actions = document.createElement("div");
        actions.className = "audio-segment-row__actions";
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
        dl.setAttribute("download", "");
        actions.appendChild(dl);
        row.appendChild(actions);
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
        dl.setAttribute("download", "");
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

  function fillAudioGenFormFromMerged(mm) {
    var m = mm || {};
    var grp = document.getElementById("audio-gen-group");
    if (grp) grp.value = m.group_id || "";
    var model = document.getElementById("audio-gen-model");
    if (model) {
      var selModel =
        typeof m.model === "string" && m.model.trim() !== ""
          ? m.model
          : "speech-2.8-turbo";
      ensureSelectHasOption(model, selModel);
      model.value = selModel;
    }
    var voice = document.getElementById("audio-gen-voice");
    if (voice) voice.value = m.voice_id || "Chinese (Mandarin)_Lyrical_Voice";
    var lang = document.getElementById("audio-gen-lang");
    if (lang) lang.value = m.language_boost || "Chinese";
    var af = document.getElementById("audio-gen-audio-fmt");
    if (af) af.value = m.audio_format || "mp3";
    var of = document.getElementById("audio-gen-out-fmt");
    if (of) of.value = m.output_format || "url";
    var sr = document.getElementById("audio-gen-sr");
    if (sr) sr.value = String(m.sample_rate != null ? m.sample_rate : 32000);
    var br = document.getElementById("audio-gen-bitrate");
    if (br) br.value = String(m.bitrate != null ? m.bitrate : 128000);
    var sp = document.getElementById("audio-gen-speed");
    if (sp) sp.value = String(m.speed != null ? m.speed : 1);
    var vo = document.getElementById("audio-gen-vol");
    if (vo) vo.value = String(m.vol != null ? m.vol : 1);
    var pi = document.getElementById("audio-gen-pitch");
    if (pi) pi.value = String(m.pitch != null ? m.pitch : 0);
    var em = document.getElementById("audio-gen-emotion");
    if (em) em.value = m.emotion != null && m.emotion !== undefined ? m.emotion : "";
    var st = document.getElementById("audio-gen-stream");
    if (st) st.checked = !!m.stream;
  }

  function collectAudioGenOverridesFromForm() {
    var o = {
      model: document.getElementById("audio-gen-model").value,
      voice_id: document.getElementById("audio-gen-voice").value.trim(),
      language_boost: document.getElementById("audio-gen-lang").value,
      audio_format: document.getElementById("audio-gen-audio-fmt").value,
      output_format: document.getElementById("audio-gen-out-fmt").value,
      sample_rate: parseInt(document.getElementById("audio-gen-sr").value, 10),
      bitrate: parseInt(document.getElementById("audio-gen-bitrate").value, 10),
      speed: parseFloat(document.getElementById("audio-gen-speed").value),
      vol: parseFloat(document.getElementById("audio-gen-vol").value),
      pitch: parseInt(document.getElementById("audio-gen-pitch").value, 10),
      stream: document.getElementById("audio-gen-stream").checked,
      emotion: document.getElementById("audio-gen-emotion").value,
    };
    var gid = document.getElementById("audio-gen-group").value.trim();
    if (gid) o.group_id = gid;
    return o;
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

  function formatMergedAudioGenForConfirm(m) {
    m = m || {};
    var gid = m.group_id;
    var lines = [];
    lines.push("Group ID：" + (gid != null && String(gid).trim() !== "" ? String(gid) : "（未指定）"));
    lines.push("合成模型：" + (m.model || "speech-2.8-turbo"));
    lines.push("音色 voice_id：" + (m.voice_id || "Chinese (Mandarin)_Lyrical_Voice"));
    lines.push("语言增强 language_boost：" + (m.language_boost || "Chinese"));
    lines.push("音频格式 audio_setting.format：" + (m.audio_format || "mp3"));
    lines.push("输出编码 output_format：" + (m.output_format || "url"));
    lines.push(
      "采样率 sample_rate：" + (m.sample_rate != null ? String(m.sample_rate) : "32000"),
    );
    lines.push("码率 bitrate：" + (m.bitrate != null ? String(m.bitrate) : "128000"));
    lines.push("语速 speed：" + (m.speed != null ? String(m.speed) : "1"));
    lines.push("音量 vol：" + (m.vol != null ? String(m.vol) : "1"));
    lines.push("音高 pitch：" + (m.pitch != null ? String(m.pitch) : "0"));
    lines.push("情绪 emotion：" + (m.emotion ? String(m.emotion) : "（自动）"));
    lines.push("流式 stream：" + (m.stream ? "是" : "否"));
    return lines.join("\n");
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
    var cfgEl = document.getElementById("audio-generate-confirm-config");
    var taEl = document.getElementById("audio-generate-confirm-transcript");
    if (cfgEl) cfgEl.textContent = formatMergedAudioGenForConfirm(merged);
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
    var mmPrefs = readStoredAudioGenOverrides();
    if (mmPrefs && Object.keys(mmPrefs).length > 0) {
      genBody.minimax_overrides = mmPrefs;
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
      var gk = segmentFileKey(selectedIndex, seg);
      if (j.filename) audioGeneratedFiles[gk] = j.filename;
      if (typeof j.duration_sec === "number" && j.duration_sec > 0) {
        audioSegmentDurations[gk] = j.duration_sec;
      }
      var url = j.url || "";
      if (url && audioPlayer) {
        audioPlayer.classList.remove("hidden");
        audioPlayer.src = url + (url.indexOf("?") >= 0 ? "&" : "?") + "t=" + Date.now();
      }
      if (audioWorkbenchStatus) {
        audioWorkbenchStatus.textContent = "第 " + (seg + 1) + " 段已生成，可试听";
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
    audioSegmentDurations = {};
    sessionId = null;
    imagesAvailable = false;
    previewCount = 0;
    previewSource = "libreoffice";
    selectedIndex = 0;
    fileInput.value = "";
    imagesBanner.classList.add("hidden");
    imagesBanner.textContent = "";
    uploadPanel.querySelector(".drop-title").textContent = "上传培训用 .pptx";
    statusLine.textContent = "";
    resetDownload();
    setImportTranscriptButtonVisible();
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
    var panelAg = document.getElementById("panel-agent");
    tabs.forEach(function (btn) {
      var on = btn.getAttribute("data-settings-tab") === name;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-selected", on ? "true" : "false");
    });
    if (panelMini) panelMini.classList.toggle("hidden", name !== "minimax");
    if (panelTr) panelTr.classList.toggle("hidden", name !== "transcript-rewrite");
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

    var trTestMsg = document.getElementById("cfg-tr-test-msg");
    if (trTestMsg) trTestMsg.textContent = "";
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
