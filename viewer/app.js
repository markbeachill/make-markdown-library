const state = {
  fileName: '',
  fullText: '',
  currentMarkdown: '',
  currentTitle: '',
  rawVisible: false,
  library: null,
};

const el = {
  fileInput: document.getElementById('fileInput'),
  openSample: document.getElementById('openSample'),
  sidebar: document.getElementById('sidebar'),
  fileLabel: document.getElementById('fileLabel'),
  documentTitle: document.getElementById('documentTitle'),
  rendered: document.getElementById('rendered'),
  raw: document.getElementById('raw'),
  toggleRaw: document.getElementById('toggleRaw'),
  copySection: document.getElementById('copySection'),
};

el.fileInput.addEventListener('change', async (event) => {
  const file = event.target.files && event.target.files[0];
  if (!file) return;
  const text = await file.text();
  loadMarkdown(text, file.name);
});

el.openSample.addEventListener('click', () => loadMarkdown(sampleLibrary(), 'sample-markdown-library.md'));
el.toggleRaw.addEventListener('click', toggleRaw);
el.copySection.addEventListener('click', copyCurrentSection);

function loadMarkdown(text, fileName) {
  state.fileName = fileName;
  state.fullText = text;
  state.rawVisible = false;
  state.library = parseLibrary(text);

  el.fileLabel.textContent = fileName;
  el.toggleRaw.disabled = false;
  el.copySection.disabled = false;
  el.raw.hidden = true;
  el.rendered.hidden = false;
  el.toggleRaw.textContent = 'Show raw';

  if (state.library) {
    renderLibrarySidebar(state.library);
    const first = state.library.sources[0];
    if (first) {
      selectSource(first.id);
    } else {
      showMarkdown(text, state.library.title || fileName);
    }
  } else {
    renderSingleSidebar(fileName);
    showMarkdown(stripFrontMatter(text), fileName);
  }
}

function parseLibrary(text) {
  const frontMatter = extractFrontMatter(text);
  const meta = frontMatter ? parseMmlibFrontMatter(frontMatter) : null;
  const markers = parseSourceMarkers(text);

  if (!meta && markers.length === 0) return null;

  const sourcesFromMeta = meta?.sources || [];
  const sources = sourcesFromMeta.length ? sourcesFromMeta : markers.map((m, idx) => ({
    id: m.id,
    title: m.title || `Source ${idx + 1}`,
    relative_path: m.path || '',
    converter: '',
    warnings: [],
  }));

  const byId = new Map(markers.map((m) => [m.id, m]));
  const mergedSources = sources.map((source, idx) => {
    const id = source.id || `src_${idx + 1}`;
    return {
      ...source,
      id,
      title: source.title || source.relative_path || id,
      marker: byId.get(id) || null,
    };
  });

  return {
    title: meta?.title || 'Markdown Library',
    description: meta?.description || '',
    category: meta?.category || '',
    built_at: meta?.built_at || '',
    converter_mode: meta?.converter_mode || '',
    markdown_policy: meta?.markdown_policy || '',
    sources: mergedSources,
    markers,
  };
}

function extractFrontMatter(text) {
  if (!text.startsWith('---\n')) return null;
  const end = text.indexOf('\n---', 4);
  if (end === -1) return null;
  return text.slice(4, end).trim();
}

function stripFrontMatter(text) {
  if (!text.startsWith('---\n')) return text;
  const end = text.indexOf('\n---', 4);
  if (end === -1) return text;
  return text.slice(end + 5).replace(/^\s+/, '');
}

function parseMmlibFrontMatter(yaml) {
  if (!/make_markdown_library\s*:/m.test(yaml)) return null;
  const lines = yaml.split(/\r?\n/);
  const meta = { sources: [] };
  let inMmlib = false;
  let inSources = false;
  let currentSource = null;

  for (const rawLine of lines) {
    const line = rawLine.replace(/\t/g, '    ');
    if (/^make_markdown_library\s*:/.test(line)) {
      inMmlib = true;
      continue;
    }
    if (!inMmlib) continue;

    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;

    if (/^sources\s*:/.test(trimmed)) {
      inSources = true;
      continue;
    }

    if (inSources) {
      const itemMatch = line.match(/^\s*-\s+([A-Za-z0-9_]+)\s*:\s*(.*)$/);
      const propMatch = line.match(/^\s+([A-Za-z0-9_]+)\s*:\s*(.*)$/);
      if (itemMatch) {
        currentSource = {};
        meta.sources.push(currentSource);
        currentSource[itemMatch[1]] = parseScalar(itemMatch[2]);
        continue;
      }
      if (propMatch && currentSource) {
        currentSource[propMatch[1]] = parseScalar(propMatch[2]);
        continue;
      }
      if (/^\S/.test(line)) inSources = false;
    }

    if (!inSources) {
      const keyMatch = trimmed.match(/^([A-Za-z0-9_]+)\s*:\s*(.*)$/);
      if (keyMatch) meta[keyMatch[1]] = parseScalar(keyMatch[2]);
    }
  }

  if (meta.type && String(meta.type).toLowerCase() !== 'library') return null;
  return meta;
}

