# Question-Bank Pipeline
## 命题 → 审校 → 合并/打乱/注入 → 验证

This document describes the multi-agent pipeline for producing a reproducible, bias-free exam-sprint quiz from raw question banks.

---

## 1. Generate — 命题阶段

One agent is spawned **per chapter / topic** to generate questions grounded in the source outline or lecture notes.

### JSON Question Schema

Every question must be a JSON object matching this shape:

```json
{
  "id":          "ch01_q003",
  "type":        "single | multi | fill | short | code",
  "chapter":     "Chapter 1 — Number Systems",
  "stem":        "Question text (bilingual encouraged)",
  "options":     ["…"],
  "answer":      "see type table below",
  "explanation": "Why this answer is correct. Required — if the source has none, the model writes one.",
  "tags":        ["unsigned", "overflow"]
}
```

#### Per-type `answer` contract

| `type`   | `options` | `answer` shape | Notes |
|----------|-----------|----------------|-------|
| `single` | required  | `int` — 0-based index into `options` | Shuffle applied at build time |
| `multi`  | required  | `int[]` — sorted indices of all correct options | Shuffle applied at build time |
| `fill`   | omit      | `string[][]` — outer = blanks, inner = accepted variants | Single-blank shorthand: `["ans"]` → normalized to `[["ans"]]` |
| `short`  | omit      | `string` — model answer (may be multi-line) | Graded by instructor; no auto-check |
| `code`   | omit      | `{"code": "…", "explanation": "…"}` | Both fields required |

#### Authoring rules

- `id` must be unique across the entire bank. Convention: `ch<NN>_q<NNN>` (zero-padded).
- Every `explanation` field must be non-empty. If the source material gives no justification, the generating agent must derive one.
- Options for `single`/`multi` should all be plausible distractors — avoid obviously wrong choices.
- Prefer bilingual stems (Chinese keyword + English gloss) for maximum reuse.

---

## 2. Adversarial Proofread — 对抗审校

A **separate, second agent** processes each chapter's batch. Its job is to *try to refute* every answer before accepting it. Default stance: skeptical.

### Checklist

1. Verify the answer index is correct against the options array (off-by-one is common when copy-pasting).
2. Re-derive any numeric answer independently.
3. Flag ambiguous distractors (a "wrong" option that is actually correct under some interpretation).
4. Check `explanation` for internal consistency with `answer`.
5. For `code` questions: mentally compile the snippet; check for undefined behavior, wrong types, missing includes.

### Real Failure Examples Caught by This Stage

These bugs slipped through without adversarial review and were caught only at this stage:

| Bug class | Example |
|-----------|---------|
| **signed/unsigned comparison** | A question claimed `(signed char)0xFF > 0` is true. Wrong: `(signed char)0xFF` is `-1` on two's-complement hardware, so the comparison is false. The generating agent confused the bit pattern with the unsigned value. |
| **idle-value typo** | An MCU GPIO idle-high configuration used mask `0x0f` instead of the correct `0xf0`, reversing which nibble was affected. A reader familiar with the register layout catches this immediately; the first-pass agent does not. |
| **wrong serial-config constant** | A `SCON` initialization question listed `0x50` (SM0=0, SM1=1, REN=1 — mode 1, receive enabled) but the stem described mode 2. The constant and the prose disagreed. |
| **baud-rate magic value** | A Timer 1 reload constant was given as `0xFD` (correct for 9600 baud at 11.0592 MHz, SMOD=0). The adversarial agent recomputed it: `256 − (11059200 / (384 × 9600)) = 256 − 3 = 253 = 0xFD` — confirmed. However, a variant question at 11.0592 MHz with SMOD=1 (doubles baud clock) used the same `0xFD`; the correct value there is `0xFA`. Caught and corrected. |

### Output

The adversarial agent returns either:
- The **same JSON** (no changes) if all answers are correct, or
- A **corrected JSON patch** with a `_review` field explaining each change.

The merge step discards `_review` fields before writing the final bank.

---

## 3. Merge — 合并阶段

```
ch01.json  ch02.json  ch03.json  …
       ↓  collect_bank_files()
       ↓  load + normalize per question
       ↓  dedup check on ids
       →  all_questions[]
```

