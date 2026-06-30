# Exam Sprint Builder — Deliverables Catalog

> **Shared conventions** apply to every deliverable unless noted otherwise.
> - **Theme**: warm off-white (`#fdf6ee`) for light mode, dark slate (`#1a1a2e`) for dark mode.
> - **Theme persistence**: `localStorage` key `esb-theme`; toggled by a visible button in the header.
> - **Self-contained offline**: no CDN, no external fonts, no `https?://` URLs inside the file; all assets inlined as base64 or embedded CSS.
> - **File target**: openable from the local filesystem via `file://` without a server.
> - **Language**: English prose + Chinese subject keywords; never mix in copyrighted exam text.

---

## 1. MD Note Library (Obsidian Vault)

**Purpose**  
A self-contained Obsidian vault that turns raw subject notes into a navigable knowledge base for long-form review. Designed for learners who already use Obsidian but also usable by anyone with a Markdown reader.

**Inputs needed**
- Subject name and chapter list (JSON or plain list).
- Per-chapter bullet points / key concepts (plain text or structured JSON).
- Optional: glossary entries, formula list.

**Output**
```
{subject}/
  _MOC.md            ← Map of Contents (总目录)
  chapters/
    01-{name}.md
    02-{name}.md
    …
  _glossary.md
  _formulas.md
```

**Structure**
- `_MOC.md`: YAML frontmatter (`tags: [moc, {subject}]`); bulleted `[[wikilink]]` tree to every chapter note and support file.
- Each chapter note: frontmatter with `tags`, `chapter`, `status`; H2 sections for concepts, key terms, examples; `[[Back to MOC]]` footer; cross-links to related chapters via `[[wikilink]]`.
- `_glossary.md`: two-column table (term | definition); linked from MOC.
- `_formulas.md`: fenced code blocks and inline LaTeX for each formula.

**Theme / UI**  
Plain Markdown — rendered by Obsidian's CSS. No custom CSS injected; the vault must be portable across themes.

**Key features**
- Every note is self-contained (reads fine as plain `.md`).
- `[[wikilink]]` inter-linking ensures graph view is populated from the start.
- Frontmatter `status: draft | review | done` supports spaced repetition plugins.
- Separate glossary and formula files avoid clutter in chapter notes.

---

## 2. HTML Study System

**Purpose**  
A single-file interactive study hub: chapter cards expand to show key-reference tables and concept summaries. The primary "sit down and learn" interface.

**Inputs needed**
- Chapter list with titles and summaries.
- Per-chapter: key terms (table rows), code examples (for `<pre>` blocks), and callout tips.

**Output filename**: `{subject}_study_system.html`

**Structure**
- Sticky header: subject title + light/dark toggle (saves to `esb-theme`).
- Chapter grid: each card shows chapter number + title; click expands an accordion panel.
- Inside each panel: concept summary paragraph, key-reference table (`Term | Value/Description`), and optional `<pre>` code block.
- Footer: revision date, "made offline" badge.

**Theme**  
Warm light (`#fdf6ee` bg, `#3d2b1f` text) / dark slate (`#1a1a2e` bg, `#e8d5b7` text). Card borders use accent color `#c47a3a` (light) / `#f0a060` (dark).

**Key features**
- Pure CSS accordion (no JS required for basic expand/collapse; JS enhances with smooth animation).
- Quick-ref tables are sortable via a lightweight inline JS sort (no library).
- "Collapse all / Expand all" button in header.
- Print-friendly: each card prints on its own page break.

---

## 3. One-Page Speed Review

**Purpose**  
A condensed must-memorize cheat document. Designed for the final 30 minutes before an exam: one Markdown version for editing, one HTML version for display.

**Inputs needed**
- Ranked list of must-know points (provided as bullet text, one point per line).
- Optional: magic values table, formula list.

**Output filenames**: `{subject}_speed_review.md`, `{subject}_speed_review.html`

