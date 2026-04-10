from __future__ import annotations

import html
import shutil
from pathlib import Path
from typing import Any

import markdown
import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENTS_DIR = ROOT / "contents"
SITE_DIR = ROOT / "html-site"

TRACK_ORDER = ["map", "mechanism", "decision", "build"]

TRACK_META = {
    "en": {
        "map": {"title": "Map", "desc": "Reading path, glossary, and evidence rules."},
        "mechanism": {"title": "Mechanism", "desc": "Runtime, tools, permissions, and compaction."},
        "decision": {"title": "Decision", "desc": "Why the architecture is shaped this way."},
        "build": {"title": "Build", "desc": "Implementation playbooks and checklists."},
    },
    "zh": {
        "map": {"title": "地图", "desc": "阅读路径、术语、证据规范。"},
        "mechanism": {"title": "机制", "desc": "运行时、工具、权限、压缩机制。"},
        "decision": {"title": "决策", "desc": "为什么这样设计，以及关键权衡。"},
        "build": {"title": "复建", "desc": "最小实现方案与工程清单。"},
    },
}

UI_TEXT = {
    "en": {
        "lang_code": "en",
        "home": "Home",
        "recommended": "Recommended Start",
        "tracks": "Tracks",
        "site_title": "Lessons from Claude Code",
        "site_intro": "A developer-focused architecture analysis site generated from markdown.",
        "track_back": "Back to",
        "track_nav": "Track Articles",
        "prereq": "Prerequisites",
        "anchors": "Code Anchors",
        "none": "None",
        "updated": "Updated",
        "source": "Source markdown:",
        "to_zh": "中文",
    },
    "zh": {
        "lang_code": "zh-CN",
        "home": "首页",
        "recommended": "推荐先读",
        "tracks": "阅读轨道",
        "site_title": "Lessons from Claude Code",
        "site_intro": "面向开发者的架构分析站，网页由 markdown 自动生成。",
        "track_back": "返回",
        "track_nav": "同轨文章",
        "prereq": "前置阅读",
        "anchors": "代码锚点",
        "none": "无",
        "updated": "更新",
        "source": "Markdown 源文件：",
        "to_zh": "English",
    },
}