Steps performed by `build_quiz.py --banks <dir>`:

1. **Collect**: glob all `*.json` files in the banks directory, sorted deterministically.
2. **Load**: UTF-8, `json.load`. Parse errors are collected and reported; the file is skipped.
3. **Normalize**: type aliases resolved (`choice` → `single`); legacy field names remapped (`explain` → `explanation`, `chTitle` → `chapter`); `tags` defaulted to `[]`.
4. **Deduplicate**: duplicate `id` values are flagged as errors. First occurrence wins.
5. **Validate structure**: required fields checked (`id`, `type`, `stem`, `answer`); answer indices range-checked.

---

## 4. Deterministic Option Shuffle — 确定性选项打乱

### Why this matters — positional bias (位置偏差)

Naive question generators tend to put the correct answer at `options[0]` before any shuffling, because they write the correct answer first. If you then shuffle with `random.shuffle()` using a global random state seeded by time, two problems arise:

1. Different runs produce different orderings → impossible to reproduce a specific quiz.
2. Statistical audits of real generated banks have shown answer-index 0 appearing 40–60 % of the time even after "shuffling", because many generators re-seed at import time or don't shuffle at all.

### Algorithm

For each `single` or `multi` question:

```python
import hashlib, random

def seed_of(qid: str) -> int:
    """Deterministic integer seed derived from question id."""
    return int(hashlib.md5(qid.encode("utf-8")).hexdigest(), 16) % (2**31)

# single
order = list(range(len(opts)))
random.Random(seed_of(qid)).shuffle(order)
new_opts   = [opts[i] for i in order]
new_answer = order.index(original_answer_index)

# multi — same shuffle, remap all correct indices
new_answers = sorted(order.index(i) for i in original_answer_indices)
```

Key properties:
- **Reproducible**: same `id` always produces the same shuffle across machines and Python versions (md5 is deterministic; `random.Random` with an integer seed is deterministic within CPython's Mersenne Twister).
- **Independent per question**: shuffling `ch01_q001` does not affect the RNG state for `ch01_q002`.
- **Answer remapped**: `answer` always reflects the *post-shuffle* index, so the runtime engine reads it directly.

### Verifying Balance

After building, print and inspect:

```
Single-choice answer-index distribution: {0: 12, 1: 11, 2: 9, 3: 10}
  (percentages) {0: '28.6%', 1: '26.2%', 2: '21.4%', 3: '23.8%'}
```

A balanced bank should show no index exceeding ~35 % for 4-option questions. If one index dominates, suspect authoring bias — most questions were written with the correct answer at that position and the shuffle is not operating (e.g., wrong field name).

---

## 5. Inject — 注入阶段

The HTML template contains exactly one placeholder token (default `/*__BANK__*/[]`):

```html
<script>
const BANK = /*__BANK__*/[];
</script>
```

`build_quiz.py` replaces this token with the compact JSON dump of `all_questions`:

```python
bank_json = json.dumps(all_q, ensure_ascii=False, separators=(",", ":"))
html = html.replace(placeholder, bank_json, 1)   # replace exactly once
```

`ensure_ascii=False` preserves Chinese characters. `separators=(",",":")` produces compact JSON (no extra whitespace).

The replacement is performed **exactly once** (`str.replace(..., 1)`). If the placeholder appears zero times, the script aborts with a clear error.

---

## 6. Verify — 验证阶段

`build_quiz.py` performs these checks before writing output, collecting all errors and printing a report:

| Check | How |
|-------|-----|
| Valid JSON per file | `json.load` with exception catch |
| Top-level is array | `isinstance(data, list)` |
| Required fields present | `{"id","type","stem","answer"} ⊆ q.keys()` |
| No duplicate ids | `Counter(ids)` — flag any count > 1 |
| Answer index in range | For `single`: `0 <= answer < len(options)`; for `multi`: all elements in range |
| Balanced distribution | Print distribution; human inspects |
| Placeholder present | Abort if token not found in template |

Non-fatal problems (e.g., a single malformed question) are collected and printed at the end; the build continues with the remaining valid questions. Fatal problems (no valid questions, missing template, missing placeholder) cause an immediate `sys.exit(1)`.
