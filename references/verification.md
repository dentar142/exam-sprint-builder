# Exam Sprint Builder — Independent Verification Pass

> Run this pass **before** claiming a deliverable is complete.
> The verifier is a separate role: never self-approve in the same context that produced the file.
> Evidence must be shown inline (command output, counts, pass/fail lines) — assertions without evidence do not count.

---

## 1. HTML Deliverables

### 1a. No External URLs

Regex scan for any `http://` or `https://` URL, plus known CDN hostnames even without a scheme.

```bash
# Fail if any external URL found
grep -En "https?://" target.html
grep -Ein "cdn\.|unpkg\.|jsdelivr\.|googleapis\.|cloudflare\.|gstatic\." target.html
```

Expected output: **no matches**. Any match is an automatic FAIL.

Also check `<link>`, `<script src=`, `<img src=`, and `url()` in CSS:

```bash
grep -En "<(link|script|img)[^>]+src\s*=\s*[\"']https?://" target.html
grep -En "url\s*\(\s*https?://" target.html
```

### 1b. JS Syntax Checking (via Node)

Extract each `<script>` block and check it parses. Python cannot parse JS, so this step uses Node.

```bash
# Extract all inline <script> blocks and check syntax
python scripts/extract_scripts.py target.html | while read tmpfile; do
    node --check "$tmpfile" && echo "PASS: $tmpfile" || echo "FAIL: $tmpfile"
done
```

Or with a one-liner using Node's `vm.Script`:

```bash
node -e "
const fs = require('fs');
const html = fs.readFileSync('target.html', 'utf8');
const re = /<script(?![^>]*src)[^>]*>([\s\S]*?)<\/script>/gi;
let m, i = 0;
while ((m = re.exec(html)) !== null) {
  const src = m[1].trim();
  if (!src) continue;
  try {
    new (require('vm').Script)(src);
    console.log('PASS script block', ++i);
  } catch(e) {
    console.error('FAIL script block', ++i, e.message);
    process.exitCode = 1;
  }
}
"
```

Expected: every block prints `PASS script block N`. Any `FAIL` line is a blocker.

### 1c. No Placeholder Residue

Check that no template placeholders or encoding artifacts survived rendering.

```bash
grep -En "__BANK__|/\*__|undefined|[-]" target.html
```

Also check for common generator artifacts:

```bash
grep -En "TODO|FIXME|INSERT_HERE|PLACEHOLDER|lorem ipsum" target.html
```

Expected: **no matches**. Stray `undefined` (even as JS runtime output) is a FAIL — the bank must have been substituted before writing the file.

### 1d. Theme Toggle + `esb-theme` Present

```bash
grep -c "esb-theme" target.html          # must be >= 2 (write + read)
grep -c "data-theme" target.html         # must be >= 1
grep -c "theme-toggle\|themeToggle\|toggleTheme" target.html  # must be >= 1
```

Manual check: open the file in a browser, click the toggle, reload — the chosen theme must persist.

### 1e. `file://` Openable

```bash
# On Linux/macOS:
xdg-open target.html
# On Windows:
start target.html
```

No "blocked" security dialogs expected for a pure HTML/CSS/JS file with no external loads.
Any browser console error relating to CORS or mixed content is a FAIL.

---

## 2. Quiz Bank JSON

### 2a. Valid JSON

```bash
python -m json.tool quiz_bank.json > /dev/null && echo PASS || echo FAIL
# or
node -e "JSON.parse(require('fs').readFileSync('quiz_bank.json','utf8')); console.log('PASS')"
```

### 2b. Required Fields Present

Every question object must have: `id`, `type`, `chapter`, `text`, `answer`, `explanation`.

```bash
node -e "
const qs = JSON.parse(require('fs').readFileSync('quiz_bank.json','utf8')).questions;
const required = ['id','type','chapter','text','answer','explanation'];
let fail = 0;
qs.forEach((q, i) => {
  required.forEach(f => {
    if (q[f] === undefined || q[f] === null || q[f] === '') {
      console.error('FAIL q[' + i + '] missing field:', f);
      fail++;
    }
  });
});
if (!fail) console.log('PASS: all required fields present in', qs.length, 'questions');
process.exitCode = fail ? 1 : 0;
"
```

