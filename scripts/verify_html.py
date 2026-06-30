#!/usr/bin/env python3
"""
verify_html.py — Exam Sprint Builder HTML verifier (stdlib only).

Usage:
    python verify_html.py <file.html>

Checks performed:
  (a) No external URLs (http/https or known CDN hostnames)
  (b) No build-placeholder residue (__BANK__/__CONTENT__/__SECTIONS__, /*__…,
      <!--__…, INSERT_HERE, lorem ipsum, PUA chars U+E000/U+E001). Deliberately
      does NOT flag the JS keyword `undefined`, the HTML `placeholder=` attribute,
      or TODO/FIXME — those legitimately appear in real quiz content.
  (c) Required markers present (data-theme, esb-theme, a theme toggle)
  (d) Structural counts (<table>, <pre>, callout blocks, <script> blocks)
  (e) File size

Note: JS-syntax checking is intentionally NOT done here because Python cannot
parse JavaScript. Run JS syntax checks separately using Node:
    node -e "new (require('vm').Script)(require('fs').readFileSync('file.html','utf8'))"
Or extract <script> blocks and run: node --check each_block.js
"""

import re
import sys
import os


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _label(tag: str, width: int = 6) -> str:
    """Format a PASS/FAIL label, padded for alignment."""
    return tag.ljust(width)


def check(name: str, passed: bool, detail: str = "") -> tuple[bool, str]:
    """Return a (passed, line) tuple and print immediately."""
    tag = "PASS" if passed else "FAIL"
    line = f"[{_label(tag)}] {name}"
    if detail:
        line += f"  — {detail}"
    print(line)
    return passed, line


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def check_no_external_urls(content: str) -> bool:
    """(a) Fail if any http(s):// URL or CDN hostname is present."""
    # Direct http/https URLs
    http_matches = re.findall(r'https?://', content)
    # CDN hostnames (without scheme too, e.g. src="//cdn.example.com/...")
    cdn_pattern = re.compile(
        r'(cdn\.|unpkg\.|jsdelivr\.|googleapis\.|cloudflare\.|gstatic\.|fastly\.)',
        re.IGNORECASE
    )
    cdn_matches = cdn_pattern.findall(content)

    all_hits = http_matches + cdn_matches
    passed, _ = check(
        "No external URLs / CDN references",
        len(all_hits) == 0,
        f"{len(all_hits)} hit(s) found" if all_hits else "clean"
    )

    if all_hits:
        # Print up to 5 sample matches with context
        for pat in [r'https?://\S{0,80}', r'(?:cdn|unpkg|jsdelivr|googleapis|cloudflare|gstatic|fastly)\.\S{0,60}']:
            for m in re.finditer(pat, content, re.IGNORECASE):
                line_no = content[:m.start()].count('\n') + 1
                print(f"         line {line_no}: {m.group()[:100]!r}")
                break  # one sample per pattern

    return passed


def check_no_placeholder_residue(content: str) -> bool:
    """(b) Fail if placeholder tokens or encoding artifacts remain."""
    patterns = {
        "__BANK__ placeholder": r'__BANK__',
        "__CONTENT__ placeholder": r'__CONTENT__',
        "__SECTIONS__ placeholder": r'__SECTIONS__',
        "/*__…*/ build comment": r'/\*__\w',
        "<!--__…--> build comment": r'<!--__\w',
        "PUA char U+E000": r'',
        "PUA char U+E001": r'',
        "INSERT_HERE marker": r'INSERT_HERE',
        "lorem ipsum": r'lorem\s+ipsum',
    }
    hits = {}
    for name, pat in patterns.items():
        matches = re.findall(pat, content, re.IGNORECASE)
        if matches:
            hits[name] = len(matches)

    passed, _ = check(
        "No placeholder residue",
        len(hits) == 0,
        "clean" if not hits else ", ".join(f"{k}: {v}" for k, v in hits.items())
    )
    return passed


