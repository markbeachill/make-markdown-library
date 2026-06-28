#!/usr/bin/env python3
"""Build the checked-in static HTML documentation site from docs/*.md.

The project keeps Markdown docs for editing and agent workflows, and generated
HTML docs for users who want a browsable multi-page site without installing
MkDocs. This generator intentionally uses only the Python standard library.
"""
from __future__ import annotations

import html
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITE = ROOT / "site"

@dataclass(frozen=True)
class Page:
    title: str
    source: str
    output: str
    group: str = "Docs"
    description: str = ""

PAGES = [
    Page("What is Make Markdown Library?", "index.md", "index.html", "Overview", "Project overview and workflow."),
    Page("Getting started", "getting-started.md", "getting-started/index.html", "Overview", "Install, build, and inspect your first library."),
    Page("Processing rules", "processing-rules.md", "processing-rules/index.html", "Overview", "The safety and behaviour contract."),
    Page("CLI reference", "cli-reference.md", "cli-reference/index.html", "Reference", "Complete command and option reference."),
    Page("Output reference", "output-reference.md", "output-reference/index.html", "Reference", "Generated files, index schema, and split outputs."),
    Page("Converter modes", "guides/converter-modes.md", "guides/converter-modes/index.html", "Guides", "MarkItDown, LiteParse, auto, and hybrid routing."),
    Page("LiteParse fallback", "guides/liteparse-fallback.md", "guides/liteparse-fallback/index.html", "Guides", "Fallback and PDF complexity routing."),
    Page("Markdown folders", "guides/markdown-folders.md", "guides/markdown-folders/index.html", "Guides", "Existing Markdown, generated files, and repeat runs."),
    Page("OCR, PDFs, and images", "guides/ocr-and-pdfs.md", "guides/ocr-and-pdfs/index.html", "Guides", "Scanned PDFs, image-heavy docs, and LiteParse options."),
    Page("JSON and YAML indexes", "guides/indexes-json-yaml.md", "guides/indexes-json-yaml/index.html", "Guides", "Machine-readable build metadata."),
    Page("Rebuilding libraries", "guides/rebuilding-libraries.md", "guides/rebuilding-libraries/index.html", "Guides", "Rebuild from a JSON index."),
    Page("GUI usage", "guides/gui-usage.md", "guides/gui-usage/index.html", "Guides", "Using the Tkinter interface."),
    Page("Agent workflows", "guides/agent-workflows.md", "guides/agent-workflows/index.html", "Guides", "Using libraries and llms.txt with agents."),
    Page("Static HTML site", "guides/static-html-site.md", "guides/static-html-site/index.html", "Guides", "Markdown source vs generated HTML docs."),
    Page("GitHub Pages deployment", "guides/github-pages.md", "guides/github-pages/index.html", "Guides", "Deploy the generated HTML docs with GitHub Actions."),
    Page("Troubleshooting", "troubleshooting.md", "troubleshooting/index.html", "Reference", "Common failure modes and fixes."),
]

