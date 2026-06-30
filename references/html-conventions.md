# HTML Conventions Reference

Every HTML deliverable this skill produces is **one self-contained file that
opens by double-click** — a study system, a quiz app, a mock exam, a cheat sheet,
a knowledge diagram. These rules keep them all consistent, offline, and durable.
Follow them exactly; the verifier checks for them.

---

## 1. Self-contained, offline-first

The single hard constraint: a file must render fully from `file://` with no
network and no build step.

**Do**

- Inline **all** CSS in one `<style>` and **all** JS in one or more classic
  `<script>` blocks.
- Inline images as `data:` URIs when they must travel with the file.
- Keep everything in one `.html` the student can email, copy to a USB stick, or
  open years later.

**Never**

- `<link rel="stylesheet" href="https://…">` or any CDN (`cdn.`, `unpkg`,
  `jsdelivr`, `googleapis`, …).
- `<script src="https://…">` — no remote libraries.
- `<script type="module">`, `import`, or `export`. ES modules are fetched by the
  browser, and `file://` blocks that fetch under the **CORS / same-origin policy**
  — the page silently breaks on double-click. Use classic scripts and plain
  function/IIFE scope instead.
- `fetch()` / `XMLHttpRequest` against the local disk for the same reason.

> [!warning] The double-click test
> Verification opens the file directly from the filesystem (no `localhost`, no
> dev server). If a feature only works over `http://`, it does not ship.

**Why these break under `file://`**

| Pattern | Failure on `file://` |
|---|---|
| `<script type="module">` | Module fetch blocked by same-origin policy → script never runs. |
| CDN `<link>` / `<script src>` | No network (or offline) → unstyled / dead page. |
| `fetch('./data.json')` | `file://` fetch blocked → empty/blank UI. |
| Web fonts from Google Fonts | No network → silent fallback, layout shift. Use the system font stack. |

---

## 2. Light / dark theming

One mechanism for **all** pages so they agree with each other.

- The active theme is the `data-theme` attribute on **`document.documentElement`**
  (`<html data-theme="light">` / `"dark"`).
- All colors are CSS custom properties; `:root` / `[data-theme="light"]` holds the
  light set, `[data-theme="dark"]` overrides for dark. (Token sets:
  [themes.md](themes.md).)
- A visible **toggle button** flips the attribute.
- The choice is persisted to the **shared** `localStorage` key **`esb-theme`** so
  every generated page in the package opens in the same theme.
- An **anti-flash inline head script** sets `data-theme` *before first paint* so a
  dark-mode user never sees a white flash.

### 2.1 Anti-flash head script (copy-paste)

Place this as the **first** `<script>` in `<head>`, before the `<style>`. It is
tiny and synchronous on purpose — it must run before the body paints.

```html
<script>
(function () {
  try {
    var t = localStorage.getItem('esb-theme');
    if (!t) {
      t = (window.matchMedia &&
           window.matchMedia('(prefers-color-scheme: dark)').matches)
          ? 'dark' : 'light';
    }
    document.documentElement.setAttribute('data-theme', t);
  } catch (e) { /* localStorage blocked (rare under file://) — fall through */ }
})();
</script>
```

Notes:
- No saved preference → fall back to the OS preference, then to `light`.
- Wrap in `try/catch`: some browsers throw on `localStorage` access from
  `file://`. The page must still render.
- Keep `<html>` authored as `data-theme="light"` so the page is valid before the
  script runs; the script corrects it pre-paint.

### 2.2 Theme-toggle snippet (copy-paste)

Markup:

```html
<button id="theme-toggle" class="theme-btn" type="button">🌙 暗色</button>
```

Behavior (classic script, runs after the button exists):

```html
<script>
(function () {
  function apply(t) {
    document.documentElement.setAttribute('data-theme', t);
    var b = document.getElementById('theme-toggle');
    if (b) b.textContent = (t === 'dark') ? '☀ 亮色' : '🌙 暗色';
    try { localStorage.setItem('esb-theme', t); } catch (e) {}
  }
  var btn = document.getElementById('theme-toggle');
  if (btn) btn.onclick = function () {
    var cur = document.documentElement.getAttribute('data-theme') || 'light';
    apply(cur === 'dark' ? 'light' : 'dark');
  };
  apply(document.documentElement.getAttribute('data-theme') || 'light');
})();
</script>
```

`esb-theme` is the same key the anti-flash script reads, so a toggle on one page
is honored when the student opens any other page.

---

## 3. Per-app persisted state

Beyond the shared theme, each app keeps its own state in a **namespaced**
`localStorage` key so two apps never collide.

- Naming: `esb-<app>-<subject>-<purpose>`, lowercase, hyphen-separated.
  - `esb-quiz-数电-progress` — quiz answers / spaced-repetition schedule.
  - `esb-mock-数电-attempt` — a mock-exam attempt in progress.
  - `esb-notes-数电` — personal annotations on a study page.
- Reserved shared key: **`esb-theme`** (theme only — never overload it).
- Store JSON; bump a `version` field inside the value when the schema changes so
  old saves can be migrated or discarded gracefully.

```js
var KEY = 'esb-quiz-' + subject + '-progress';
function save(state){ try{ localStorage.setItem(KEY, JSON.stringify(state)); }catch(e){} }
function load(){ try{ return JSON.parse(localStorage.getItem(KEY)) || null; }catch(e){ return null; } }
```

### Export / import (offline backup)

`localStorage` is per-browser and per-origin; under `file://` it can be cleared
unexpectedly. Always give state-bearing apps a JSON **export** and **import** so
progress survives a cache wipe or moves between machines — with no server.