def check_required_markers(content: str) -> tuple[bool, dict]:
    """(c) Verify data-theme attribute, esb-theme localStorage key, and a theme toggle element."""
    markers = {
        "data-theme attribute": r'data-theme\s*=',
        "esb-theme localStorage key": r'esb-theme',
        "theme toggle element/function": r'(applyTheme|toggleTheme|theme.?toggle|setItem\(\s*["\']esb-theme|id=["\'](?:themeBtn|tbtn|theme-toggle|theme-btn)["\'])',
    }
    results = {}
    all_pass = True
    for label, pat in markers.items():
        found = bool(re.search(pat, content, re.IGNORECASE))
        results[label] = found
        if not found:
            all_pass = False

    detail = "; ".join(
        f"{k}: {'yes' if v else 'MISSING'}" for k, v in results.items()
    )
    check("Required theme markers present", all_pass, detail)
    return all_pass, results


def count_structural_elements(content: str) -> dict:
    """(d) Count tables, pre blocks, callouts, and script blocks; print report."""
    counts = {
        "<table> blocks": len(re.findall(r'<table[\s>]', content, re.IGNORECASE)),
        "<pre> blocks": len(re.findall(r'<pre[\s>]', content, re.IGNORECASE)),
        "callout blocks (.callout/.tip/.warn class)": len(
            re.findall(r'class=["\'][^"\']*(?:callout|tip|warn|note|danger)[^"\']*["\']', content, re.IGNORECASE)
        ),
        "<script> blocks (inline)": len(
            re.findall(r'<script(?![^>]*\bsrc\b)[^>]*>', content, re.IGNORECASE)
        ),
    }
    print("[INFO  ] Structural element counts:")
    for k, v in counts.items():
        print(f"           {k}: {v}")
    return counts


def check_file_size(path: str) -> bool:
    """(e) Report file size; warn if over 5 MB (may indicate accidental binary embed)."""
    size = os.path.getsize(path)
    size_kb = size / 1024
    size_mb = size_kb / 1024
    label = f"{size_kb:.1f} KB"
    if size_mb >= 1:
        label = f"{size_mb:.2f} MB"

    threshold_mb = 5.0
    passed = size_mb < threshold_mb
    check(
        "File size within limit (< 5 MB)",
        passed,
        f"{label} {'— OK' if passed else '— exceeds 5 MB warning threshold'}"
    )
    return passed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python verify_html.py <file.html>", file=sys.stderr)
        return 2

    path = sys.argv[1]

    if not os.path.isfile(path):
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2

    # Read as UTF-8; replace errors so PUA detection still works on malformed files
    with open(path, encoding="utf-8", errors="replace") as fh:
        content = fh.read()

    print(f"\nVerifying: {os.path.abspath(path)}")
    print("=" * 60)

    results = []

    # (a) External URLs
    results.append(check_no_external_urls(content))

    # (b) Placeholder residue
    results.append(check_no_placeholder_residue(content))

    # (c) Required markers
    markers_ok, _ = check_required_markers(content)
    results.append(markers_ok)

    # (d) Structural counts (informational; does not affect pass/fail)
    count_structural_elements(content)

    # (e) File size
    results.append(check_file_size(path))

    # JS note
    print(
        "\n[NOTE  ] JS syntax checking requires Node — run separately:\n"
        "         node -e \"const vm=require('vm'),fs=require('fs');\"\n"
        "                    \"const h=fs.readFileSync('file.html','utf8');\"\n"
        "                    \"const re=/<script(?![^>]*src)[^>]*>([\\\\s\\\\S]*?)<\\/script>/gi;\"\n"
        "                    \"let m,i=0; while((m=re.exec(h))){\"\n"
        "                    \"try{new vm.Script(m[1]);console.log('PASS block',++i);}\"\n"
        "                    \"catch(e){console.error('FAIL block',++i,e.message);process.exitCode=1;}}\""
    )

    # Verdict
    passed_count = sum(1 for r in results if r)
    total = len(results)
    overall = passed_count == total

    print("\n" + "=" * 28 + " VERDICT " + "=" * 23)
    verdict = "PASS" if overall else "FAIL"
    print(f"{verdict}  ({passed_count}/{total} checks passed)")
    print("=" * 60 + "\n")

    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
