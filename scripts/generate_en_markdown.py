from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENTS_DIR = ROOT / "contents"

TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"
CODE_RE = re.compile(r"`[^`]*`")
ZH_RE = re.compile(r"[\u4e00-\u9fff]")


def has_zh(text: str) -> bool:
    return bool(ZH_RE.search(text))


def google_translate(text: str, src: str = "zh-CN", dst: str = "en") -> str:
    if not text.strip():
        return text
    query = urllib.parse.urlencode(
        {
            "client": "gtx",
            "sl": src,
            "tl": dst,
            "dt": "t",
            "q": text,
        }
    )
    url = f"{TRANSLATE_URL}?{query}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    translated = "".join(part[0] for part in data[0] if part and part[0])
    return translated


def protect_inline_code(line: str) -> tuple[str, dict[str, str]]:
    mapping: dict[str, str] = {}

    def repl(match: re.Match[str]) -> str:
        key = f"__CODE_{len(mapping)}__"
        mapping[key] = match.group(0)
        return key

    return CODE_RE.sub(repl, line), mapping


def restore_inline_code(line: str, mapping: dict[str, str]) -> str:
    for k, v in mapping.items():
        line = line.replace(k, v)
    return line


def translate_table_line(line: str) -> str:
    parts = line.split("|")
    out = []
    for p in parts:
        if has_zh(p):
            p2, code_map = protect_inline_code(p)
            try:
                translated = google_translate(p2.strip())
                translated = restore_inline_code(translated, code_map)
                # keep surrounding spaces if any
                left = len(p) - len(p.lstrip(" "))
                right = len(p) - len(p.rstrip(" "))
                p = (" " * left) + translated + (" " * right)
            except Exception:
                pass
            time.sleep(0.08)
        out.append(p)
    return "|".join(out)


def translate_markdown_body(body: str) -> str:
    lines = body.splitlines()
    out: list[str] = []
    in_code = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            out.append(line)
            continue
        if in_code or not has_zh(line):
            out.append(line)
            continue

        # Markdown table separator rows should remain unchanged
        if stripped.startswith("|") and re.fullmatch(r"[\|\-\:\s]+", stripped):
            out.append(line)
            continue

        # translate table content cell by cell
        if stripped.startswith("|"):
            out.append(translate_table_line(line))
            continue

        # keep list/header markers and translate the text part
        m = re.match(r"^(\s*(?:#{1,6}\s+|[-*+]\s+|\d+\.\s+|>\s+)?)?(.*)$", line)
        prefix = m.group(1) or ""
        content = m.group(2) or ""
        if not content.strip():
            out.append(line)
            continue
        protected, code_map = protect_inline_code(content)
        try:
            translated = google_translate(protected.strip())
            translated = restore_inline_code(translated, code_map)
            out.append(prefix + translated)
        except Exception:
            out.append(line)
        time.sleep(0.08)
    return "\n".join(out).strip() + "\n"


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        raise ValueError("Missing front matter")
    _, rest = text.split("---\n", 1)
    fm, body = rest.split("\n---\n", 1)
    meta = yaml.safe_load(fm)
    return meta, body


def dump_doc(meta: dict[str, Any], body: str) -> str:
    fm = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True, width=120)
    return f"---\n{fm}---\n\n{body.strip()}\n"


def main() -> None:
    zh_files = [p for p in CONTENTS_DIR.rglob("*.md") if not p.name.endswith("_EN.md")]
    generated = 0
    for path in zh_files:
        text = path.read_text(encoding="utf-8").lstrip("\ufeff")
        meta, body = parse_frontmatter(text)
        if str(meta.get("lang", "")).lower().startswith("en"):
            continue

        out_path = path.with_name(path.stem + "_EN.md")

        en_meta = dict(meta)
        if has_zh(str(meta.get("title", ""))):
            try:
                en_meta["title"] = google_translate(str(meta["title"]))
                time.sleep(0.08)
            except Exception:
                pass
        if has_zh(str(meta.get("summary", ""))):
            try:
                en_meta["summary"] = google_translate(str(meta["summary"]))
                time.sleep(0.08)
            except Exception:
                pass
        en_meta["lang"] = "en"
        en_meta["translation_of"] = meta.get("slug")

        en_body = translate_markdown_body(body)
        out_path.write_text(dump_doc(en_meta, en_body), encoding="utf-8")
        generated += 1
        print(f"Generated {out_path.relative_to(ROOT)}")

    print(f"Done. Generated {generated} EN markdown files.")


if __name__ == "__main__":
    main()

