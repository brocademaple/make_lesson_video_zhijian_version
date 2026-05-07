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
  const btnTransform = document.getElementById("btn-transform");
  const slideCounter = document.getElementById("slide-counter");
  const slideMeta = document.getElementById("slide-meta");
  const pvModeLabel = document.getElementById("pv-mode-label");
  const pvImageWrap = document.getElementById("pv-image-wrap");
  const pvCarousel = document.getElementById("pv-carousel");
  const pvCarouselState = document.getElementById("pv-carousel-state");
  const btnPvCarouselPrev = document.getElementById("pv-carousel-prev");
  const btnPvCarouselNext = document.getElementById("pv-carousel-next");
  const pvImage = document.getElementById("pv-image");
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
  const btnAudioSegmentsToolbar = document.getElementById("btn-audio-segments-toolbar");
  const btnAudioOpenSegments = document.getElementById("btn-audio-open-segments");
  const btnAudioSegmentAdd = document.getElementById("btn-audio-segment-add");
  const btnAudioSegmentsSave = document.getElementById("btn-audio-segments-save");
  const audioGenSettingsDialog = document.getElementById("audio-gen-settings-dialog");
  const audioGenerateConfirmDialog = document.getElementById("audio-generate-confirm-dialog");
  const audioGenerateConfirmSegLabel = document.getElementById("audio-generate-confirm-seg-label");
  const btnAudioGenSettings = document.getElementById("btn-audio-gen-settings");
  const externalSettingsDialog = document.getElementById("external-settings-dialog");
  const btnExternalSettings = document.getElementById("btn-external-settings");

  var AUDIO_GEN_LS_KEY = "ppt_course_audio_gen_overrides";

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
  let pendingAudioGenerateSegmentIndex = 0;
  /** @type {string | null} */
  let currentTaskId = null;
  /** 上传解析会话为 session；从已存任务打开为 stored */
  let previewMode = "session";

  let pvMediaRequestId = 0;
  /** @type {Array<{ url: string, caption: string }>} */
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
      btnTransform.disabled = true;
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
    } catch (_) {}
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

    /** @type {Array<{ url: string, caption: string }>} */
    var frames = [];
    if (fullSrc) {
      frames.push({ url: fullSrc, caption: "整页" });
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
      currentPreviewHelpText += " 使用两侧箭头在多条预览之间切换。";
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

  function flushAudioTranscript() {
    if (!audioTranscriptEl || !slides.length) return;
    audioTranscripts[selectedIndex] = audioTranscriptEl.value;
  }

  function refreshAudioWorkbench() {
    if (!audioTranscriptEl || !slides.length) return;
    var t = audioTranscripts[selectedIndex];
    audioTranscriptEl.value = typeof t === "string" ? t : "";
    if (audioWorkbenchStatus) audioWorkbenchStatus.textContent = "";
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
      if (j.transcripts && j.transcripts.length === slides.length) {
        audioTranscripts = j.transcripts;
      }
      refreshAudioWorkbench();
    } catch (_) {}
  }

  function readStoredAudioGenOverrides() {
    try {
      var s = localStorage.getItem(AUDIO_GEN_LS_KEY);
      if (!s) return {};
      var o = JSON.parse(s);
      return o && typeof o === "object" ? o : {};
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
      ensureSelectHasOption(model, m.model);
      model.value = m.model || "speech-2.8-hd";
    }
    var voice = document.getElementById("audio-gen-voice");
    if (voice) voice.value = m.voice_id || "Chinese (Mandarin)_Lyrical_Voice";
    var lang = document.getElementById("audio-gen-lang");
    if (lang) lang.value = m.language_boost || "Chinese";
    var af = document.getElementById("audio-gen-audio-fmt");
    if (af) af.value = m.audio_format || "mp3";
    var of = document.getElementById("audio-gen-out-fmt");
    if (of) of.value = m.output_format || "hex";
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
    lines.push("合成模型：" + (m.model || "speech-2.8-hd"));
    lines.push("音色 voice_id：" + (m.voice_id || "Chinese (Mandarin)_Lyrical_Voice"));
    lines.push("语言增强 language_boost：" + (m.language_boost || "Chinese"));
    lines.push("音频格式 audio_setting.format：" + (m.audio_format || "mp3"));
    lines.push("输出编码 output_format：" + (m.output_format || "hex"));
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
    if (taEl && audioTranscriptEl) taEl.textContent = audioTranscriptEl.value;
    audioGenerateConfirmDialog.showModal();
  }

  async function saveAudioWorkspaceRemote() {
    flushAudioTranscript();
    if (!slides.length) return;
    var body = {
      slide_count: slides.length,
      transcripts: audioTranscripts.slice(),
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
    var genBody = { slide_index: selectedIndex };
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
      var url = j.url || "";
      if (url && audioPlayer) {
        audioPlayer.classList.remove("hidden");
        audioPlayer.src = url + (url.indexOf("?") >= 0 ? "&" : "?") + "t=" + Date.now();
        audioWorkbenchStatus.textContent = "已生成，可播放试听";
      }
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
      btnTransform.disabled = false;
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
    sessionId = null;
    imagesAvailable = false;
    previewCount = 0;
    previewSource = "libreoffice";
    selectedIndex = 0;
    btnTransform.disabled = true;
    fileInput.value = "";
    imagesBanner.classList.add("hidden");
    imagesBanner.textContent = "";
    uploadPanel.querySelector(".drop-title").textContent = "上传培训用 .pptx";
    statusLine.textContent = "";
    resetDownload();
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

  btnTransform.addEventListener("click", async function () {
    if (!currentFile) return;
    await maxUploadReady;
    if (currentFile.size > maxUploadBytes) {
      showErr(
        errorWork,
        "文件过大（上限 " +
          (maxUploadBytes / (1024 * 1024)).toFixed(0) +
          " MB）。请提高 PPT_COURSE_MAX_UPLOAD_MB 后重启服务，或改用较小的源文件。",
      );
      return;
    }
    clearErr(errorWork);
    resetDownload();
    btnTransform.disabled = true;
    statusLine.textContent = "正在生成课程化 PPTX…";

    var fd = new FormData();
    fd.append("file", currentFile);

    try {
      var res = await fetch("/api/transform", { method: "POST", body: fd });
      if (!res.ok) {
        var detail = "生成失败（" + res.status + "）";
        try {
          var j = await res.json();
          if (j.detail) detail = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail);
        } catch (_) {}
        throw new Error(detail);
      }

      var blob = await res.blob();
      var src = res.headers.get("X-Source-Slides");
      var out = res.headers.get("X-Output-Slides");
      var name = currentFile.name.replace(/\.pptx$/i, "") + "_course.pptx";
      var cd = res.headers.get("Content-Disposition");
      if (cd) {
        var m = /filename\*=UTF-8''([^;\n]+)/i.exec(cd);
        if (m && m[1]) {
          try {
            name = decodeURIComponent(m[1].trim());
          } catch (_) {}
        }
      }

      lastObjectUrl = URL.createObjectURL(blob);
      downloadLink.href = lastObjectUrl;
      downloadLink.download = name;

      var a = document.createElement("a");
      a.href = lastObjectUrl;
      a.download = name;
      document.body.appendChild(a);
      a.click();
      a.remove();

      var stats = "已生成课程化 PPTX（完整下载），可在本机用 PowerPoint / WPS 打开。";
      if (src != null && out != null) {
        stats = "源稿 " + src + " 页 → 课程页 " + out + " 页。" + stats;
      }
      resultStats.textContent = stats;
      resultBanner.classList.remove("hidden");
      statusLine.textContent = "生成完成。";
    } catch (err) {
      showErr(errorWork, err instanceof Error ? err.message : String(err));
      statusLine.textContent = "";
    } finally {
      btnTransform.disabled = false;
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
    var panelAg = document.getElementById("panel-agent");
    tabs.forEach(function (btn) {
      var on = btn.getAttribute("data-settings-tab") === name;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-selected", on ? "true" : "false");
    });
    if (panelMini) panelMini.classList.toggle("hidden", name !== "minimax");
    if (panelAg) panelAg.classList.toggle("hidden", name !== "agent");
  }

  async function fillExternalSettingsForm() {
    var res = await fetch("/api/settings/external");
    if (!res.ok) return;
    var j = await res.json();
    var mm = j.minimax || {};
    var selBase = document.getElementById("cfg-mm-base");
    var base = mm.api_base || "https://api.minimax.io";
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
    if (keyEl) {
      keyEl.value = "";
      keyEl.placeholder = mm.configured
        ? "已保存密钥（尾号 " + (mm.suffix || "****") + "），留空不改"
        : "在此填写 MiniMax API Key";
    }
    var gid = document.getElementById("cfg-mm-group");
    if (gid) gid.value = mm.group_id || "";
    var model = document.getElementById("cfg-mm-model");
    if (model) model.value = mm.model || "speech-2.8-hd";
    var voice = document.getElementById("cfg-mm-voice");
    if (voice)
      voice.value =
        mm.voice_id || "Chinese (Mandarin)_Lyrical_Voice";
    var lang = document.getElementById("cfg-mm-lang");
    if (lang) lang.value = mm.language_boost || "Chinese";
    var af = document.getElementById("cfg-mm-audio-fmt");
    if (af) af.value = mm.audio_format || "mp3";
    var of = document.getElementById("cfg-mm-out-fmt");
    if (of) of.value = mm.output_format || "hex";
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

    var testMsg = document.getElementById("cfg-mm-test-msg");
    if (testMsg) testMsg.textContent = "";
  }

  document.querySelectorAll("[data-settings-tab]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var name = btn.getAttribute("data-settings-tab");
      if (name) setExternalSettingsTab(name);
    });
  });

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

  var btnSettingsSave = document.getElementById("btn-settings-save");
  if (btnSettingsSave) {
    btnSettingsSave.addEventListener("click", async function () {
      var grpEl = document.getElementById("cfg-mm-group");
      var agentNoteEl = document.getElementById("cfg-agent-note");
      var payload = {
        minimax: {
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
        },
        agent: {
          note: agentNoteEl ? agentNoteEl.value : "",
          provider: document.getElementById("cfg-agent-provider").value,
        },
      };
      var ek = document.getElementById("cfg-mm-key").value.trim();
      if (ek) payload.minimax.api_key = ek;
      var emo = document.getElementById("cfg-mm-emotion").value;
      if (emo) payload.minimax.emotion = emo;

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
        var res = await fetch("/api/settings/external/minimax/test", { method: "POST" });
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

  if (btnAudioSave) {
    btnAudioSave.addEventListener("click", async function () {
      if (!audioWorkbenchStatus) return;
      audioWorkbenchStatus.textContent = "保存中…";
      var ok = await saveAudioWorkspaceRemote();
      audioWorkbenchStatus.textContent = ok ? "已保存逐字稿" : "保存失败";
    });
  }

  if (btnAudioGenerate) {
    btnAudioGenerate.addEventListener("click", function () {
      openAudioGenerateConfirmDialog();
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

  refreshTaskList();
})();