```js
// Export: trigger a download, no network.
function exportState() {
  var data = localStorage.getItem(KEY) || '{}';
  var blob = new Blob([data], { type: 'application/json' });
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = KEY + '.json';
  a.click();
  URL.revokeObjectURL(a.href);
}

// Import: read a chosen file with FileReader (works under file://).
function importState(file) {
  var r = new FileReader();
  r.onload = function () {
    try { localStorage.setItem(KEY, r.result); location.reload(); }
    catch (e) { alert('导入失败 / import failed'); }
  };
  r.readAsText(file);
}
```

Use `<input type="file">` + `FileReader` for import — never `fetch`, which is
blocked on `file://`.

---

## 4. Sidebar TOC + scrollspy (long doc pages)

Study notes and past-paper solutions are long; a sticky left **table of contents**
with **scrollspy** (auto-highlight the section in view) makes them navigable.
`assets/md2html.js` generates this automatically from `h1`–`h3`.

Structure:

```html
<div class="layout">                <!-- grid: 266px sidebar + content -->
  <nav class="toc" id="toc">
    <a href="#sec-1" class="lv1" data-id="sec-1">第一章 概述</a>
    <a href="#sec-1-1" class="lv2" data-id="sec-1-1">1.1 关键点</a>
    <!-- … -->
  </nav>
  <main class="content" id="content">
    <h1 id="sec-1">第一章 概述</h1>
    <!-- … headings carry stable slug ids … -->
  </main>
</div>
```

Scrollspy with `IntersectionObserver` (no scroll-event polling):

```js
var links = {};
document.querySelectorAll('#toc a').forEach(function (a) { links[a.dataset.id] = a; });
var obs = new IntersectionObserver(function (entries) {
  entries.forEach(function (e) {
    if (!e.isIntersecting) return;
    Object.values(links).forEach(function (x) { x.classList.remove('active'); });
    var a = links[e.target.id];
    if (a) { a.classList.add('active'); a.scrollIntoView({ block: 'nearest' }); }
  });
}, { rootMargin: '-60px 0px -70% 0px' });   // "active" = heading near the top
document.querySelectorAll('#content h1,#content h2,#content h3')
  .forEach(function (h) { if (h.id) obs.observe(h); });
```

Conventions:
- Heading ids are **stable slugs** (deduplicated with a numeric suffix on
  collision) so `#anchor` deep links keep working.
- Give headings `scroll-margin-top` equal to the sticky header height so anchored
  jumps are not hidden behind the bar.
- Collapse the sidebar into a `☰` drawer under ~820px (mobile / narrow windows).

---

## 5. Print rules

Students print cheat sheets and mock papers. Make print a first-class output.

- A **print button**: `<button onclick="window.print()">🖨 打印</button>`.
- `@page { size: A4; margin: 16mm; }` — A4 is the classroom default. Use
  `size: A4 landscape;` for wide tables.
- In `@media print`, hide chrome (top bar, sidebar TOC, theme/print buttons) and
  let content flow full width; drop shadows (they waste toner).

```css
@media print {
  .bar, .toc, .menu, .tbtn, .theme-btn, .print-btn { display: none !important; }
  .layout { display: block; max-width: none; }
  .content { max-width: none; padding: 0; }
  pre, table, .card { box-shadow: none; }
  @page { size: A4; margin: 16mm; }
}
```

### Cheat sheets: 3-column dense layout

A one-page 小抄 maximizes density with CSS multi-column, and keeps cards from
splitting across columns or pages:

```css
.cheat { column-count: 3; column-gap: 10px; }
.cheat .card { break-inside: avoid; margin: 0 0 8px; }
@media print { .cheat { column-count: 3; } @page { size: A4 portrait; margin: 8mm; } }
```

Drop to `column-count: 2` for content-heavy sheets, `1` on narrow screens via a
media query. Print preview is the source of truth — verify the sheet fits the
intended page count.

---

## 6. Contrast & readability

The pages are for tired eyes the night before an exam.

- Target **WCAG AA**: ≥ 4.5:1 contrast for body text, ≥ 3:1 for large headings,
  in **both** themes. Re-check `--ink` on `--bg` and accent-on-surface after any
  palette tweak.
- Body **line-height ≥ 1.6**; cap reading width near `--maxw` (~1080px) / content
  column ~860px so lines do not run edge to edge.
- Never signal correct/incorrect or warnings by **color alone** — pair it with an
  icon, label, or shape (color-blind safety).
- Code blocks keep their own dark, high-contrast surface (`--code-bg` /
  `--code-ink`) in both themes for legibility.
- Use the **system font stack** (no web fonts to fetch); include CJK families
  (`Microsoft YaHei`, `PingFang SC`, `Noto Serif SC`) so Chinese keywords render
  cleanly offline.

---

## 7. Quick checklist (per file)

- [ ] Opens from `file://` by double-click; no console errors.
- [ ] No CDN, no `<script type="module">`, no `import`/`export`, no remote `fetch`.
- [ ] Anti-flash head script present and first in `<head>`; reads `esb-theme`.
- [ ] Theme toggle flips `data-theme` on `<html>` and writes `esb-theme`.
- [ ] App state in a namespaced `esb-…` key with JSON export/import.
- [ ] (Doc pages) sidebar TOC + scrollspy + stable heading ids.
- [ ] Print button + `@media print` + `@page A4`; cheat sheets paginate cleanly.
- [ ] AA contrast in light **and** dark; no color-only signaling.
