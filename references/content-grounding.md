# Content Grounding Reference

How to turn raw source files (slides, transcript, past papers) into a single
source-of-truth "tested-points outline" (`源内容.md`) that every downstream
generator consumes.

**Golden rule**: extract then verify — never invent exam content from general
knowledge. Every tested point must be traceable to at least one source.

---

## 1. Extracting text from source formats

### 1a. DOCX (Word documents)

Use `python-docx` for paragraphs and table cells:

```python
from docx import Document

doc = Document("review_notes.docx")

lines = []
# Plain paragraphs
for para in doc.paragraphs:
    text = para.text.strip()
    if text:
        lines.append(text)

# Table cells
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            text = cell.text.strip()
            if text:
                lines.append(text)

with open("docx_text.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
```

For **embedded images** in a DOCX, use the zip approach (see `extract_docx_images.py`
in `scripts/`): a `.docx` is a ZIP archive; images live under `word/media/`.

### 1b. PPTX (PowerPoint slides)

Use `python-pptx` to iterate slides and shapes:

```python
from pptx import Presentation
from pptx.util import Inches
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pathlib import Path
import shutil

prs = Presentation("lecture.pptx")
out_img = Path("pptx_images"); out_img.mkdir(exist_ok=True)
lines = []
img_count = 0

for slide_num, slide in enumerate(prs.slides, start=1):
    lines.append(f"\n## Slide {slide_num}")
    for shape in slide.shapes:
        # Text frames
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                text = para.text.strip()
                if text:
                    lines.append(text)
        # Picture shapes
        if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
            img_data = shape.image.blob
            ext = shape.image.ext          # e.g. "png", "jpeg"
            img_path = out_img / f"slide{slide_num:03d}_img{img_count:02d}.{ext}"
            img_path.write_bytes(img_data)
            lines.append(f"[IMAGE: {img_path}]")
            img_count += 1

with open("pptx_text.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"Extracted {img_count} images to {out_img}/")
```

### 1c. PDF

Use `PyMuPDF` (`pip install pymupdf`):

```python
import fitz   # PyMuPDF
from pathlib import Path

doc = fitz.open("past_paper.pdf")
out_img = Path("pdf_images"); out_img.mkdir(exist_ok=True)
lines = []

for page_num, page in enumerate(doc, start=1):
    # Text extraction (preserves reading order)
    lines.append(f"\n## Page {page_num}")
    lines.append(page.get_text())

    # Image extraction
    for img_index, img in enumerate(page.get_images(full=True)):
        xref = img[0]
        base_image = doc.extract_image(xref)
        img_bytes = base_image["image"]
        ext = base_image["ext"]
        img_path = out_img / f"page{page_num:03d}_img{img_index:02d}.{ext}"
        img_path.write_bytes(img_bytes)
        lines.append(f"[IMAGE: {img_path}]")

with open("pdf_text.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
```

---

## 2. Transcript cleanup

Raw ASR output contains repetition, filler words, and mis-transcriptions.
Clean before merging.

### 2a. Deduplicate ASR repeats

Teachers often repeat the same sentence for emphasis; ASR duplicates them verbatim.

```python
from difflib import SequenceMatcher

def dedup_segments(segments, similarity_threshold=0.85):
    """Remove consecutive near-duplicate ASR segments."""
    cleaned = []
    for seg in segments:
        if not cleaned:
            cleaned.append(seg)
            continue
        ratio = SequenceMatcher(None, cleaned[-1]["text"], seg["text"]).ratio()
        if ratio < similarity_threshold:
            cleaned.append(seg)
    return cleaned
```

### 2b. Align segments to slide timestamps

If you kept slide-frame timestamps from `ffmpeg showinfo` (printed to stderr as
`pts_time`), map each transcript segment to the nearest slide:

```python
# slide_times: list of (slide_index, pts_time_seconds) from ffmpeg showinfo log
# segments: list of {"start": float, "end": float, "text": str}

import bisect

slide_pts = [t for _, t in slide_times]   # sorted ascending

def slide_for_time(t):
    idx = bisect.bisect_right(slide_pts, t) - 1
    return max(0, idx)

for seg in segments:
    seg["slide"] = slide_for_time(seg["start"])
```

