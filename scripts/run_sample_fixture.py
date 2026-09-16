#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the sample bank into both quiz templates, then verify the outputs.

Writes into a temporary directory. Does not overwrite
examples/sample-bank/sample-quiz.html.

Usage (from repo root):
    python scripts/run_sample_fixture.py
"""

from __future__ import print_function

import os
import subprocess
import sys
import tempfile


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def run(cmd, cwd):
    print("+", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=cwd)
    if proc.returncode != 0:
        print("[FAIL] command exited {}".format(proc.returncode), file=sys.stderr)
        sys.exit(proc.returncode)


def main():
    root = repo_root()
    py = sys.executable
    banks = os.path.join(root, "examples", "sample-bank")
    build = os.path.join(root, "scripts", "build_quiz.py")
    verify = os.path.join(root, "scripts", "verify_html.py")

    templates = [
        ("quiz-material3.html", "sample-material3.html"),
        ("quiz-metro.html", "sample-metro.html"),
    ]

    with tempfile.TemporaryDirectory(prefix="esb-fixture-") as tmp:
        print("[fixture] writing outputs to", tmp, flush=True)
        outputs = []
        for tmpl_name, out_name in templates:
            tmpl = os.path.join(root, "assets", "templates", tmpl_name)
            out = os.path.join(tmp, out_name)
            run(
                [
                    py,
                    build,
                    "--banks",
                    banks,
                    "--template",
                    tmpl,
                    "--out",
                    out,
                ],
                cwd=root,
            )
            outputs.append(out)

        print("[fixture] verifying generated HTML (not raw templates)")
        for out in outputs:
            run([py, verify, out], cwd=root)

    print("[fixture] PASS — both quiz templates built and verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
