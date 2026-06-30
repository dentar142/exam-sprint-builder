"""
extract_docx_images.py — extract embedded images from a .docx file.

Usage:
    python extract_docx_images.py <file.docx> <out_dir>

A .docx file is a ZIP archive.  Embedded images live under the internal path
``word/media/``.  This script opens the ZIP, finds every entry whose name starts
with ``word/media/``, and writes it to <out_dir> using only the basename.

PITFALL — directory entries in the ZIP
---------------------------------------
``zipfile.ZipFile.namelist()`` includes the *directory entry* ``word/media/``
itself, not just the files inside it.  That entry has an empty basename, so a
naive ``os.path.basename(name)`` call returns ``""`` and
``open("", "wb")`` raises FileNotFoundError (or silently creates a junk file,
depending on the OS).  The guard::

    if name.startswith("word/media/") and not name.endswith("/"):

skips directory entries entirely — this is the critical bug we hit during the
real extraction session.
"""

import os
import sys
import zipfile


def extract_docx_images(docx_path: str, out_dir: str) -> list[str]:
    """Extract all images from *docx_path* into *out_dir*.

    Returns a list of absolute paths of the extracted files.

    Parameters
    ----------
    docx_path:
        Path to the ``.docx`` file.
    out_dir:
        Directory to write images into.  Created if it does not exist.

    Raises
    ------
    FileNotFoundError
        If *docx_path* does not exist.
    zipfile.BadZipFile
        If *docx_path* is not a valid ZIP / DOCX file.
    """
    if not os.path.isfile(docx_path):
        raise FileNotFoundError(f"Input file not found: {docx_path}")

    os.makedirs(out_dir, exist_ok=True)

    extracted = []

    with zipfile.ZipFile(docx_path, "r") as zf:
        for name in zf.namelist():
            # Skip directory entries — their basename is empty and they carry
            # no image data.  This guard is the fix for the pitfall described
            # in the module docstring.
            if not name.startswith("word/media/") or name.endswith("/"):
                continue

            basename = os.path.basename(name)
            if not basename:
                # Defensive: skip anything else that resolves to an empty name.
                continue

            dest = os.path.join(out_dir, basename)
            with zf.open(name) as src, open(dest, "wb") as dst:
                dst.write(src.read())

            extracted.append(os.path.abspath(dest))

    return extracted


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python extract_docx_images.py <file.docx> <out_dir>")
        sys.exit(1)

    docx_path = sys.argv[1]
    out_dir = sys.argv[2]

    try:
        files = extract_docx_images(docx_path, out_dir)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except zipfile.BadZipFile:
        print(f"Error: '{docx_path}' is not a valid .docx (ZIP) file.", file=sys.stderr)
        sys.exit(1)

    print(f"Extracted {len(files)} image(s) to '{out_dir}':")
    for path in files:
        print(f"  {path}")


if __name__ == "__main__":
    main()