**Structure**
- H1: subject name + exam date placeholder.
- H2 sections (max 5): e.g., "Core Concepts 核心概念", "Magic Values 关键数值", "Common Traps 常见陷阱", "Code Patterns 代码模板", "Last-Minute Formulas 最后公式".
- Each section: tight bulleted list, max 10 bullets.
- HTML version adds a compact inline stylesheet for 2-column layout on wide screens, 1-column on mobile.

**Theme**  
Minimal. Light: white bg, black text, red callout color for traps. Dark: `#111` bg, `#eee` text, orange callouts. Toggle in HTML version only.

**Key features**
- Under 2 printed pages (A4) when browser-printed.
- No images; no tables longer than 8 rows.
- MD source is editable; HTML is the display artifact.

---

## 4. A4 Cheat Sheet (HTML)

**Purpose**  
A print-ready single A4 page crammed with scoring information only: magic values, register addresses/bits, code skeletons, and known trap answers. Assumes the reader already knows the basics.

**Inputs needed**
- Magic values list (name → hex/decimal value).
- Register map (register name → address, bit fields).
- Code skeleton snippets (init sequences, ISR templates, etc.).
- Known exam traps (short Q&A pairs).

**Output filename**: `{subject}_cheat_sheet.html`

**Structure**
- CSS `@page { size: A4; margin: 8mm; }`.
- Three CSS columns (`column-count: 3; column-gap: 4mm`).
- Sections within columns: `<h3>` headings (8pt), tight `<table>` rows (7pt), `<pre>` code blocks (6.5pt Consolas).
- "Print this page" button (hidden in `@media print`).
- Page header bar: subject name + date (tiny, non-printing color).

**Theme**  
Print-first white background. Screen view uses light warm theme. Dark mode toggle available on screen but print always outputs white.

**Key features**
- All font sizes in `pt` for predictable print output.
- `break-inside: avoid` on each section block.
- Columns rebalance automatically; overflow gets a second page rather than clipping.
- Print button calls `window.print()`.

---

## 5. Mock Exam (HTML)

**Purpose**  
A self-graded practice exam that mimics the real exam format: answer all questions, then reveal scores with per-question feedback.

**Inputs needed**
- Quiz bank JSON (see Quiz App spec for schema).
- Exam metadata: total marks, time limit, section breakdown.

**Output filename**: `{subject}_mock_exam.html`

**Structure**
- Cover page: subject, instructions, timer (countdown JS, auto-alerts at half-time and 5 min left).
- Sections (e.g., Section A: MCQ, Section B: Fill-in, Section C: Short answer).
- Each question: numbered, point value shown.
- "Submit exam" button → calculates score → reveals correct answers inline with color coding (green correct, red wrong, blue skipped).
- Score summary card: total/max, percentage, per-section breakdown.

**Theme**  
Shared warm/dark theme. During exam mode: neutral white-ish to reduce distraction. After submission: colored feedback overlays appear.

**Key features**
- Timer state stored in `sessionStorage` so a page refresh does not lose time.
- "Submit" disabled until all required questions answered (or user confirms skip).
- Answer reveal shows both the correct answer and a brief rationale (sourced from quiz bank `explanation` field).
- No server; all grading done in inline JS.

---

## 6. Quiz App (Material 3 / Pixel style)

**Purpose**  
A polished, mobile-friendly quiz application with multiple question types, per-session progress tracking, a wrong-answer book, and persistent statistics.

**Inputs needed**
- Quiz bank JSON (validated; see schema below).
- Subject name and chapter list for filtering.

**Output filename**: `{subject}_quiz_app.html`

**Quiz bank JSON schema (shared across deliverables 6 & 7)**
```json
{
  "meta": { "subject": "string", "version": "string" },
  "questions": [
    {
      "id": "string (unique)",
      "type": "single | fill | short | multi",
      "chapter": "number",
      "text": "string",
      "options": ["string"],          // required for single/multi
      "answer": 0,                    // index (single/multi) or string (fill/short)
      "explanation": "string",
      "tags": ["string"],
      "difficulty": 1                 // 1–3
    }
  ]
}
```

