(function () {
  var copy = {
    materials: {
      kicker: "素材入仓",
      title: "生成 raw_material_manifest.json",
      body: "每页预览图、正文、备注和图片素材都会落盘，后续脚本能引用真实课件证据。",
    },
    director: {
      kicker: "导演中枢",
      title: "生成 director_manifest.json",
      body: "把素材重组为章节、镜头、旁白意图和画面调度，便于人工审核和重跑。",
    },
    audio: {
      kicker: "声音工坊",
      title: "维护逐页口播与音频版本",
      body: "每页可以有多段口播，多次合成会保留记录，方便试听、回滚和替换模型。",
    },
    render: {
      kicker: "成片引擎",
      title: "生成 Remotion 渲染入参",
      body: "render_plan.json 和 input-props.json 会进入 React Composition，最后渲染 MP4。",
    },
  };

  var tiles = Array.prototype.slice.call(document.querySelectorAll("[data-story-tile]"));
  var steps = Array.prototype.slice.call(document.querySelectorAll("[data-story-step]"));
  var kicker = document.getElementById("story-board-kicker");
  var title = document.getElementById("story-board-title");
  var body = document.getElementById("story-board-copy");

  function setActive(name) {
    var next = copy[name] || copy.materials;
    tiles.forEach(function (tile) {
      tile.classList.toggle("is-active", tile.getAttribute("data-story-tile") === name);
    });
    if (kicker) kicker.textContent = next.kicker;
    if (title) title.textContent = next.title;
    if (body) body.textContent = next.body;
  }

  tiles.forEach(function (tile) {
    tile.addEventListener("click", function () {
      var name = tile.getAttribute("data-story-tile") || "materials";
      var step = document.querySelector('[data-story-step="' + name + '"]');
      setActive(name);
      if (step && typeof step.scrollIntoView === "function") {
        step.scrollIntoView({ behavior: "smooth", block: "center" });
      } else if (step && step.id) {
        window.location.hash = step.id;
      }
    });
  });

  if ("IntersectionObserver" in window) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            setActive(entry.target.getAttribute("data-story-step") || "materials");
          }
        });
      },
      { root: null, threshold: 0.52 }
    );
    steps.forEach(function (step) {
      observer.observe(step);
    });
  }
})();
