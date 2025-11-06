#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
------------------------------------------------------------
Script: reindex_srt.py
Purpose:
    Automatically reindex all subtitle blocks in .srt files.
    It ensures that each subtitle block is numbered sequentially
    starting from 1 (e.g., 1, 2, 3, 4, ...).

Usage:
    1️⃣ Reindex a single .srt file:
        python scripts/reindex_srt.py "sessions/test.zh.srt"

    2️⃣ Reindex all .srt files recursively in a folder:
        python scripts/reindex_srt.py sessions/

    Notes:
        - This script **overwrites the original files** directly.
        - It does NOT create backup files (.bak).
        - Works on UTF-8 and UTF-8-BOM encoded .srt files.
------------------------------------------------------------
"""

import os
import re
import sys


def reindex_srt(file_path: str) -> bool:
    """
    Reindex a single SRT file.

    - Reads the file.
    - Splits it into subtitle blocks separated by blank lines.
    - Renumbers each block sequentially from 1.
    - Overwrites the original file directly.

    Args:
        file_path (str): Path to the .srt file.

    Returns:
        bool: True if success, False if any error occurs.
    """
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            content = f.read().strip()
    except Exception as e:
        print(f"❌ Unable to read file {file_path}: {e}")
        return False

    if not content:
        print(f"⚠️ Empty file: {file_path}")
        return False

    # Split blocks by blank lines
    blocks = re.split(r"\n\s*\n", content)
    new_blocks = []
    new_index = 1

    for block in blocks:
        # Skip empty segments
        lines = [line for line in block.splitlines() if line.strip()]
        if not lines:
            continue

        # Replace or insert block number
        if lines[0].strip().isdigit():
            lines[0] = str(new_index)
        else:
            lines.insert(0, str(new_index))

        new_blocks.append("\n".join(lines))
        new_index += 1

    # Join all blocks with blank lines between them
    new_content = "\n\n".join(new_blocks).strip() + "\n"

    try:
        # Overwrite the original file directly
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ Reindexed {file_path} ({new_index - 1} blocks)")
        return True
    except Exception as e:
        print(f"❌ Failed to write {file_path}: {e}")
        return False


def main():
    """
    Entry point of the script.
    Accepts either a file or a folder path.
    """
    base_path = sys.argv[1] if len(sys.argv) > 1 else "."
    total = 0

    # Case 1: Single file
    if os.path.isfile(base_path) and base_path.lower().endswith(".srt"):
        reindex_srt(base_path)
        sys.exit(0)

    # Case 2: Folder – recursively reindex all .srt files
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.lower().endswith(".srt"):
                path = os.path.join(root, file)
                if reindex_srt(path):
                    total += 1

    print(f"\n🎯 Completed. Total reindexed files: {total}")


if __name__ == "__main__":
    main()