**Structure**
- Home screen: subject title, mode selector chips (单选 / 填空 / 简答 / 混合 / 收藏 / 错题本).
- Quiz screen: question card with animated slide-in; options as tappable chips (Material 3 filled button style).
- After each answer: instant color feedback (green/red chip highlight) + reveal-answer panel.
- Stats bar: accuracy per type (shown as mini progress rings).
- Settings drawer: chapter range filter, difficulty filter, shuffle toggle.

**Theme**  
Material 3 color tokens: primary `#6750A4` (light) / `#D0BCFF` (dark). Surface uses warm tones per shared convention. `data-theme` on `<html>`.

**Key features**
- Modes: single-type drill, fill-in text input, short-answer manual grade, mixed, starred (bookmarked), wrong-book (previously wrong).
- Wrong-answer book: stored in `localStorage` as `esb-wrong-{subject}`; shows count badge on home screen.
- Per-type accuracy ring charts (pure SVG, no library).
- JSON export/import of progress via a modal dialog.
- "Reveal answer" button always available after submitting.

---

## 7. Metro Quiz (Windows 10 Tile style)

**Purpose**  
A visually distinct tile-grid quiz interface inspired by Windows 10 Metro UI, targeting desktop-first use with keyboard navigation.

**Inputs needed**
- Same quiz bank JSON as deliverable 6.
- Optional curated ranges (chapter start/end).

**Output filename**: `{subject}_metro_quiz.html`

**Structure**
- Tile home screen: colorful flat tiles (2×2, 1×2, 1×1 grid) for each mode and chapter group.
- Quiz panel: full-width card with question; multiple-choice options as large flat buttons.
- For fill/short: `<textarea>` with character counter.
- For code questions: syntax-highlighted `<pre>` (highlight via inline CSS classes, no external lib).
- Stats tile on home: animated flip tile showing live accuracy.

**Theme**  
Metro palette: accent colors per tile (cobalt, teal, purple, green, red). Light/dark toggle; dark mode uses `#1a1a2e` background. `data-theme` + `esb-theme` localStorage.

**Key features**
- Question types: single / multi / fill / short / code (display + fill blank).
- Tile home with drill-down to chapter or full-set mode.
- Instant feedback after each answer (tile color flash animation).
- Stats panel: overall accuracy, per-chapter bar chart (inline SVG).
- localStorage progress + JSON export/import button in settings tile.
- "All questions" and "Curated range" modes selectable on home.
- Keyboard navigation: arrow keys to move between options, Enter to submit.

---

## 8. Interactive Knowledge Diagram (SVG)

**Purpose**  
A clickable concept map showing the structural relationships between chapters, components, or system blocks. Only generated when the subject has clear hierarchical or graph structure (e.g., MCU peripheral relationships, OS layer diagrams).

**Inputs needed**
- Node list: `{id, label, chapter, group}`.
- Edge list: `{from, to, label}`.
- Optional: highlight groups (e.g., "interrupt system", "memory map").

**Output filename**: `{subject}_knowledge_diagram.html`

**Gate condition**: Skip this deliverable if the subject's node list has fewer than 6 nodes or no meaningful edges.

**Structure**
- Full-viewport SVG with pan/zoom (pure JS, no D3).
- Nodes rendered as rounded rectangles; edges as labeled arrows.
- Color-coded by group; legend in top-right corner.
- Click a node → info panel slides in from right (chapter reference, brief description, links to related quiz questions).
- Highlight mode: clicking a group dims unrelated nodes.

**Theme**  
Node fill uses warm palette in light mode, muted dark palette in dark mode. SVG `<defs>` holds both palettes; `data-theme` attribute swap triggers re-color.

**Key features**
- Pan: click-drag on background. Zoom: scroll wheel or pinch.
- "Reset view" button.
- Highlight on hover (stroke weight increases).
- Clicking a chapter reference deep-links to the HTML study system file (`{subject}_study_system.html#{chapter-id}`).
- Exportable as a PNG via `canvas` + `toDataURL` (button in toolbar).

