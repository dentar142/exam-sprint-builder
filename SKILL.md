---
name: exam-sprint-builder
description: >-
  Use when someone wants to turn course materials — a review-class recording or
  audio, lecture slides, notes, an AI summary, or past exam papers — into a
  complete, self-contained, OFFLINE exam-prep package before a test: an Obsidian
  study-note library, an HTML study system, large grounded quiz apps with instant
  feedback, a mock exam, a one-page cheat sheet, an interactive knowledge diagram,
  and past-paper solutions. Triggers include 考前冲刺 / 复习资料生成 / 把录屏整理成复习 /
  刷题网页 / 模拟卷 / 小抄 / cram kit / mock exam builder / study-package generator.
---

# Exam Sprint Builder

## Overview

Turn whatever a student already has — a review-class **recording**, a lecture
**slide deck**, scattered **notes**, an **AI summary**, or **past exam papers** —
into one coherent, **exam-oriented** revision package. Every output is a
**self-contained file that opens by double-click** (`file://`, no server, no CDN),
with light+dark themes and browser-local persistence.

**Core principle: ground everything in the student's real material.** Slides,
transcript, and past papers are the source of truth. Never invent exam content
from general knowledge; extract it, then have a second adversarial pass verify it.

This skill is **interactive and guided**. On first use you walk the student through
a short, humane intake — they should never face a wall of questions. Default
hard, ask only what you can't infer, and let them skip anything.

## When to Use

- "把这段复习课录屏 / 课件 / 历年卷整理成复习资料" (organize a recording / slides / past papers into revision material)
- They want quiz / 刷题 web apps, a mock exam, a cheat sheet, a study-note vault, or a knowledge diagram
- Exam is near and they need *exam-shaped*, high-yield material, not a textbook

**Not for:** writing the textbook itself, general note-taking with no exam target,
or anything that must be deployed online (this skill is offline-first — see Hard Rules).

## Guided Intake (6 steps)

Run these in order. **Full verbatim wording, option menus, and skip rules are in
[references/intake-flow.md](references/intake-flow.md) — follow it.** Summary:

0. **Welcome + dependency self-check.** Say what you'll produce. Check ONLY the
   tools the chosen inputs need: `node` (always, for HTML), `ffmpeg`/`ffprobe`
   (video/audio), `python` + `faster-whisper` (speech→text). Give install hints
   for whatever is missing; never force a full toolchain.
1. **Course basics (minimal).** Subject name → exam format & marks (skippable —
   infer from material) → key chapters → output folder (default
   `<subject>-考前冲刺/`; **originals are never modified**).
2. **Submit material (≥1).** Ask per type: recording / standalone audio / slides /
   notes / past papers / teacher outline or AI summary / an existing study vault to
   reference-only. Take a path or pasted text for each.
3. **Pick deliverables (multi-select).** Presets: `全都要` / `精简三件套`
   (notes + quiz + cheat sheet) / `自定义`. The ten deliverables are catalogued in
   [references/deliverables-catalog.md](references/deliverables-catalog.md).
4. **Style & options.** Visual theme (warm / dark-tech / Material 3 / Win10 Metro /
   custom accent) → light/dark (default both) → question volume (lean ~10 / standard
   ~20 / heavy 30+ per chapter) + curated set? → adversarial proofreading pass
   (default ON) → report language → deployment (**offline `file://` by default; do
   NOT publish online unless explicitly asked**).
5. **Confirm + generate.** Echo a one-screen summary, get a go, run the pipeline,
   then **verify independently** and report the finished list in the user's language.

## Generation Pipeline

Dispatch agents; don't do it all in one context.

1. **Extract** — recording → slide frames (`ffmpeg` scene detect) + audio →
   transcript (`faster-whisper`); docx/pptx/pdf → text + images. See
   [references/media-extraction.md](references/media-extraction.md) and
   [references/content-grounding.md](references/content-grounding.md).
2. **Ground** — reconcile transcript + slides + papers into a single source-of-truth
   outline of tested points (the "teacher-named" points).
3. **Generate (parallel, one agent per deliverable)** — each output is built from the
   grounded outline. HTML rules in
   [references/html-conventions.md](references/html-conventions.md); palettes in
   [references/themes.md](references/themes.md).
4. **Author question banks** via the命题 → adversarial-proofread → merge/shuffle/inject
   pipeline in [references/question-bank-pipeline.md](references/question-bank-pipeline.md).
   Bundled tools: `scripts/build_quiz.py`, `assets/md2html.js`, `assets/templates/`.
5. **Verify (independent pass)** — run `scripts/verify_html.py` on **generated**
   HTML only (4 checks; expected `PASS (4/4 checks passed)`). Do not verify
   uninjected templates. Bank contract: top-level JSON array, field `stem`.
   Checklist in [references/verification.md](references/verification.md).

## Hard Rules

- **Never modify the student's originals.** Read them; write only into the new output folder.
- **Offline-first.** Self-contained HTML only: no CDN, no ES-module imports, openable via `file://`. **Do not deploy online unless the user explicitly asks.**
- **Ground, then verify.** No exam content from general knowledge alone; a second adversarial pass checks every generated question and answer.
- **Report in the user's language** (mirror whatever they write; default 中文 if they wrote in Chinese), and only claim "done" after the verifier passes — show the evidence.
- **Light + dark** share one `localStorage` theme key with an anti-flash inline head script (see html-conventions).

## Common Pitfalls (full list in references/troubleshooting.md)

- Windows console shows GBK mojibake though files are clean UTF-8 — trust Read/Grep, not console echo.
- Inline `node -e '...'` mangles Windows backslash paths — write the script to a file and run it.
- Bank-extraction regex stops at the first `];` inside embedded C code — scan bracket depth instead.
- A naive question generator puts every correct answer at index 0 — shuffle options deterministically.
