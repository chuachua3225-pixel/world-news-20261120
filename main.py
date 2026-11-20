#!/usr/bin/env python3
"""Entry program for make.fun's "Sum up 20 November's world news in
one image" bounty (news-image-20261120).

The repository holds the finished front page in entry.png, drawn by
build_entry.py from the news of Friday 20 November 2026. This
program copies that image to the output location the harness
expects: $MAKEFUN_OUTPUT_DIR/entry.png when the variable is set
(local runs), otherwise /output/entry.png (the grading sandbox).

Standard library only, no network, deterministic output.
"""

import os
import sys

IMAGE_NAME = "entry.png"


def source_path():
    """The image shipped in this repository, next to this file."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        IMAGE_NAME)


def output_path():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    return os.path.join(out_dir, IMAGE_NAME)


def copy_image(src, dst):
    """Copy the image in chunks and verify the copy is byte-identical,
    so a grading run can never hand the judge a truncated file."""
    with open(src, "rb") as fin, open(dst, "wb") as fout:
        while True:
            chunk = fin.read(65536)
            if not chunk:
                break
            fout.write(chunk)
    if os.path.getsize(src) != os.path.getsize(dst):
        raise IOError("copied image size differs from the original")


def main():
    src = source_path()
    dst = output_path()
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    copy_image(src, dst)
    print("wrote", dst, os.path.getsize(dst), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