---

## 9. Teacher-Named Points Detail + Line-by-Line Code Explanations

**Purpose**  
Structured coverage of points explicitly called out by a teacher or syllabus as high-priority, with annotated code where relevant. Both a reading document (MD) and a styled display (HTML).

**Inputs needed**
- List of named points (e.g., "中断优先级判断", "定时器初值计算"); provided as a JSON array of `{name, description, code_example}` objects.
- Optional: teacher's exact wording for each point (quoted but not copyrighted paraphrase).

**Output filenames**: `{subject}_teacher_points.md`, `{subject}_teacher_points.html`

**Structure**
- MD: H2 for each named point; sub-sections: "What it means", "Why it matters", "Code example" (fenced block), "Common mistake".
- HTML: same structure; code blocks use inline syntax highlighting (CSS token classes for keywords/comments/strings).
- Line-by-line annotation: each code line has a trailing `// ← explanation` comment; HTML version renders these as styled `<span class="annotation">`.
- Index table at top (HTML): clickable anchor links to each point.

**Theme**  
Shared warm/dark. Code block background: `#2b1f0e` (dark) / `#fff8ee` (light). Annotation comments use italic muted color.

**Key features**
- "Show/hide annotations" toggle button (HTML only).
- Each named point has a `data-point-id` attribute for deep-linking.
- Printable: annotations suppressed in `@media print` by default; checkbox in header to include them.
- MD version uses `<!-- annotation -->` HTML comments so they don't appear in basic Markdown renderers.

---

## 10. Past-Paper Organization & Solutions

**Purpose**  
A structured archive of past exam questions with full solutions and annotated code. Generated only when past paper content is supplied.

**Inputs needed**
- Past paper questions (user-provided, non-copyrighted paraphrases or original practice questions).
- Model answers / full code solutions per question.
- Year/exam label (e.g., "2023 期末", "模拟卷 A").

**Output filenames**: `{subject}_past_papers.md`, `{subject}_past_papers.html`

**Gate condition**: Skip if no past-paper input is provided.

**Structure**
- MD: H1 per exam, H2 per question; sub-sections "题目 (Question)", "解析 (Analysis)", "答案 (Answer)", "完整代码 (Full Code)".
- HTML: filterable table of contents by year/topic; question cards with collapsible solution panels.
- Full code per question in a `<pre>` block with inline annotations.
- Summary table at top: question number, topic, marks, difficulty.

**Theme**  
Shared warm/dark. Solution panels use a subtle left-border accent (green for full solutions, amber for partial).

**Key features**
- Toggle "show all solutions" / "hide all solutions" in HTML header.
- Filter by year, topic, or difficulty (inline JS, no library).
- "Copy code" button per code block (copies to clipboard via `navigator.clipboard`).
- Word count and estimated reading time shown per exam section.
- MD version uses horizontal rules (`---`) to clearly separate exams.

---

## Shared Input → Deliverable Dependency Map

| Input | Deliverables that consume it |
|---|---|
| Chapter list + concept bullets | 1, 2, 3, 8, 9 |
| Quiz bank JSON | 5, 6, 7 |
| Magic values / register map | 3, 4, 9 |
| Teacher-named points JSON | 9 |
| Past paper Q&A | 10 |
| Code snippets / skeletons | 4, 9, 10 |
| Node + edge list (graph) | 8 |

## Shared Theme / Persistence Conventions

| Convention | Value |
|---|---|
| localStorage key | `esb-theme` |
| `data-theme` values | `"light"` (default) / `"dark"` |
| Toggle element | `<button id="theme-toggle">` in page header |
| Light bg / text | `#fdf6ee` / `#3d2b1f` |
| Dark bg / text | `#1a1a2e` / `#e8d5b7` |
| Accent (light) | `#c47a3a` |
| Accent (dark) | `#f0a060` |
| Wrong-answer key | `esb-wrong-{subject}` |
| No external URLs | enforced by verifier (see `verification.md`) |
