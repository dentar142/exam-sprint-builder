# -*- coding: utf-8 -*-
"""
build_quiz.py — generalized exam-sprint quiz builder

Usage:
    python build_quiz.py --banks <dir-or-glob> --template <html> --out <html>
                         [--placeholder <token>]

Stdlib-only (+ hashlib). Requires Python 3.7+.
"""

import argparse
import glob
import hashlib
import io
import json
import os
import random
import sys
from collections import Counter


# ---------------------------------------------------------------------------
# Seed / shuffle helpers
# ---------------------------------------------------------------------------

def seed_of(qid):
    """Deterministic integer seed derived from question id via MD5."""
    return int(hashlib.md5(qid.encode("utf-8")).hexdigest(), 16) % (2 ** 31)


def shuffle_single(opts, answer_idx, qid):
    """
    Shuffle options with a deterministic, question-specific seed.
    Returns (new_opts, new_answer_idx).
    Prevents positional bias from naive generators that always write
    the correct option first.
    """
    order = list(range(len(opts)))
    random.Random(seed_of(qid)).shuffle(order)
    new_opts = [opts[i] for i in order]
    new_answer = order.index(answer_idx)
    return new_opts, new_answer


def shuffle_multi(opts, answer_indices, qid):
    """
    Same deterministic shuffle for multi-select questions.
    Returns (new_opts, sorted_new_answer_indices).
    """
    order = list(range(len(opts)))
    random.Random(seed_of(qid)).shuffle(order)
    new_opts = [opts[i] for i in order]
    new_answers = sorted(order.index(i) for i in answer_indices)
    return new_opts, new_answers


# ---------------------------------------------------------------------------
# File collection
# ---------------------------------------------------------------------------

def collect_bank_files(banks_arg):
    """
    Accept a directory path or a glob pattern.
    Returns a sorted list of .json file paths.
    """
    if os.path.isdir(banks_arg):
        pattern = os.path.join(banks_arg, "*.json")
    else:
        pattern = banks_arg
    files = sorted(glob.glob(pattern))
    if not files:
        print("[WARN] No JSON files matched: {}".format(banks_arg), file=sys.stderr)
    return files