SLUG_RE = re.compile(r"[^a-z0-9]+")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+\.md)(#[^)]+)?\)")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")


def slugify(text: str) -> str:
    slug = SLUG_RE.sub("-", text.lower()).strip("-")
    return slug or "section"


def page_url_for_source(source: str) -> str:
    source_norm = str(Path(source).as_posix())
    for page in PAGES:
        if page.source == source_norm:
            return root_relative(page.output)
    return root_relative("index.html")


def root_relative(output: str) -> str:
    return "/" + output.replace("index.html", "").rstrip("/") if output != "index.html" else "/"


def relative_link(from_output: str, to_output: str) -> str:
    from_dir = Path(from_output).parent
    rel = Path("/")
    # Use posix relative paths for static local browsing.
    target = Path(to_output)
    if from_dir == Path("."):
        return target.as_posix()
    return Path(*([".."] * len(from_dir.parts)), target).as_posix()


def rewrite_links(text: str, current_source: str, current_output: str) -> str:
    current_dir = (DOCS / current_source).parent

    def repl(match: re.Match[str]) -> str:
        label, href, anchor = match.group(1), match.group(2), match.group(3) or ""
        target_source = (current_dir / href).resolve().relative_to(DOCS.resolve()).as_posix() if not href.startswith("/") else href.lstrip("/")
        for page in PAGES:
            if page.source == target_source:
                return f"[{label}]({relative_link(current_output, page.output)}{anchor})"
        return match.group(0)
    return MD_LINK_RE.sub(repl, text)


def inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = BOLD_RE.sub(r"<strong>\1</strong>", escaped)
    escaped = INLINE_CODE_RE.sub(lambda m: f"<code>{m.group(1)}</code>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>', escaped)
    return escaped


def render_table(lines: list[str]) -> str:
    header = [cell.strip() for cell in lines[0].strip().strip("|").split("|")]
    rows = []
    for raw in lines[2:]:
        rows.append([cell.strip() for cell in raw.strip().strip("|").split("|")])
    out = ["<div class=\"table-wrap\"><table>", "<thead><tr>"]
    out += [f"<th>{inline(cell)}</th>" for cell in header]
    out.append("</tr></thead><tbody>")
    for row in rows:
        out.append("<tr>")
        out += [f"<td>{inline(cell)}</td>" for cell in row]
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "\n".join(out)


def is_table_start(lines: list[str], i: int) -> bool:
    return i + 1 < len(lines) and "|" in lines[i] and re.match(r"^\s*\|?\s*:?-{3,}:?", lines[i + 1]) is not None


def render_markdown(markdown: str, current_source: str, current_output: str) -> tuple[str, list[tuple[int, str, str]]]:
    markdown = rewrite_links(markdown, current_source, current_output)
    lines = markdown.splitlines()
    out: list[str] = []
    toc: list[tuple[int, str, str]] = []
    i = 0
    in_code = False
    code_lang = ""
    code_lines: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []

    def flush_para() -> None:
        nonlocal paragraph
        if paragraph:
            out.append(f"<p>{inline(' '.join(paragraph))}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            out.append("<ul>" + "".join(f"<li>{inline(item)}</li>" for item in list_items) + "</ul>")
            list_items = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            if not in_code:
                flush_para(); flush_list()
                in_code = True
                code_lang = stripped[3:].strip()
                code_lines = []
            else:
                code_text = html.escape("\n".join(code_lines))
                lang = f" data-lang=\"{html.escape(code_lang, quote=True)}\"" if code_lang else ""
                out.append(f"<div class=\"code-card\"{lang}><button class=\"copy\" type=\"button\">Copy</button><pre><code>{code_text}</code></pre></div>")
                in_code = False
                code_lang = ""
                code_lines = []
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        if not stripped:
            flush_para(); flush_list(); i += 1; continue

        if is_table_start(lines, i):
            flush_para(); flush_list()
            table_lines = [lines[i], lines[i+1]]
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                table_lines.append(lines[i]); i += 1
            out.append(render_table(table_lines))
            continue

        if stripped.startswith("#"):
            flush_para(); flush_list()
            level = len(stripped) - len(stripped.lstrip("#"))
            title = stripped[level:].strip()
            anchor = slugify(title)
            if level <= 3:
                toc.append((level, title, anchor))
            out.append(f"<h{level} id=\"{anchor}\"><a class=\"anchor\" href=\"#{anchor}\">#</a>{inline(title)}</h{level}>")
            i += 1
            continue

        if stripped.startswith("- "):
            flush_para()
            list_items.append(stripped[2:].strip())
            i += 1
            continue

        if re.match(r"^\d+\.\s+", stripped):
            flush_para(); flush_list()
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            out.append("<ol>" + "".join(f"<li>{inline(item)}</li>" for item in items) + "</ol>")
            continue

        if stripped.startswith("> "):
            flush_para(); flush_list()
            out.append(f"<blockquote>{inline(stripped[2:].strip())}</blockquote>")
            i += 1
            continue

        paragraph.append(stripped)
        i += 1

    flush_para(); flush_list()
    return "\n".join(out), toc


def nav_html(current_output: str) -> str:
    groups: dict[str, list[Page]] = {}
    for page in PAGES:
        groups.setdefault(page.group, []).append(page)
    parts = []
    for group, pages in groups.items():
        parts.append(f"<div class=\"nav-group\"><div class=\"nav-title\">{html.escape(group)}</div>")
        for page in pages:
            href = relative_link(current_output, page.output)
            active = " active" if page.output == current_output else ""
            parts.append(f'<a class="nav-link{active}" href="{href}">{html.escape(page.title)}</a>')
        parts.append("</div>")
    return "\n".join(parts)


def toc_html(toc: list[tuple[int, str, str]]) -> str:
    if not toc:
        return '<p class="muted">No headings on this page.</p>'
    parts = []
    for level, title, anchor in toc:
        if level == 1:
            continue
        parts.append(f'<a class="toc-link depth-{level}" href="#{anchor}">{html.escape(title)}</a>')
    return "\n".join(parts) or '<p class="muted">No headings on this page.</p>'


def template(page: Page, body: str, toc: list[tuple[int, str, str]]) -> str:
    css = relative_link(page.output, "assets/docs.css")
    js = relative_link(page.output, "assets/docs.js")
    raw_link = relative_link(page.output, f"../docs/{page.source}")
    llms = relative_link(page.output, "llms.txt")
    home = relative_link(page.output, "index.html")
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{html.escape(page.title)} · Make Markdown Library</title>
  <meta name=\"description\" content=\"{html.escape(page.description, quote=True)}\">
  <link rel=\"stylesheet\" href=\"{css}\">
</head>
<body>
  <header class=\"topbar\">
    <a class=\"brand\" href=\"{home}\"><span class=\"brand-mark\">M↓</span><span>Make Markdown Library</span></a>
    <div class=\"top-actions\">
      <input class=\"search\" id=\"search\" type=\"search\" placeholder=\"Search docs…\" aria-label=\"Search docs\">
      <a class=\"pill\" href=\"{llms}\">llms.txt</a>
      <button class=\"pill\" id=\"theme-toggle\" type=\"button\">Theme</button>
    </div>
  </header>
  <div class=\"layout\">
    <aside class=\"sidebar\">
      <div class=\"side-heading\">Documentation</div>
      {nav_html(page.output)}
    </aside>
    <main class=\"content\">
      <div class=\"page-toolbar\">
        <span class=\"eyebrow\">{html.escape(page.group)}</span>
        <span class=\"toolbar-links\"><a href=\"{raw_link}\">View Markdown</a><button class=\"copy-page\" type=\"button\" data-raw=\"{raw_link}\">Copy Markdown path</button></span>
      </div>
      <article class=\"doc-card\">
        {body}
      </article>
      <nav class=\"pager\">{pager(page)}</nav>
    </main>
    <aside class=\"toc\">
      <div class=\"side-heading\">On this page</div>
      {toc_html(toc)}
    </aside>
  </div>
  <script src=\"{js}\"></script>
</body>
</html>
"""


def pager(page: Page) -> str:
    idx = PAGES.index(page)
    prev_html = ""
    next_html = ""
    if idx > 0:
        prev = PAGES[idx-1]
        prev_html = f'<a class="pager-item" href="{relative_link(page.output, prev.output)}"><span>Previous</span><strong>{html.escape(prev.title)}</strong></a>'
    if idx + 1 < len(PAGES):
        nxt = PAGES[idx+1]
        next_html = f'<a class="pager-item next" href="{relative_link(page.output, nxt.output)}"><span>Next</span><strong>{html.escape(nxt.title)}</strong></a>'
    return prev_html + next_html


def write_assets() -> None:
    assets = SITE / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / "docs.css").write_text(CSS)
    (assets / "docs.js").write_text(JS)


def main() -> None:
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)
    write_assets()
    search_items = []
    for page in PAGES:
        source_path = DOCS / page.source
        md = source_path.read_text()
        body, toc = render_markdown(md, page.source, page.output)
        output_path = SITE / page.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(template(page, body, toc))
        search_items.append({"title": page.title, "url": page.output, "description": page.description, "source": page.source})
    (SITE / "search-index.json").write_text(json.dumps(search_items, indent=2))
    if (ROOT / "llms.txt").exists():
        shutil.copyfile(ROOT / "llms.txt", SITE / "llms.txt")


CSS = r'''
:root {
  --bg: #f8fafc;
  --panel: #ffffff;
  --text: #182230;
  --muted: #667085;
  --line: #e4e7ec;
  --accent: #635bff;
  --accent-2: #0ea5e9;
  --code-bg: #0f172a;
  --code-text: #e5e7eb;
  --shadow: 0 12px 36px rgba(15, 23, 42, .08);
}
[data-theme="dark"] {
  --bg: #0b1020;
  --panel: #111827;
  --text: #e5e7eb;
  --muted: #9ca3af;
  --line: #253047;
  --accent: #8b7cff;
  --accent-2: #38bdf8;
  --code-bg: #020617;
  --code-text: #f8fafc;
  --shadow: 0 16px 50px rgba(0, 0, 0, .35);
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: var(--bg); color: var(--text); font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.topbar { position: sticky; top: 0; z-index: 20; height: 64px; display: flex; align-items: center; justify-content: space-between; gap: 20px; padding: 0 24px; border-bottom: 1px solid var(--line); background: color-mix(in srgb, var(--panel), transparent 7%); backdrop-filter: blur(12px); }
.brand { display: flex; align-items: center; gap: 10px; font-weight: 760; color: var(--text); }
.brand:hover { text-decoration: none; }
.brand-mark { display: inline-grid; place-items: center; width: 34px; height: 34px; border-radius: 10px; color: #fff; background: linear-gradient(135deg, var(--accent), var(--accent-2)); font-size: 13px; font-weight: 800; }
.top-actions { display: flex; align-items: center; gap: 10px; }
.search { width: min(320px, 36vw); border: 1px solid var(--line); border-radius: 999px; background: var(--bg); color: var(--text); padding: 10px 14px; }
.pill, .copy-page { border: 1px solid var(--line); background: var(--panel); color: var(--text); border-radius: 999px; padding: 9px 12px; font: inherit; cursor: pointer; }
.layout { display: grid; grid-template-columns: 280px minmax(0, 1fr) 240px; gap: 28px; max-width: 1480px; margin: 0 auto; padding: 28px 28px 48px; }
.sidebar, .toc { position: sticky; top: 92px; align-self: start; max-height: calc(100vh - 112px); overflow: auto; }
.side-heading { font-size: 12px; letter-spacing: .08em; color: var(--muted); text-transform: uppercase; font-weight: 800; margin: 0 0 14px; }
.nav-group { margin: 0 0 22px; }
.nav-title { color: var(--muted); font-size: 13px; font-weight: 700; margin: 0 0 6px; }
.nav-link { display: block; color: var(--text); padding: 8px 10px; border-radius: 10px; font-size: 14px; }
.nav-link:hover { background: color-mix(in srgb, var(--accent), transparent 92%); text-decoration: none; }
.nav-link.active { color: var(--accent); background: color-mix(in srgb, var(--accent), transparent 88%); font-weight: 700; }
.content { min-width: 0; }
.page-toolbar { display: flex; align-items: center; justify-content: space-between; gap: 18px; margin-bottom: 14px; }
.eyebrow { color: var(--accent); font-size: 13px; font-weight: 800; text-transform: uppercase; letter-spacing: .08em; }
.toolbar-links { display: flex; align-items: center; gap: 10px; font-size: 13px; }
.doc-card { background: var(--panel); border: 1px solid var(--line); border-radius: 22px; padding: clamp(26px, 4vw, 54px); box-shadow: var(--shadow); }
.doc-card h1 { margin-top: 0; font-size: clamp(2.15rem, 4vw, 4.2rem); line-height: 1.02; letter-spacing: -.045em; }
.doc-card h2 { margin-top: 2.2em; padding-top: .6em; border-top: 1px solid var(--line); font-size: clamp(1.45rem, 2vw, 2rem); }
.doc-card h3 { margin-top: 1.8em; font-size: 1.2rem; }
.doc-card p, .doc-card li { line-height: 1.72; color: color-mix(in srgb, var(--text), var(--muted) 12%); }
.doc-card ul { padding-left: 1.2rem; }
.anchor { opacity: 0; margin-left: -1.05em; padding-right: .25em; }
h1:hover .anchor, h2:hover .anchor, h3:hover .anchor { opacity: 1; }
.code-card { position: relative; margin: 18px 0; border-radius: 16px; overflow: hidden; border: 1px solid color-mix(in srgb, var(--line), #000 15%); background: var(--code-bg); }
.code-card::before { content: attr(data-lang); position: absolute; top: 10px; left: 14px; color: #94a3b8; font: 12px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; text-transform: uppercase; }
pre { margin: 0; padding: 38px 18px 18px; overflow-x: auto; }
code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; font-size: .92em; }
pre code { color: var(--code-text); }
:not(pre) > code { background: color-mix(in srgb, var(--accent), transparent 90%); color: var(--text); padding: .15em .35em; border-radius: 6px; }
.copy { position: absolute; top: 8px; right: 8px; border: 1px solid rgba(255,255,255,.16); background: rgba(255,255,255,.08); color: #e5e7eb; border-radius: 999px; padding: 6px 10px; cursor: pointer; }
.table-wrap { overflow-x: auto; margin: 20px 0; border: 1px solid var(--line); border-radius: 16px; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th, td { padding: 12px 14px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
th { background: color-mix(in srgb, var(--accent), transparent 94%); font-weight: 760; }
tr:last-child td { border-bottom: 0; }
blockquote { margin: 20px 0; padding: 14px 18px; border-left: 4px solid var(--accent); background: color-mix(in srgb, var(--accent), transparent 93%); border-radius: 12px; }
.toc-link { display: block; color: var(--muted); padding: 6px 0; font-size: 13px; }
.toc-link.depth-3 { padding-left: 14px; }
.muted { color: var(--muted); }
.pager { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 22px 0 0; }
.pager-item { display: block; padding: 16px; border: 1px solid var(--line); border-radius: 16px; background: var(--panel); color: var(--text); }
.pager-item span { display: block; color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .08em; margin-bottom: 4px; }
.pager-item.next { text-align: right; grid-column: 2; }
.pager-item:hover { text-decoration: none; border-color: color-mix(in srgb, var(--accent), var(--line) 55%); }
@media (max-width: 1100px) { .layout { grid-template-columns: 240px minmax(0, 1fr); } .toc { display: none; } }
@media (max-width: 780px) { .topbar { height: auto; padding: 14px; align-items: flex-start; flex-direction: column; } .top-actions { width: 100%; flex-wrap: wrap; } .search { width: 100%; } .layout { display: block; padding: 18px; } .sidebar { position: static; max-height: none; margin-bottom: 18px; } .page-toolbar { align-items: flex-start; flex-direction: column; } .pager { grid-template-columns: 1fr; } .pager-item.next { grid-column: 1; text-align: left; } }
'''

JS = r'''
(function () {
  const root = document.documentElement;
  const saved = localStorage.getItem('mml-docs-theme');
  if (saved) root.setAttribute('data-theme', saved);
  document.getElementById('theme-toggle')?.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('mml-docs-theme', next);
  });
  document.querySelectorAll('.copy').forEach((button) => {
    button.addEventListener('click', async () => {
      const code = button.parentElement.querySelector('code')?.innerText || '';
      await navigator.clipboard?.writeText(code);
      button.textContent = 'Copied';
      setTimeout(() => button.textContent = 'Copy', 1200);
    });
  });
  document.querySelectorAll('.copy-page').forEach((button) => {
    button.addEventListener('click', async () => {
      await navigator.clipboard?.writeText(button.getAttribute('data-raw') || '');
      button.textContent = 'Copied';
      setTimeout(() => button.textContent = 'Copy Markdown path', 1200);
    });
  });
  const search = document.getElementById('search');
  search?.addEventListener('input', () => {
    const q = search.value.toLowerCase().trim();
    document.querySelectorAll('.nav-link').forEach((link) => {
      const hit = !q || link.textContent.toLowerCase().includes(q);
      link.style.display = hit ? 'block' : 'none';
    });
  });
})();
'''

if __name__ == "__main__":
    main()
