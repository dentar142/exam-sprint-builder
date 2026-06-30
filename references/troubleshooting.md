# Troubleshooting Guide — exam-sprint-builder

Real pitfalls encountered during the session that produced this skill, each documented as **Symptom → Cause → Fix**.

---

## 1. Windows Console GBK Mojibake

**Symptom:** Chinese characters display as garbage (`鍗曠墖鏈?`) in the Windows terminal, even though the source file looks correct in a proper editor.

**Cause:** Windows console (cmd.exe, older PowerShell hosts) defaults to GBK/CP936 codepage. Files on disk are valid UTF-8, but the console misinterprets them.

**Fix:** Trust the Read/Grep tools, not `echo` or console output. Do not "fix" files based on what the console shows — the bytes are correct. If you must verify encoding in the shell, use `[System.IO.File]::ReadAllText(path)` in PowerShell with explicit `[System.Text.Encoding]::UTF8`, or a Node snippet that prints char codes.

---

## 2. `node -e '...'` Mangles Backslash Windows Paths

**Symptom:** A path like `C:\Users\Neko\file.js` passed inside `node -e "..."` becomes `C:UsersNekofile.js` at runtime — backslashes silently consumed.

**Cause:** The shell (cmd.exe or bash) processes the inline string before Node.js sees it, eating every `\` as an escape character.

**Fix:** Write the Node script to a `.js` file first, then invoke `node script.js`. Never embed Windows absolute paths with backslashes in a `-e` one-liner. If the path must be dynamic, pass it as an environment variable (`$env:TARGET_PATH = "C:\..."`) and read `process.env.TARGET_PATH` inside the script.

---

## 3. Bank-Extraction Regex Stops Early

**Symptom:** The question-bank extractor only captures the first few questions; the rest are silently dropped.

**Cause:** The regex `/const BANK = (\[[\s\S]*?\]);/` uses a lazy quantifier (`*?`) and stops at the first `];` it finds. Question banks that contain embedded C code — e.g. `arr[i];` inside a code snippet — contain `];` substrings, triggering the early stop.

**Fix:** Replace the regex with a bracket-depth counter that walks the source character by character, tracking `[` / `]` depth while respecting string literals (single-quoted, double-quoted, template literals, and C-style string spans inside code blocks). Only close the bank array when depth returns to zero.

```js
function extractBank(src) {
  const start = src.indexOf('const BANK = [');
  if (start === -1) throw new Error('BANK not found');
  let depth = 0, inStr = false, strChar = '', i = start + 'const BANK = '.length;
  const out = [];
  for (; i < src.length; i++) {
    const ch = src[i];
    if (inStr) {
      if (ch === '\\') { i++; continue; }
      if (ch === strChar) inStr = false;
    } else {
      if (ch === '"' || ch === "'" || ch === '`') { inStr = true; strChar = ch; }
      else if (ch === '[') depth++;
      else if (ch === ']') { if (--depth === 0) { out.push(ch); break; } }
    }
    out.push(ch);
  }
  return out.join('');
}
```

---

## 4. PUA Sentinels Look Empty / Missing

**Symptom:** Code-span protection replaces backtick spans with sentinel characters before Markdown processing, but the sentinels appear "missing" or blank in editors and diffs — developers delete them, breaking the round-trip.

**Cause:** The sentinels use Private Use Area code points (`U+E000`, `U+E001`), which are valid Unicode but render as invisible or as boxes in most fonts. They look like empty strings.

**Fix:** Do not delete or "repair" invisible characters in the protected source. Verify sentinel presence with a char-code script rather than visual inspection:

```js
const s = require('fs').readFileSync('file.html', 'utf8');
[...s].forEach((c, i) => {
  const cp = c.codePointAt(0);
  if (cp >= 0xE000 && cp <= 0xF8FF) console.log(`PUA at ${i}: U+${cp.toString(16).toUpperCase()}`);
});
```

---

## 5. zip Directory Entries Break Image Extraction

**Symptom:** When extracting images from a `.docx` file (which is a ZIP archive), the script crashes with an error about an empty filename or tries to write a file with no name.

**Cause:** `namelist()` (Python `zipfile`) includes directory entries such as `word/media/` — a path that ends with `/` and has an empty `basename`. Passing this to `open()` as a write target raises an error.

**Fix:** Guard the extraction loop:

```python
for name in z.namelist():
    if name.startswith('word/media/') and not name.endswith('/'):
        # safe to extract
        data = z.read(name)
        out_path = output_dir / Path(name).name
        out_path.write_bytes(data)