def load_json(fp):
    with io.open(fp, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

def normalize_question(raw, problems):
    """
    Normalize a raw question dict to canonical schema.

    Type aliases resolved:
      'choice'  -> 'single'   (legacy single-select name)

    Legacy field renames:
      'explain'  -> 'explanation'
      'chTitle'  -> 'chapter'
      'tag'      -> 'tags' (string -> list)

    Returns the normalized dict, or None on a fatal structural error
    (the error description is appended to `problems`).
    """
    q = dict(raw)  # shallow copy; caller owns original

    # --- type alias ---
    if q.get("type") == "choice":
        q["type"] = "single"

    # --- legacy field renames ---
    if "explain" in q and "explanation" not in q:
        q["explanation"] = q.pop("explain")
    q.setdefault("explanation", "")

    if "chTitle" in q and "chapter" not in q:
        q["chapter"] = q.pop("chTitle")
    q.setdefault("chapter", "")

    if "tag" in q and "tags" not in q:
        raw_tag = q.pop("tag")
        q["tags"] = [raw_tag] if isinstance(raw_tag, str) and raw_tag else []
    q.setdefault("tags", [])

    qid = q.get("id", "<unknown>")
    t = q.get("type")

    # --- per-type normalization + shuffle ---
    if t == "single":
        opts = q.get("options")
        ai = q.get("answer")
        if not (isinstance(opts, list) and len(opts) >= 2
                and isinstance(ai, int) and 0 <= ai < len(opts)):
            problems.append(
                "{}: single — options must be list of >=2, answer must be int in range".format(qid)
            )
            return None
        q["options"], q["answer"] = shuffle_single(opts, ai, qid)

    elif t == "multi":
        opts = q.get("options")
        ai = q.get("answer")
        if not (isinstance(opts, list) and len(opts) >= 2
                and isinstance(ai, list) and len(ai) >= 1
                and all(isinstance(x, int) and 0 <= x < len(opts) for x in ai)):
            problems.append(
                "{}: multi — options must be list of >=2, answer must be non-empty int[] in range".format(qid)
            )
            return None
        q["options"], q["answer"] = shuffle_multi(opts, ai, qid)

    elif t == "fill":
        a = q.get("answer")
        # Normalize to list-of-lists: outer = blanks, inner = accepted variants
        if isinstance(a, str):
            a = [[a]]
        elif isinstance(a, list) and len(a) > 0 and isinstance(a[0], str):
            # Single blank given as flat list of accepted strings
            a = [a]
        elif isinstance(a, list) and len(a) > 0 and isinstance(a[0], list):
            pass  # already multi-blank form
        else:
            problems.append("{}: fill — answer must be str, str[], or str[][]".format(qid))
            return None
        q["answer"] = [[str(x) for x in blk] for blk in a]

    elif t == "short":
        a = q.get("answer")
        if isinstance(a, list):
            a = "\n".join(str(x) for x in a)
        if not a:
            problems.append("{}: short — answer is empty".format(qid))
            return None
        q["answer"] = str(a)

    elif t == "code":
        a = q.get("answer")
        if not (isinstance(a, dict) and a.get("code")):
            problems.append(
                '{}: code — answer must be {{"code": "...", "explanation": "..."}}'.format(qid)
            )
            return None
        a.setdefault("explanation", "")
        q["answer"] = a

    else:
        problems.append("{}: unknown type {!r}".format(qid, t))
        return None

    return q


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_bank(questions, problems):
    """Post-normalization checks: duplicate ids, required fields."""
    ids = [q.get("id") for q in questions]
    dups = [k for k, v in Counter(ids).items() if v > 1]
    if dups:
        problems.append("Duplicate ids: " + ", ".join(str(d) for d in dups))

    required = {"id", "type", "stem", "answer"}
    for q in questions:
        missing = required - set(q.keys())
        if missing:
            problems.append("{}: missing required fields {}".format(q.get("id"), missing))


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_statistics(questions):
    by_type = Counter(q["type"] for q in questions)
    print("  Total questions : {}".format(len(questions)))
    print("  By type         : {}".format(dict(by_type)))

    single_qs = [q for q in questions if q["type"] == "single"]
    if single_qs:
        dist = Counter(q["answer"] for q in single_qs)
        n = len(single_qs)
        pct = {k: "{:.1f}%".format(v / n * 100) for k, v in sorted(dist.items())}
        print("  Single-choice answer-index distribution: {}".format(dict(sorted(dist.items()))))
        print("    (percentages) {}".format(pct))
        # Bias warning: any index > 40% for 4-option questions is suspicious
        max_pct = max(v / n for v in dist.values()) * 100
        if max_pct > 40.0:
            print("  [WARN] Answer-index distribution imbalanced "
                  "(max {:.1f}%). Check for authoring positional bias.".format(max_pct))

    multi_qs = [q for q in questions if q["type"] == "multi"]
    if multi_qs:
        print("  Multi-select questions: {}".format(len(multi_qs)))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Build an exam-sprint quiz HTML from JSON question banks.\n"
            "Applies deterministic MD5-seeded option shuffle to eliminate positional bias."
        )
    )
    parser.add_argument(
        "--banks", required=True,
        help="Directory containing *.json bank files, or a glob pattern (e.g. 'banks/ch*.json')."
    )
    parser.add_argument(
        "--template", required=True,
        help="Path to the HTML template file."
    )
    parser.add_argument(
        "--out", required=True,
        help="Path for the output HTML file."
    )
    parser.add_argument(
        "--placeholder", default="/*__BANK__*/[]",
        help="Token in the template replaced by the bank JSON. Default: /*__BANK__*/[]"
    )
    args = parser.parse_args()

    # --- collect ---
    bank_files = collect_bank_files(args.banks)
    print("[build_quiz] Bank files found: {}".format(len(bank_files)))
    for fp in bank_files:
        print("  {}".format(fp))

    # --- load + normalize ---
    problems = []
    all_q = []
    for fp in bank_files:
        name = os.path.basename(fp)
        try:
            data = load_json(fp)
        except Exception as e:
            problems.append("{}: JSON parse error — {}".format(name, e))
            continue
        if not isinstance(data, list):
            problems.append("{}: top-level value must be a JSON array".format(name))
            continue
        file_ok = 0
        for raw in data:
            q = normalize_question(raw, problems)
            if q is not None:
                all_q.append(q)
                file_ok += 1
        print("  {} -> {} questions loaded".format(name, file_ok))

    # --- verify ---
    verify_bank(all_q, problems)

    # --- report ---
    print("[build_quiz] Statistics:")
    print_statistics(all_q)

    if problems:
        print("[build_quiz] Problems ({} total):".format(len(problems)))
        for p in problems:
            print("  !! {}".format(p))
    else:
        print("[build_quiz] No problems found.")

    if not all_q:
        print("[ERROR] No valid questions loaded. Aborting.", file=sys.stderr)
        sys.exit(1)

    # --- load template ---
    try:
        html = io.open(args.template, encoding="utf-8").read()
    except FileNotFoundError:
        print("[ERROR] Template not found: {}".format(args.template), file=sys.stderr)
        sys.exit(1)

    if args.placeholder not in html:
        print(
            "[ERROR] Placeholder {!r} not found in template {}.".format(
                args.placeholder, args.template
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    # --- inject ---
    bank_json = json.dumps(all_q, ensure_ascii=False, separators=(",", ":"))
    html = html.replace(args.placeholder, bank_json, 1)  # replace exactly once

    # --- write ---
    out_dir = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(out_dir, exist_ok=True)
    io.open(args.out, "w", encoding="utf-8").write(html)
    size = os.path.getsize(args.out)
    print("[build_quiz] Written: {} ({:,} bytes)".format(args.out, size))


if __name__ == "__main__":
    main()