def parse_doc(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8").lstrip("\ufeff")
    if not text.startswith("---\n"):
        raise ValueError(f"Missing front matter: {path}")
    _, rest = text.split("---\n", 1)
    fm, body = rest.split("\n---\n", 1)
    meta = yaml.safe_load(fm)
    meta["body"] = body.strip()
    meta["path"] = path
    return meta


def load_docs() -> list[dict[str, Any]]:
    docs = [parse_doc(p) for p in sorted(CONTENTS_DIR.rglob("*.md"))]
    docs.sort(key=lambda d: (d.get("order", 999), d["slug"]))
    return docs


def split_docs_by_lang(docs: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {"en": [], "zh": []}
    for d in docs:
        lang = str(d.get("lang", "zh-CN")).lower()
        key = "en" if lang.startswith("en") else "zh"
        out[key].append(d)
    for key in out:
        out[key].sort(key=lambda x: (x.get("order", 999), x["slug"]))
    return out


def md_to_html(text: str) -> str:
    return markdown.markdown(
        text,
        extensions=["fenced_code", "tables", "sane_lists"],
        output_format="html5",
    )


def ensure_clean_site() -> None:
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    (SITE_DIR / "assets").mkdir(parents=True, exist_ok=True)
    (SITE_DIR / "articles").mkdir(parents=True, exist_ok=True)
    (SITE_DIR / "zh" / "articles").mkdir(parents=True, exist_ok=True)


def nav_html(lang: str, active: str, prefix: str) -> str:
    t = UI_TEXT[lang]
    track = TRACK_META[lang]

    def item(key: str, href: str, label: str) -> str:
        cls = "active" if active == key else ""
        return f'<a class="{cls}" href="{href}">{label}</a>'

    return "".join(
        [
            item("home", f"{prefix}index.html", t["home"]),
            item("map", f"{prefix}map.html", track["map"]["title"]),
            item("mechanism", f"{prefix}mechanism.html", track["mechanism"]["title"]),
            item("decision", f"{prefix}decision.html", track["decision"]["title"]),
            item("build", f"{prefix}build.html", track["build"]["title"]),
        ]
    )


def render_layout(
    *,
    lang: str,
    title: str,
    active: str,
    content: str,
    asset_prefix: str,
    nav_prefix: str,
    switch_href: str,
) -> str:
    t = UI_TEXT[lang]
    switch_label = t["to_zh"]
    return f"""<!doctype html>
<html lang="{t['lang_code']}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="{asset_prefix}assets/style.css" />
  <script defer src="{asset_prefix}assets/site.js"></script>
</head>
<body>
  <header class="site-header">
    <div class="container site-header-inner">
      <a class="brand" href="{nav_prefix}index.html">Lessons from Claude Code</a>
      <div class="controls">
        <a class="toggle-btn" href="{switch_href}">{switch_label}</a>
        <button id="theme-toggle" class="toggle-btn" type="button">Light</button>
      </div>
      <nav class="nav" aria-label="Main">{nav_html(lang, active, nav_prefix)}</nav>
    </div>
  </header>
  <main class="main"><div class="container">{content}</div></main>
</body>
</html>
"""


def render_index(lang: str, docs: list[dict[str, Any]], switch_href: str) -> str:
    t = UI_TEXT[lang]
    track = TRACK_META[lang]
    cards = []
    for key in TRACK_ORDER:
        count = len([d for d in docs if d["track"] == key])
        cards.append(
            f"<a class='card' href='{key}.html'><h3>{track[key]['title']}</h3>"
            f"<p class='lead'>{track[key]['desc']}</p>"
            f"<div class='meta'><span class='badge'>{count} {'articles' if lang == 'en' else '篇'}</span></div></a>"
        )
    featured = "".join(
        f"<a class='card' href='articles/{d['slug']}.html'><h3>{html.escape(d['title'])}</h3>"
        f"<p class='lead'>{html.escape(d['summary'])}</p>"
        f"<div class='meta'><span class='badge'>{d['track']}</span><span class='badge'>{d['level']}</span></div></a>"
        for d in docs[:4]
    )
    body = f"""
<section class="hero">
  <h1>{t['site_title']}</h1>
  <p>{t['site_intro']}</p>
</section>
<section class="section">
  <h2>{t['tracks']}</h2>
  <div class="grid">{''.join(cards)}</div>
</section>
<section class="section">
  <h2>{t['recommended']}</h2>
  <div class="grid">{featured}</div>
</section>
""".strip()
    return render_layout(
        lang=lang,
        title=t["home"],
        active="home",
        content=body,
        asset_prefix="" if lang == "en" else "../",
        nav_prefix="",
        switch_href=switch_href,
    )


def render_track(lang: str, track_key: str, docs: list[dict[str, Any]], switch_href: str) -> str:
    track = TRACK_META[lang][track_key]
    cards = []
    for d in docs:
        tags = "".join(f"<span class='tag'>{html.escape(tag)}</span>" for tag in d.get("tags", []))
        cards.append(
            f"<a class='card' href='articles/{d['slug']}.html'><h3>{html.escape(d['title'])}</h3>"
            f"<p class='lead'>{html.escape(d['summary'])}</p>"
            f"<div class='meta'><span class='badge'>{d['depth']}</span><span class='badge'>{d['evidence_level']}</span></div>"
            f"<div class='meta'>{tags}</div></a>"
        )
    body = f"""
<section class="hero">
  <h1>{track['title']}</h1>
  <p>{track['desc']}</p>
</section>
<section class="section">
  <div class="grid">{''.join(cards)}</div>
</section>
""".strip()
    return render_layout(
        lang=lang,
        title=track["title"],
        active=track_key,
        content=body,
        asset_prefix="" if lang == "en" else "../",
        nav_prefix="",
        switch_href=switch_href,
    )


def render_article(lang: str, doc: dict[str, Any], peers: list[dict[str, Any]], switch_href: str) -> str:
    t = UI_TEXT[lang]
    track_key = doc["track"]
    track_title = TRACK_META[lang][track_key]["title"]

    side_links = "".join(
        f"<a class='{'active' if p['slug'] == doc['slug'] else ''}' href='{p['slug']}.html'>{html.escape(p['title'])}</a>"
        for p in peers
    )
    prereq = doc.get("prerequisites", [])
    prereq_html = "".join(f"<li><a href='{slug}.html'><code>{slug}</code></a></li>" for slug in prereq) or f"<li class='lead'>{t['none']}</li>"
    anchors = "".join(
        "<li><code>{}</code><br/><span class='lead'>{}</span></li>".format(
            html.escape(a.get("path", "")),
            html.escape(", ".join(a.get("symbols", []))),
        )
        for a in doc.get("code_anchors", [])
    )

    sidebar = f"""
<aside class="article-sidebar">
  <h3>{track_title}</h3>
  <p class="lead"><a href="../{track_key}.html">{t['track_back']} {track_title}</a></p>
  <h3>{t['track_nav']}</h3>
  <nav class="sidebar-nav">{side_links}</nav>
  <h3>{t['prereq']}</h3>
  <ul>{prereq_html}</ul>
  <h3>{t['anchors']}</h3>
  <ul>{anchors}</ul>
</aside>
""".strip()

    tags = "".join(f"<span class='tag'>{html.escape(tag)}</span>" for tag in doc.get("tags", []))
    body_html = md_to_html(doc["body"])
    content = f"""
<p class="lead"><a href="../{track_key}.html">{t['track_back']} {track_title}</a></p>
<div class="article-layout">
  {sidebar}
  <article class="article">
    <h1>{html.escape(doc['title'])}</h1>
    <p class="lead">{html.escape(doc['summary'])}</p>
    <div class="meta">
      <span class="badge">{doc['level']}</span>
      <span class="badge">{doc['depth']}</span>
      <span class="badge">{doc['evidence_level']}</span>
      <span class="badge">{t['updated']} {doc['updatedAt']}</span>
    </div>
    <div class="meta">{tags}</div>
    <div class="article-body">{body_html}</div>
    <p class="footer">{t['source']} <code>{doc['path'].relative_to(ROOT).as_posix()}</code></p>
  </article>
</div>
""".strip()
    return render_layout(
        lang=lang,
        title=doc["title"],
        active=track_key,
        content=content,
        asset_prefix="../" if lang == "en" else "../../",
        nav_prefix="../",
        switch_href=switch_href,
    )


def write_assets() -> None:
    css = """
:root{--bg:#f5f7fb;--surface:#fff;--text:#0f172a;--muted:#475569;--border:#dbe2ea;--accent:#0b7a75}
[data-theme="dark"]{--bg:#0b1320;--surface:#111b2b;--text:#e2e8f0;--muted:#9aa9bd;--border:#263244;--accent:#5be0d6}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:"IBM Plex Sans","Segoe UI",system-ui,-apple-system,sans-serif}
a{text-decoration:none;color:inherit}
.container{max-width:1080px;margin:0 auto;padding:0 1rem}
.site-header{position:sticky;top:0;z-index:20;background:var(--surface);border-bottom:1px solid var(--border)}
.site-header-inner{display:flex;flex-wrap:wrap;gap:.7rem;align-items:center;padding:.85rem 0}
.brand{font-weight:700;font-size:1.08rem}
.controls{margin-left:auto;display:flex;gap:.45rem;align-items:center}
.toggle-btn{border:1px solid var(--border);background:var(--surface);border-radius:999px;padding:.3rem .72rem;cursor:pointer;font-size:.92rem}
.nav{width:100%;display:flex;gap:.45rem;flex-wrap:wrap}
.nav a{color:var(--muted);border:1px solid transparent;border-radius:999px;padding:.32rem .62rem}
.nav a.active{color:var(--text);font-weight:600;border-color:var(--accent)}
.main{padding:2rem 0 3rem}
.hero{border:1px solid var(--border);background:var(--surface);border-radius:14px;padding:1.25rem}
.hero h1{margin:0 0 .6rem;font-size:clamp(1.55rem,3vw,2.1rem)}
.hero p{margin:0;color:var(--muted);line-height:1.65}
.section{margin-top:1.2rem}
.section h2{margin:0 0 .65rem}
.grid{display:grid;gap:.9rem;grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.card{border:1px solid var(--border);background:var(--surface);border-radius:12px;padding:.95rem}
.card h3{margin:0 0 .45rem;font-size:1.03rem}
.lead{color:var(--muted);font-size:.95rem;line-height:1.62}
.meta{display:flex;gap:.4rem;flex-wrap:wrap;margin-top:.6rem}
.badge,.tag{border:1px solid var(--border);border-radius:999px;font-size:.75rem;padding:.16rem .52rem}
.article-layout{display:grid;gap:1rem;grid-template-columns:1fr}
.article-layout>*{min-width:0}
.article,.article-sidebar{border:1px solid var(--border);background:var(--surface);border-radius:14px}
.article{padding:1.25rem}
.article h1{margin:0 0 .6rem;font-size:clamp(1.4rem,2.6vw,1.9rem)}
.article h2{margin-top:1.35rem;font-size:1.1rem}
.article p,.article li{line-height:1.75;overflow-wrap:anywhere;word-break:break-word}
.article pre{background:#0b1020;color:#dbeafe;padding:.82rem;border-radius:10px;overflow:auto}
.article code{font-family:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;overflow-wrap:anywhere;word-break:break-word}
.mermaid{border:1px solid var(--border);background:var(--surface);border-radius:10px;padding:.6rem;overflow:auto;margin:.9rem 0}
.mermaid svg{display:block;max-width:100%;height:auto}
.article table{width:100%;border-collapse:collapse;margin:.9rem 0}
.article th,.article td{border:1px solid var(--border);padding:.45rem;text-align:left;vertical-align:top}
.article-sidebar{padding:.95rem}
.article-sidebar h3{margin:.25rem 0 .5rem;font-size:.94rem}
.sidebar-nav{display:flex;flex-direction:column;gap:.4rem}
.sidebar-nav a{color:var(--muted);font-size:.9rem;overflow-wrap:anywhere;word-break:break-word}
.sidebar-nav a.active{color:var(--text);font-weight:600}
.article-sidebar li{overflow-wrap:anywhere;word-break:break-word}
.article-sidebar code{overflow-wrap:anywhere;word-break:break-all}
.footer{margin-top:1rem;color:var(--muted);font-size:.83rem}
@media (min-width:960px){.article-layout{grid-template-columns:290px 1fr}.article-sidebar{position:sticky;top:6.2rem;height:fit-content}}
""".strip()

    js = """
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
""".strip()

    (SITE_DIR / "assets" / "style.css").write_text(css + "\n", encoding="utf-8")
    (SITE_DIR / "assets" / "site.js").write_text(js + "\n", encoding="utf-8")


def write_lang_site(lang: str, docs: list[dict[str, Any]]) -> None:
    if lang == "en":
        base = SITE_DIR
        switch_index = "zh/index.html"
        switch_track = "zh/{track}.html"
        switch_article = "../zh/articles/{slug}.html"
    else:
        base = SITE_DIR / "zh"
        base.mkdir(parents=True, exist_ok=True)
        (base / "articles").mkdir(parents=True, exist_ok=True)
        switch_index = "../index.html"
        switch_track = "../{track}.html"
        switch_article = "../../articles/{slug}.html"

    (base / "index.html").write_text(render_index(lang, docs, switch_href=switch_index), encoding="utf-8")

    for track in TRACK_ORDER:
        tdocs = [d for d in docs if d["track"] == track]
        (base / f"{track}.html").write_text(
            render_track(lang, track, tdocs, switch_href=switch_track.format(track=track)),
            encoding="utf-8",
        )
        for doc in tdocs:
            (base / "articles" / f"{doc['slug']}.html").write_text(
                render_article(lang, doc, tdocs, switch_href=switch_article.format(slug=doc["slug"])),
                encoding="utf-8",
            )


def main() -> None:
    all_docs = load_docs()
    by_lang = split_docs_by_lang(all_docs)
    zh_docs = by_lang["zh"]
    en_docs = by_lang["en"] if by_lang["en"] else []

    ensure_clean_site()
    write_assets()
    if not en_docs:
        raise RuntimeError("No English markdown found. Please generate *_EN.md files first.")
    write_lang_site("en", en_docs)  # default site root is English
    write_lang_site("zh", zh_docs)

    print(f"Generated {len(en_docs)} EN + {len(zh_docs)} ZH articles into {SITE_DIR}")


if __name__ == "__main__":
    main()
