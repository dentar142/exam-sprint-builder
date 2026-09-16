# Exam Sprint Builder — Independent Verification Pass

> Run this pass **before** claiming a deliverable is complete.
> The verifier is a separate role: never self-approve in the same context that produced the file.
> Evidence must be shown inline (command output, counts, pass/fail lines) — assertions without evidence do not count.

**Source of truth for HTML checks is `scripts/verify_html.py`.** It runs **4** pass/fail checks. Structural counts are informational only.

**Do not run the verifier on uninjected templates.**
`assets/templates/*.html` still contain `__BANK__`, `__CONTENT__`, or `__SECTIONS__` and **must** fail check (b). Verify only generated outputs after injection.

The script does **not** flag the JavaScript keyword `undefined`, HTML `placeholder=` attributes, or `TODO`/`FIXME` in legitimate quiz text.

---

## 1. HTML deliverables — run the script

```bash
python scripts/verify_html.py target.html
```

Expected verdict:

```
========== VERDICT ==========
PASS  (4/4 checks passed)
```

| # | Check | What fails it |
|---|-------|----------------|
| (a) | No external URLs / CDN hostnames | `http://`, `https://`, or `cdn.` / `unpkg.` / `jsdelivr.` / `googleapis.` / `cloudflare.` / `gstatic.` / `fastly.` |
| (b) | No placeholder residue | leftover `__BANK__`, `__CONTENT__`, `__SECTIONS__`, `/*__…*/`, `<!--__…-->`, PUA `U+E000`/`U+E001`, `INSERT_HERE`, `lorem ipsum` |
| (c) | Theme markers | missing `data-theme`, `esb-theme`, or a theme-toggle hook |
| (e) | File size | ≥ 5 MB (accidental binary embed) |

Check (d) prints table / `<pre>` / callout / `<script>` counts and does **not** affect the verdict.

Any `FAIL` line must be resolved before shipping. Re-run after every post-generation edit.

### 1b. JS syntax (optional extra; not counted in 4/4)

Python cannot parse JavaScript. If Node is available, extract inline `<script>` blocks in-process — **there is no `scripts/extract_scripts.py`**. Write the extractor to a file first on Windows (do not embed backslash paths in `node -e`).

```js
// check-scripts.js — pass the HTML path as argv[2]
const fs = require("fs");
const vm = require("vm");
const html = fs.readFileSync(process.argv[2], "utf8");
const re = /<script(?![^>]*src)[^>]*>([\s\S]*?)<\/script>/gi;
let m, i = 0, fail = 0;
while ((m = re.exec(html)) !== null) {
  const src = m[1].trim();
  if (!src) continue;
  try {
    new vm.Script(src);
    console.log("PASS script block", ++i);
  } catch (e) {
    console.error("FAIL script block", ++i, e.message);
    fail++;
  }
}
process.exitCode = fail ? 1 : 0;
```

```bash
node check-scripts.js target.html
```

### 1c. `file://` smoke check

Open the generated file from the filesystem (no `localhost`):

```bash
# Linux/macOS
xdg-open target.html
# Windows
start target.html
```

CORS / mixed-content console errors are a FAIL.

---

## 2. Quiz bank JSON

Canonical shape: a **top-level JSON array**. Required fields per question: `id`, `type`, `stem`, `answer`. `explanation` should be non-empty. Stem field is **`stem`**, not `text`.

Prefer letting `scripts/build_quiz.py` load and normalize the bank (it already checks types, duplicate ids, and index ranges). Manual Node checks below assume the same array contract.

### 2a. Valid JSON array

```bash
python -m json.tool quiz_bank.json > /dev/null && echo PASS || echo FAIL
```

### 2b. Required fields

```bash
node check-bank-fields.js quiz_bank.json
```

```js
// check-bank-fields.js
const qs = JSON.parse(require("fs").readFileSync(process.argv[2], "utf8"));
if (!Array.isArray(qs)) {
  console.error("FAIL: top-level value must be a JSON array");
  process.exit(1);
}
const required = ["id", "type", "stem", "answer"];
let fail = 0;
qs.forEach((q, i) => {
  required.forEach((f) => {
    if (q[f] === undefined || q[f] === null || q[f] === "") {
      console.error("FAIL q[" + i + "] missing field:", f);
      fail++;
    }
  });
});
if (!fail) console.log("PASS: all required fields present in", qs.length, "questions");
process.exitCode = fail ? 1 : 0;
```

### 2c. Answer indices in range

For `type: single`, `answer` is an int index into `options`. For `multi`, every index in the array must be in range.

### 2d. No duplicate ids

`id` values must be unique across the merged bank.

### 2e. Answer-index distribution

After `build_quiz.py` shuffle, no single index should exceed ~40% of single-choice answers (the builder warns above 40%; treat > 60% as a hard fail). Clustering at `0` usually means the shuffle did not run.

---

## 3. Subject-specific content check

Verify that key magic values for the *this* subject appear in the generated file. The list is supplied at verification time — do not reuse another course's constants.

```bash
for val in "0xFD" "0x20"; do
    grep -qF "$val" target.html && echo "PASS: $val" || echo "FAIL: $val missing"
done
```

---

## 4. Sample-bank fixture

From the repo root:

```bash
python scripts/run_sample_fixture.py
```

This builds `examples/sample-bank/bank.json` into both quiz templates in a temp directory, then runs `verify_html.py` on each output. It does **not** overwrite `examples/sample-bank/sample-quiz.html`.

---

## 5. Process discipline

| Step | Required |
|---|---|
| Run `verify_html.py` on every **generated** HTML output | Yes |
| Do **not** run it on raw templates in `assets/templates/` | Yes |
| Run quiz-bank checks (or `build_quiz.py`) on every JSON bank | Yes |
| Run magic-values check with a subject-specific list | Yes |
| Show raw command output (not just "it passed") | Yes |
| Claim completion only after checks pass | Yes |
| Re-run after any post-generation edit | Yes |

**Never** accept a human statement like "it looks fine" as verification. Run the commands, show the output, count the PASSes.