```

---

## 6. Positional Answer Bias

**Symptom:** Generated multiple-choice questions always show the correct answer as option A (index 0). Students quickly notice the pattern.

**Cause:** A naive generator appends the correct answer first, then fills in distractors — producing a deterministic ordering with no shuffle.

**Fix:** After assembling the option list, shuffle with a deterministic seed derived from the question content (e.g. `md5(question_text)` mod `N!`). This ensures the correct answer lands at a different index for each question, but remains stable across regeneration runs (same input → same layout), which is important for reproducible answer keys.

---

## 7. `.cmd` File with Chinese Content Parses as GBK

**Symptom:** A `.cmd` batch file saved as UTF-8 that contains Chinese characters fails to run or displays garbled output; in some cases `cmd.exe` refuses to parse it at all.

**Cause:** `cmd.exe` reads `.cmd` files using the system codepage (GBK on Chinese-locale Windows), not UTF-8, even if the file has a UTF-8 BOM.

**Fix:** Use one of:
- Keep the `.cmd` body **pure ASCII** — move all Chinese strings into a separate UTF-8 file that the batch reads at runtime with `type`.
- Replace the `.cmd` with a `.ps1` PowerShell script and write files with `-Encoding utf8`.
- Use a Node or Python launcher script instead of batch.

---

## 8. ES Modules Fail Under `file://`

**Symptom:** An HTML page that uses `<script type="module">` works fine when served over HTTP but shows `Cross-Origin Request Blocked` or `Failed to load module script` when opened directly from disk (`file://`).

**Cause:** Browsers enforce CORS for ES module imports even under `file://`. A module loading another module from the same directory is blocked because `file://` origins are treated as opaque/null.

**Fix:** Use only **inline classic scripts** (`<script>` without `type="module"`). Bundle all JS into a single `<script>` block inside the HTML, or use an IIFE pattern. This keeps the deliverable fully offline and openable by double-clicking.

---

## 9. faster-whisper First-Run Model Download

**Symptom:** The transcription step hangs or takes unexpectedly long on the first run with no apparent progress.

**Cause:** `faster-whisper` downloads the Whisper model weights from HuggingFace Hub on first use. The `base` model is ~145 MB; larger models are several GB. This requires a working internet connection and significant time.

**Fix:** Document this in setup instructions. For offline-first use, pre-download the model once (`faster_whisper.WhisperModel("base", download_root="./models")`) and commit the `models/` path to `.gitignore` with instructions to run the download step separately. On subsequent runs the cached model is used immediately.

---

## 10. ffmpeg Scene-Change Threshold Too High

**Symptom:** Slide extraction from a lecture recording produces very few output images — major slide transitions are missed.

**Cause:** The `select='gt(scene,THRESHOLD)'` ffmpeg filter is too conservative. A high threshold (e.g. `0.5`) only fires on very dramatic visual changes; gradual slide animations or low-contrast transitions are skipped.

**Fix:** Tune the threshold between `0.03` and `0.1`. Start at `0.05` and adjust based on output count vs. expected slide count. Also consider using `-fps_mode vfr` with a minimum frame interval to avoid extracting near-duplicate frames during animations.

```bash
ffmpeg -i lecture.mp4 -vf "select='gt(scene,0.05)',scale=1280:-1" -vsync vfr slide_%04d.jpg
```