function parseScalar(value) {
  const trimmed = String(value || '').trim();
  if (trimmed === '[]') return [];
  if (trimmed === 'true') return true;
  if (trimmed === 'false') return false;
  if ((trimmed.startsWith('"') && trimmed.endsWith('"')) || (trimmed.startsWith("'") && trimmed.endsWith("'"))) {
    return trimmed.slice(1, -1).replace(/\\"/g, '"');
  }
  return trimmed;
}

function parseSourceMarkers(text) {
  const startRegex = /<!--\s*mmlib:source-start\s+([^>]*)-->/g;
  const markers = [];
  let match;
  while ((match = startRegex.exec(text)) !== null) {
    const attrs = parseAttrs(match[1]);
    const id = attrs.id || `marker_${markers.length + 1}`;
    const endRegex = new RegExp(`<!--\\s*mmlib:source-end\\s+id=["']?${escapeRegex(id)}["']?\\s*-->`, 'g');
    endRegex.lastIndex = startRegex.lastIndex;
    const endMatch = endRegex.exec(text);
    const startIndex = startRegex.lastIndex;
    const endIndex = endMatch ? endMatch.index : text.length;
    markers.push({
      id,
      title: attrs.title || attrs.path || id,
      path: attrs.path || '',
      startIndex,
      endIndex,
      markdown: text.slice(startIndex, endIndex).trim(),
    });
    if (endMatch) startRegex.lastIndex = endRegex.lastIndex;
  }
  return markers;
}

function parseAttrs(input) {
  const attrs = {};
  const regex = /([A-Za-z0-9_-]+)=("[^"]*"|'[^']*'|[^\s]+)/g;
  let match;
  while ((match = regex.exec(input)) !== null) {
    attrs[match[1]] = match[2].replace(/^['"]|['"]$/g, '');
  }
  return attrs;
}

function renderLibrarySidebar(library) {
  const sourceItems = library.sources.map((source, index) => `
    <li>
      <button class="source-button" type="button" data-source-id="${escapeAttr(source.id)}">
        <span class="source-title">${escapeHtml(source.title || `Source ${index + 1}`)}</span>
        ${source.relative_path ? `<span class="source-path">${escapeHtml(source.relative_path)}</span>` : ''}
        ${source.converter ? `<span class="source-meta">${escapeHtml(source.converter)}</span>` : ''}
      </button>
    </li>
  `).join('');

  el.sidebar.innerHTML = `
    <div class="panel library-meta">
      <p class="eyebrow">Library</p>
      <h2>${escapeHtml(library.title || 'Markdown Library')}</h2>
      ${library.description ? `<p>${escapeHtml(library.description)}</p>` : ''}
      <div class="tags">
        ${library.category ? `<span class="tag">${escapeHtml(library.category)}</span>` : ''}
        ${library.converter_mode ? `<span class="tag">${escapeHtml(library.converter_mode)}</span>` : ''}
        <span class="tag">${library.sources.length} source${library.sources.length === 1 ? '' : 's'}</span>
      </div>
    </div>
    <input id="sourceSearch" class="search-box" type="search" placeholder="Search sources…" aria-label="Search sources">
    <ol id="sourceList" class="source-list">${sourceItems}</ol>
  `;

  el.sidebar.querySelectorAll('.source-button').forEach((button) => {
    button.addEventListener('click', () => selectSource(button.dataset.sourceId));
  });

  const search = document.getElementById('sourceSearch');
  search.addEventListener('input', () => filterSources(search.value));
}

function renderSingleSidebar(fileName) {
  el.sidebar.innerHTML = `
    <div class="panel library-meta">
      <p class="eyebrow">Markdown file</p>
      <h2>${escapeHtml(fileName)}</h2>
      <p>This does not contain Make Markdown Library front matter or source markers, so the whole file is shown as one document.</p>
    </div>
  `;
}

function selectSource(id) {
  const source = state.library?.sources.find((item) => item.id === id);
  if (!source) return;
  const markdown = source.marker?.markdown || fallbackSectionFromHeading(source) || '';
  showMarkdown(markdown || '_No section content found for this source._', source.title || source.id);
  document.querySelectorAll('.source-button').forEach((button) => {
    button.classList.toggle('active', button.dataset.sourceId === id);
  });
}

function fallbackSectionFromHeading(source) {
  if (!source.title) return '';
  const escaped = escapeRegex(source.title);
  const match = state.fullText.match(new RegExp(`(^|\\n)#{1,3}\\s+${escaped}\\s*(\\n[\\s\\S]*)`, 'm'));
  return match ? match[0] : '';
}

function filterSources(query) {
  const needle = query.trim().toLowerCase();
  document.querySelectorAll('#sourceList li').forEach((item) => {
    const text = item.textContent.toLowerCase();
    item.hidden = needle && !text.includes(needle);
  });
}

function showMarkdown(markdown, title) {
  state.currentMarkdown = markdown;
  state.currentTitle = title;
  el.documentTitle.textContent = title;
  el.raw.value = markdown;
  el.rendered.innerHTML = renderMarkdown(markdown);
}

function renderMarkdown(markdown) {
  if (window.markdownit) {
    const md = window.markdownit({ html: false, linkify: true, typographer: true });
    const rendered = md.render(markdown || '');
    return window.DOMPurify ? window.DOMPurify.sanitize(rendered) : rendered;
  }
  return fallbackMarkdown(markdown || '');
}

function fallbackMarkdown(markdown) {
  const html = [];
  const lines = markdown.replace(/\r\n/g, '\n').split('\n');
  let inCode = false;
  let codeLines = [];
  let inList = false;
  let paragraph = [];

  const flushParagraph = () => {
    if (paragraph.length) {
      html.push(`<p>${inlineMarkdown(paragraph.join(' '))}</p>`);
      paragraph = [];
    }
  };
  const flushList = () => {
    if (inList) {
      html.push('</ul>');
      inList = false;
    }
  };

  for (const line of lines) {
    const fence = line.match(/^```/);
    if (fence && !inCode) {
      flushParagraph();
      flushList();
      inCode = true;
      codeLines = [];
      continue;
    }
    if (fence && inCode) {
      html.push(`<pre><code>${escapeHtml(codeLines.join('\n'))}</code></pre>`);
      inCode = false;
      continue;
    }
    if (inCode) {
      codeLines.push(line);
      continue;
    }

    if (!line.trim()) {
      flushParagraph();
      flushList();
      continue;
    }

    const heading = line.match(/^(#{1,6})\s+(.*)$/);
    if (heading) {
      flushParagraph();
      flushList();
      const level = heading[1].length;
      html.push(`<h${level}>${inlineMarkdown(heading[2])}</h${level}>`);
      continue;
    }

    if (/^---+$/.test(line.trim())) {
      flushParagraph();
      flushList();
      html.push('<hr>');
      continue;
    }

    if (/^>\s?/.test(line)) {
      flushParagraph();
      flushList();
      html.push(`<blockquote>${inlineMarkdown(line.replace(/^>\s?/, ''))}</blockquote>`);
      continue;
    }

    const bullet = line.match(/^\s*[-*+]\s+(.*)$/);
    if (bullet) {
      flushParagraph();
      if (!inList) {
        html.push('<ul>');
        inList = true;
      }
      html.push(`<li>${inlineMarkdown(bullet[1])}</li>`);
      continue;
    }

    paragraph.push(line.trim());
  }
  flushParagraph();
  flushList();
  if (inCode) html.push(`<pre><code>${escapeHtml(codeLines.join('\n'))}</code></pre>`);
  return html.join('\n');
}

function inlineMarkdown(text) {
  let safe = escapeHtml(text);
  safe = safe.replace(/`([^`]+)`/g, '<code>$1</code>');
  safe = safe.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  safe = safe.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  safe = safe.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" rel="noreferrer noopener" target="_blank">$1</a>');
  return safe;
}

function toggleRaw() {
  state.rawVisible = !state.rawVisible;
  el.raw.hidden = !state.rawVisible;
  el.rendered.hidden = state.rawVisible;
  el.toggleRaw.textContent = state.rawVisible ? 'Show formatted' : 'Show raw';
}

async function copyCurrentSection() {
  if (!state.currentMarkdown) return;
  try {
    await navigator.clipboard.writeText(state.currentMarkdown);
    const old = el.copySection.textContent;
    el.copySection.textContent = 'Copied';
    setTimeout(() => { el.copySection.textContent = old; }, 1200);
  } catch {
    el.raw.hidden = false;
    el.rendered.hidden = true;
    el.raw.focus();
    el.raw.select();
  }
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
  }[char]));
}

function escapeAttr(value) { return escapeHtml(value).replace(/`/g, '&#096;'); }
function escapeRegex(value) { return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

function sampleLibrary() {
  return `---
make_markdown_library:
  type: "library"
  schema_version: "1.0"
  title: "Sample Markdown Library"
  description: "A tiny example for the viewer."
  category: "Demo"
  built_at: "2026-06-29T12:00:00+00:00"
  converter_mode: "auto"
  markdown_policy: "include"
  sources:
    - id: "src_demo_pdf"
      title: "project.pdf"
      relative_path: "project.pdf"
      converter: "liteparse 2.2.1"
      warnings: []
    - id: "src_demo_notes"
      title: "notes.md"
      relative_path: "notes.md"
      converter: "direct-markdown"
      warnings: []
---

# Sample Markdown Library

<!-- mmlib:source-start id="src_demo_pdf" title="project.pdf" path="project.pdf" -->
## project.pdf

This is a rendered section from a PDF.

- It can include lists.
- It can include **bold text** and \`inline code\`.

\`\`\`
Example code block
\`\`\`

<!-- mmlib:source-end id="src_demo_pdf" -->

<!-- mmlib:source-start id="src_demo_notes" title="notes.md" path="notes.md" -->
## notes.md

This is a normal Markdown source file included in the library.

> The viewer is read-only: inspect, search, copy.

<!-- mmlib:source-end id="src_demo_notes" -->
`;
}
