import os
import re
import sys
from datetime import timedelta

# Regex for SRT timestamp line
TIME_PATTERN = re.compile(
    r"^(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})$"
)

def parse_timestamp(h, m, s, ms):
    """Convert timestamp components to timedelta."""
    return timedelta(hours=int(h), minutes=int(m), seconds=int(s), milliseconds=int(ms))


def check_srt_format(file_path):
    """Validate .srt file structure and timing order."""
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            lines = [line.rstrip("\n") for line in f.readlines()]
    except Exception as e:
        return False, f"Cannot read file: {e}"

    if not lines:
        return False, "File is empty"

    # --- Split into subtitle blocks ---
    blocks, current_block, line_numbers = [], [], []
    for i, line in enumerate(lines, start=1):
        if line.strip() == "":
            if current_block:
                blocks.append((current_block, line_numbers))
                current_block, line_numbers = [], []
        else:
            current_block.append(line)
            line_numbers.append(i)
    if current_block:
        blocks.append((current_block, line_numbers))

    expected_index = 1
    prev_end_time = timedelta(0)
    prev_block_info = None  # (block_index, end_time, line_number)

    for block_index, (block_lines, block_line_nums) in enumerate(blocks, start=1):
        if len(block_lines) < 3:
            return False, f"Block {block_index}: too few lines (needs at least 3), starts at line {block_line_nums[0]}"

        # --- Check index ---
        idx_line = block_lines[0].strip()
        if not idx_line.isdigit():
            return False, f"Block {block_index}: line {block_line_nums[0]} should be a numeric index, found '{idx_line}'"
        index = int(idx_line)
        if index != expected_index:
            hint = ""
            if index > expected_index:
                hint = f" (possibly missing block {expected_index})"
            elif index < expected_index:
                hint = " (duplicate or misplaced index)"
            return False, f"Block {block_index}: line {block_line_nums[0]} index mismatch (expected {expected_index}, got {index}){hint}"
        expected_index += 1

        # --- Check timestamp line ---
        time_line = block_lines[1].strip()
        m = TIME_PATTERN.match(time_line)
        if not m:
            return False, (
                f"Block {block_index}: line {block_line_nums[1]} invalid timestamp format "
                f"(expected 'HH:MM:SS,mmm --> HH:MM:SS,mmm'), got '{time_line}'"
            )

        start = parse_timestamp(*m.groups()[:4])
        end = parse_timestamp(*m.groups()[4:])

        if end <= start:
            return False, f"Block {block_index}: line {block_line_nums[1]} end time is earlier than or equal to start time"

        # --- Check against previous block ---
        if prev_block_info:
            prev_idx, prev_end, prev_line = prev_block_info
            if start < prev_end:
                return False, (
                    f"Block {block_index}: line {block_line_nums[1]} start time overlaps "
                    f"with previous block {prev_idx} (previous end at line {prev_line})"
                )

        prev_block_info = (block_index, end, block_line_nums[1])

        # --- Check subtitle text presence ---
        if not any(l.strip() for l in block_lines[2:]):
            return False, f"Block {block_index}: missing subtitle text (starting at line {block_line_nums[2]})"

    return True, "OK"


def main():
    changed_files = os.getenv("CHANGED_FILES", "").splitlines()

    # Fallback for local runs: scan all .srt files
    if not changed_files:
        print("⚠️  No CHANGED_FILES detected — scanning all .srt files under current directory.")
        for root, _, files in os.walk("."):
            for file in files:
                if file.lower().endswith(".srt"):
                    changed_files.append(os.path.join(root, file))

    srt_files = [f for f in changed_files if f.lower().endswith(".srt")]
    if not srt_files:
        print("No .srt files found.")
        sys.exit(0)

    failed = []
    for path in srt_files:
        if not os.path.exists(path):
            continue
        ok, msg = check_srt_format(path)
        if ok:
            print(f"✅ {path}")
        else:
            print(f"❌ {path}: {msg}")
            failed.append(f"- `{path}`: {msg}")

    if failed:
        report = (
            "❌ **SRT Format Validation Failed**\n\n"
            + "\n".join(failed)
            + "\n\nPlease fix the issues above and push again to re-run the check."
        )
        with open("srt_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        sys.exit(1)
    else:
        print("\nAll SRT files passed validation ✅")


if __name__ == "__main__":
    main()
