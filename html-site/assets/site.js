(() => {
  const root = document.documentElement;
  const current = localStorage.getItem("theme") || "light";
  const btn = document.getElementById("theme-toggle");

  async function initMermaid() {
    const blocks = [...document.querySelectorAll("pre code.language-mermaid")];
    if (!blocks.length) return;
    for (const code of blocks) {
      const pre = code.closest("pre");
      if (!pre) continue;
      const wrap = document.createElement("div");
      wrap.className = "mermaid";
      wrap.textContent = code.textContent || "";
      pre.replaceWith(wrap);
    }
    try {
      const mermaid = await import("https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs");
      mermaid.default.initialize({
        startOnLoad: false,
        securityLevel: "loose",
        theme: (root.getAttribute("data-theme") || "light") === "dark" ? "dark" : "default",
        flowchart: { htmlLabels: false, useMaxWidth: true, nodeSpacing: 50, rankSpacing: 60 },
      });
      await mermaid.default.run({ nodes: document.querySelectorAll(".mermaid") });
    } catch (e) {
      console.warn("Mermaid init failed:", e);
    }
  }

  function apply(theme) {
    root.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
    if (btn) btn.textContent = theme === "light" ? "Light" : "Dark";
  }

  btn?.addEventListener("click", () => {
    const next = (root.getAttribute("data-theme") || "light") === "light" ? "dark" : "light";
    apply(next);
  });

  apply(current);
  initMermaid();
})();
