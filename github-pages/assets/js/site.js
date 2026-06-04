(function () {
  var copy = {
    materials: {
      kicker: "素材入仓",
      title: "把 PPT 拆成可复用素材",
      body: "每页预览、文本和图片素材都会落盘，后续导演脚本能引用真实证据。",
    },
    director: {
      kicker: "导演中枢",
      title: "让素材变成镜头脚本",
      body: "系统按“讲规则、带新人、教流程、讲销售话术”等方向组织叙事和画面节奏。",
    },
    audio: {
      kicker: "声音工坊",
      title: "口播稿和音频逐段维护",
      body: "每页可以有多段口播，多次合成可保留记录，便于试听、回滚和替换。",
    },
    render: {
      kicker: "成片引擎",
      title: "React 时间线渲染 MP4",
      body: "Remotion 接收确定的 input-props，用组件、Sequence 和 interpolate 控制画面。",
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
