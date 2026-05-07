(function () {
  const uploadPanel = document.getElementById("upload-panel");
  const workspace = document.getElementById("workspace");
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("file-input");
  const errorUpload = document.getElementById("error-upload");
  const errorWork = document.getElementById("error-work");
  const slideList = document.getElementById("slide-list");
  const fileLabel = document.getElementById("file-label");
  const btnChangeFile = document.getElementById("btn-change-file");
  const btnTransform = document.getElementById("btn-transform");
  const slideCounter = document.getElementById("slide-counter");
  const slideMeta = document.getElementById("slide-meta");
  const pvModeLabel = document.getElementById("pv-mode-label");
  const pvImageWrap = document.getElementById("pv-image-wrap");
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
  const btnRefreshTasks = document.getElementById("btn-refresh-tasks");
  const btnHelpTaskList = document.getElementById("btn-help-task-list");
  const taskViewDialog = document.getElementById("task-view-dialog");
  const taskModalTitle = document.getElementById("task-modal-title");
  const tmSlideList = document.getElementById("tm-slide-list");
  const tmSlideCounter = document.getElementById("tm-slide-counter");
  const tmSlideMeta = document.getElementById("tm-slide-meta");
  const tmPvModeLabel = document.getElementById("tm-pv-mode-label");
  const tmPvImageWrap = document.getElementById("tm-pv-image-wrap");
  const tmPvImage = document.getElementById("tm-pv-image");
  const tmPvTitle = document.getElementById("tm-pv-title");
  const tmPvBlocks = document.getElementById("tm-pv-blocks");
  const tmPvNotesWrap = document.getElementById("tm-pv-notes-wrap");
  const tmPvNotes = document.getElementById("tm-pv-notes");

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

  /** @type {any[]} */
  let tmSlides = [];
  let tmSelectedIndex = 0;
  /** @type {string | null} */
  let tmTaskId = null;
  let tmPreviewCount = 0;
  let tmImagesAvailable = false;
  /** @type {"libreoffice" | "placeholder"} */
  let tmPreviewSource = "libreoffice";

  var HELP_PRODUCT_BODY =
    "上传后解析全文稿；若本机安装了 LibreOffice + Poppler，服务端会将每一页渲染为 PNG，通过临时 URL 预览（类似私有图床）。";
  var HELP_UPLOAD_BODY =
    "上传后将解析全部页面；左侧为缩略列表，右侧为当前页渲染图与从形状中提取的文本。";
  var HELP_CLI_BODY =
    "可在终端执行命令行转换：ppt-course transform 输入.pptx（将「输入.pptx」换成你的文件路径）。无需打开本页面。";
  var HELP_TASK_LIST_BODY =
    "上传并成功解析后，文件副本与解析结果会保存在项目根目录下的 ppt_course_data/tasks/（每任务一个子文件夹），并自动出现在此列表。\n\n列表为空表示尚无记录；可在服务端设置环境变量 PPT_COURSE_DATA 改用其它数据根目录。";

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
    return iso.replace("T", " ").slice(0, 19) + " UTC";
  }

  async function refreshTaskList() {
    if (!taskList) return;
    try {
      var res = await fetch("/api/tasks");
      if (!res.ok) return;
      var data = await res.json();
      var tasks = data.tasks || [];
      taskList.innerHTML = "";
      tasks.forEach(function (t) {
        var li = document.createElement("li");
        li.className = "task-li";
        var main = document.createElement("button");
        main.type = "button";
        main.className = "task-row-main";
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
          openStoredTask(t.id);
        });
        var del = document.createElement("button");
        del.type = "button";
        del.className = "task-row-del";
        del.setAttribute("aria-label", "删除该任务");
        del.textContent = "×";
        del.addEventListener("click", function (e) {
          e.stopPropagation();
          deleteStoredTask(t.id);
        });
        li.appendChild(main);
        li.appendChild(del);
        taskList.appendChild(li);
      });
      if (taskList) {
        taskList.setAttribute("aria-label", tasks.length ? "已存任务列表" : "暂无任务");
      }
    } catch (_) {}
  }

  async function deleteStoredTask(id) {
    if (!id || !window.confirm("删除该任务的本地存储记录？（不可恢复）")) return;
    try {
      var res = await fetch("/api/tasks/" + encodeURIComponent(id), { method: "DELETE" });
      if (!res.ok) return;
      refreshTaskList();
      if (tmTaskId === id && taskViewDialog) taskViewDialog.close();
    } catch (_) {}
  }

  async function openStoredTask(taskId) {
    if (!taskViewDialog || !taskModalTitle) return;
    try {
      var res = await fetch("/api/tasks/" + encodeURIComponent(taskId));
      if (!res.ok) return;
      var data = await res.json();
      tmTaskId = taskId;
      tmSlides = data.slides || [];
      tmSelectedIndex = 0;
      tmPreviewCount = typeof data.preview_count === "number" ? data.preview_count : 0;
      tmImagesAvailable = !!data.images_available;
      tmPreviewSource = data.preview_source === "placeholder" ? "placeholder" : "libreoffice";
      taskModalTitle.textContent = data.filename || "解析结果";
      renderTaskSlideList();
      renderTaskPreview();
      taskViewDialog.showModal();
    } catch (_) {}
  }

  function renderTaskSlideList() {
    if (!tmSlideList) return;
    tmSlideList.innerHTML = "";
    tmSlides.forEach(function (s, i) {
      var li = document.createElement("li");
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "slide-row" + (i === tmSelectedIndex ? " active" : "");
      var snippet =
        (s.title && s.title !== "（无标题）" ? s.title : "") ||
        (s.text_blocks && s.text_blocks[0]) ||
        (s.text && s.text.slice(0, 80)) ||
        "（空白页）";
      var thumbHtml = "";
      if (tmImagesAvailable && tmTaskId && i < tmPreviewCount) {
        thumbHtml =
          '<img class="slide-thumb" src="' +
          storedPreviewUrl(tmTaskId, i) +
          '" alt="" loading="lazy" width="72" height="40" />';
      } else {
        thumbHtml = '<span class="slide-thumb slide-thumb--placeholder">' + (i + 1) + "</span>";
      }
      btn.innerHTML =
        thumbHtml +
        '<span class="slide-col"><span class="slide-idx">第 ' +
        (i + 1) +
        " / " +
        tmSlides.length +
        ' 页</span><span class="slide-snippet">' +
        escapeHtml(snippet) +
        "</span></span>";
      btn.addEventListener("click", function () {
        tmSelectedIndex = i;
        renderTaskSlideList();
        renderTaskPreview();
      });
      li.appendChild(btn);
      tmSlideList.appendChild(li);
    });
  }

  function renderTaskPreview() {
    if (!tmSlides.length || !tmPvTitle) return;
    var s = tmSlides[tmSelectedIndex];
    if (tmSlideCounter) {
      tmSlideCounter.textContent =
        "第 " + (tmSelectedIndex + 1) + " / " + tmSlides.length + " 页";
    }
    var metaParts = [];
    if (s.layout) metaParts.push("版式：" + s.layout);
    metaParts.push("形状内图 " + (s.image_count || 0));
    metaParts.push("表 " + (s.table_count || 0));
    if (tmSlideMeta) tmSlideMeta.textContent = metaParts.join(" · ");

    if (tmImagesAvailable && tmTaskId && tmSelectedIndex < tmPreviewCount) {
      if (tmPreviewSource === "placeholder") {
        if (tmPvModeLabel) tmPvModeLabel.textContent = "文本占位整页预览（Pillow 排版示意）";
      } else {
        if (tmPvModeLabel) tmPvModeLabel.textContent = "幻灯片渲染图（服务端 LibreOffice → PNG）";
      }
      if (tmPvImageWrap) tmPvImageWrap.classList.remove("hidden");
      if (tmPvImage) {
        tmPvImage.onerror = function () {
          tmPvImage.alt = "预览图加载失败";
        };
        tmPvImage.src = storedPreviewUrl(tmTaskId, tmSelectedIndex);
        tmPvImage.onload = function () {
          tmPvImage.alt = "第 " + (tmSelectedIndex + 1) + " 页";
        };
      }
    } else if (tmImagesAvailable && tmTaskId && tmSelectedIndex >= tmPreviewCount) {
      if (tmPvModeLabel) tmPvModeLabel.textContent = "本页暂无整页渲染图";
      if (tmPvImageWrap) tmPvImageWrap.classList.add("hidden");
      if (tmPvImage) tmPvImage.removeAttribute("src");
    } else {
      if (tmPvModeLabel) tmPvModeLabel.textContent = "文本解析预览（未生成整页渲染图）";
      if (tmPvImageWrap) tmPvImageWrap.classList.add("hidden");
      if (tmPvImage) tmPvImage.removeAttribute("src");
    }

    tmPvTitle.textContent = s.title || "（无标题）";
    if (tmPvBlocks) {
      tmPvBlocks.innerHTML = "";
      var blocks =
        s.text_blocks && s.text_blocks.length
          ? s.text_blocks
          : [s.text || "（本页未识别到正文文本）"];
      blocks.forEach(function (line) {
        var div = document.createElement("div");
        div.className = "block";
        div.textContent = line;
        tmPvBlocks.appendChild(div);
      });
    }
    if (s.notes && tmPvNotes && tmPvNotesWrap) {
      tmPvNotes.textContent = s.notes;
      tmPvNotesWrap.classList.remove("hidden");
    } else if (tmPvNotesWrap) {
      tmPvNotesWrap.classList.add("hidden");
    }
  }

  function renderSlideList() {
    slideList.innerHTML = "";
    slides.forEach(function (s, i) {
      const li = document.createElement("li");
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "slide-row" + (i === selectedIndex ? " active" : "");
      const snippet =
        (s.title && s.title !== "（无标题）" ? s.title : "") ||
        (s.text_blocks && s.text_blocks[0]) ||
        s.text.slice(0, 80) ||
        "（空白页）";

      var thumbHtml = "";
      if (imagesAvailable && sessionId && i < previewCount) {
        thumbHtml =
          '<img class="slide-thumb" src="' +
          previewUrl(i) +
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
        selectedIndex = i;
        updateSelectionClasses();
        renderPreview();
      });
      li.appendChild(btn);
      slideList.appendChild(li);
    });
  }

  function updateSelectionClasses() {
    const buttons = slideList.querySelectorAll("button.slide-row");
    buttons.forEach(function (b, i) {
      if (i === selectedIndex) b.classList.add("active");
      else b.classList.remove("active");
    });
  }

  function escapeHtml(str) {
    const d = document.createElement("div");
    d.textContent = str;
    return d.innerHTML;
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

    if (imagesAvailable && sessionId && selectedIndex < previewCount) {
      if (previewSource === "placeholder") {
        pvModeLabel.textContent = "文本占位整页预览（Pillow 排版示意）";
        currentPreviewHelpText =
          "以下为 python-pptx 抽取的文本；上图由服务端根据文本生成的示意图，非像素级还原。安装 LibreOffice + Poppler 后可显示真实幻灯片渲染图。";
      } else {
        pvModeLabel.textContent = "幻灯片渲染图（服务端 LibreOffice → PNG）";
        currentPreviewHelpText =
          "以下为 python-pptx 抽取的文本，可与上图对照（复杂排版可能略有差异）。";
      }
      pvImageWrap.classList.remove("hidden");
      pvImage.onerror = function () {
        pvImage.alt = "预览图加载失败";
      };
      pvImage.src = previewUrl(selectedIndex);
      pvImage.onload = function () {
        pvImage.alt = "第 " + (selectedIndex + 1) + " 页";
      };
    } else if (imagesAvailable && sessionId && selectedIndex >= previewCount) {
      pvModeLabel.textContent = "本页暂无整页渲染图";
      pvImageWrap.classList.add("hidden");
      pvImage.removeAttribute("src");
      currentPreviewHelpText =
        "渲染得到的 PNG 页数少于幻灯片页数，请仅参考下方文本；或检查 LibreOffice 导出是否完整。";
    } else {
      pvModeLabel.textContent = "文本解析预览（未生成整页渲染图）";
      pvImageWrap.classList.add("hidden");
      pvImage.removeAttribute("src");
      currentPreviewHelpText =
        "无法生成整页预览图时仅显示抽取文本。若已安装 LibreOffice + Poppler 仍如此，请查看服务端日志。";
    }

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
  }

  async function parseFile(file) {
    if (!file.name.toLowerCase().endsWith(".pptx")) {
      showErr(errorUpload, "请选择 .pptx 格式的文件（不支持旧版 .ppt）。");
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
      renderSlideList();
      renderPreview();
      btnTransform.disabled = false;
      var msg = "已解析 " + slides.length + " 页。";
      if (imagesAvailable) {
        if (previewSource === "placeholder") {
          msg +=
            " 已生成文本占位整页预览（临时会话）；安装 LibreOffice + Poppler 后可换为真实渲染图。";
        } else {
          msg +=
            " 已生成整页预览图（临时会话，刷新页面后需重新上传）。左侧缩略图与右侧大图来自 /api/preview/…";
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
    workspace.classList.add("hidden");
    uploadPanel.classList.remove("hidden");
    clearErr(errorUpload);
    clearErr(errorWork);
    slides = [];
    currentFile = null;
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

  btnTransform.addEventListener("click", async function () {
    if (!currentFile) return;
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

  if (taskViewDialog) {
    taskViewDialog.addEventListener("click", function (e) {
      if (e.target === taskViewDialog) taskViewDialog.close();
    });
  }

  refreshTaskList();
})();