### 2c. Answer Indices In Range

For `type: single`, `answer` must be a valid index into `options`.

```bash
node -e "
const qs = JSON.parse(require('fs').readFileSync('quiz_bank.json','utf8')).questions;
let fail = 0;
qs.filter(q => q.type === 'single').forEach((q, i) => {
  if (!Array.isArray(q.options) || q.answer < 0 || q.answer >= q.options.length) {
    console.error('FAIL single q id=' + q.id + ': answer index out of range');
    fail++;
  }
});
if (!fail) console.log('PASS: all single-choice answer indices in range');
process.exitCode = fail ? 1 : 0;
"
```

### 2d. No Duplicate IDs

```bash
node -e "
const qs = JSON.parse(require('fs').readFileSync('quiz_bank.json','utf8')).questions;
const ids = qs.map(q => q.id);
const dupes = ids.filter((id, i) => ids.indexOf(id) !== i);
if (dupes.length) { console.error('FAIL duplicates:', dupes); process.exitCode = 1; }
else console.log('PASS: no duplicate ids');
"
```

### 2e. Answer-Index Distribution Balanced

For single-choice questions, the correct answer should not cluster at index 0 (which indicates a generation artifact where all answers defaulted to option A).

```bash
node -e "
const qs = JSON.parse(require('fs').readFileSync('quiz_bank.json','utf8')).questions
  .filter(q => q.type === 'single');
const counts = {};
qs.forEach(q => counts[q.answer] = (counts[q.answer] || 0) + 1);
const total = qs.length;
console.log('Answer distribution:', JSON.stringify(counts));
const maxShare = Math.max(...Object.values(counts)) / total;
if (maxShare > 0.6) {
  console.error('FAIL: answer index distribution skewed — index', Object.keys(counts).find(k => counts[k] === Math.max(...Object.values(counts))), 'is', (maxShare*100).toFixed(0) + '% of answers');
  process.exitCode = 1;
} else {
  console.log('PASS: no single index > 60% of answers');
}
"
```

---

## 3. Subject-Specific Content Check

Verify that the key magic values for the target subject actually appear in the generated file. The exact list is supplied by the caller at verification time.

**Generic example** (substitute real values for your subject):

Suppose the subject is a microcontroller unit (MCU) course. The magic-values list might be:

```
TMOD = 0x20
TH1 = 0xFD
IE = 0x85
PCON = 0x80
P1 = 0x90
```

Check command:

```bash
# Read magic values from a file, one per line; grep each in the HTML
while IFS= read -r val; do
    grep -qF "$val" target.html && echo "PASS: $val found" || echo "FAIL: $val not found"
done < magic_values.txt
```

Or inline:

```bash
for val in "0xFD" "0x20" "0x85"; do
    grep -qF "$val" target.html && echo "PASS: $val" || echo "FAIL: $val missing"
done
```

All listed magic values must appear somewhere in the file. Missing values indicate incomplete content generation.

---

## 4. Python Verifier Script

Run the bundled script for checks (a)–(d) in one shot:

```bash
python scripts/verify_html.py target.html
```

Expected output ends with:

```
========== VERDICT ==========
PASS  (6/6 checks passed)
```

Any `FAIL` line in the output must be resolved before shipping the deliverable.

For JS syntax, run separately:

```bash
node -e "/* see section 1b */"
```

---

## 5. Process Discipline

| Step | Required |
|---|---|
| Run `verify_html.py` on every HTML output | Yes |
| Run quiz bank checks on every JSON bank | Yes |
| Run magic-values check with subject-specific list | Yes |
| Run JS syntax check via Node | Yes |
| Show raw command output (not just "it passed") | Yes |
| Claim completion only after all checks pass | Yes |
| Re-run after any post-generation edit | Yes |

**Never** accept a human statement like "it looks fine" as verification. Run the commands, show the output, count the PASSes.