### 2c. Capture spoken emphasis cues (重点标记)

These phrases signal candidate tested points ("这个要考", "重点", "记一下",
"常考", "必考", "背下来"):

```python
import re

EMPHASIS_PATTERNS = re.compile(
    r"(这个要考|重点|记一下|常考|必考|背下来|一定要|考过|会考)", re.IGNORECASE
)

def flag_emphasis(segments):
    for seg in segments:
        seg["is_key_point"] = bool(EMPHASIS_PATTERNS.search(seg["text"]))
    return segments
```

Flagged segments become high-priority candidates in the reconciliation step.

---

## 3. Reconciliation: merging all sources

Combine slides, transcript, and past papers into one unified outline.

### Merge strategy

1. **Anchor on slides**: each slide becomes a section in the outline.
2. **Annotate with transcript**: attach relevant segments (by `seg["slide"]`) under
   the matching slide section. Flag emphasis-tagged segments with a `[KEY]` marker.
3. **Cross-reference past papers**: for each question in the past paper, find the
   slide/section it tests and add a `[PAST PAPER Q{n}]` annotation.
4. **Cross-class comparison** (if multiple review sessions exist): compare outlines
   side by side. Points that appear in every session → mark `[HIGH FREQ]`.
   Points unique to one session → mark `[LOW FREQ / verify]`.

```python
# Pseudocode outline — adapt to your actual data structures

outline = {}   # slide_index -> {title, bullets, transcript_notes, past_paper_refs}

for slide_idx, slide_text in enumerate(slides):
    outline[slide_idx] = {
        "title": slide_text.splitlines()[0] if slide_text else f"Slide {slide_idx+1}",
        "bullets": slide_text.splitlines()[1:],
        "transcript_notes": [],
        "past_paper_refs": [],
    }

for seg in segments:
    idx = seg["slide"]
    note = ("[KEY] " if seg["is_key_point"] else "") + seg["text"]
    outline[idx]["transcript_notes"].append(note)

for q_num, (q_text, q_slide) in enumerate(past_paper_questions, start=1):
    outline[q_slide]["past_paper_refs"].append(f"Q{q_num}: {q_text[:80]}")
```

---

## 4. Output: `源内容.md`

Write the reconciled outline as a structured Markdown file. Every downstream
generator (flashcard builder, mock-paper generator, review HTML) reads this file
and nothing else.

```python
from pathlib import Path

lines = ["# 源内容 (Source Content Outline)\n",
         "> Auto-generated — do not edit by hand. Re-run extraction to update.\n"]

for idx, section in outline.items():
    lines.append(f"\n## {section['title']}")
    for bullet in section["bullets"]:
        if bullet.strip():
            lines.append(f"- {bullet.strip()}")
    if section["transcript_notes"]:
        lines.append("\n**Transcript notes (讲课要点):**")
        for note in section["transcript_notes"]:
            lines.append(f"  - {note}")
    if section["past_paper_refs"]:
        lines.append("\n**Past paper links (历年真题):**")
        for ref in section["past_paper_refs"]:
            lines.append(f"  - {ref}")

Path("源内容.md").write_text("\n".join(lines), encoding="utf-8")
print("源内容.md written.")
```

### Quality checklist before handing off to generators

- [ ] Every tested point has a source annotation (slide number, transcript
      timestamp, or past-paper question number).
- [ ] No section is sourced only from general knowledge.
- [ ] Emphasis-flagged segments (`[KEY]`) have been manually verified against
      the slide content — ASR mis-transcription can produce false positives.
- [ ] If multiple review classes exist, `[HIGH FREQ]` vs `[LOW FREQ]` labels
      have been applied.
- [ ] Images referenced as `[IMAGE: path]` have been visually inspected;
      add a brief caption if the image contains formulas or diagrams not in the text.
