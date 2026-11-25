#!/usr/bin/env python3
"""news-image-20261125 entry point (standard library only).

Copies the pre-built entry.png (drawn by draw.py) to $MAKEFUN_OUTPUT_DIR.
Runs identically on every run: same input bytes, same output bytes.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(SRC, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
