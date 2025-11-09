import re
from datetime import timedelta

def parse_time(time_str):
    h, m, s_ms = time_str.split(':')
    s, ms = s_ms.split(',')
    return timedelta(hours=int(h), minutes=int(m), seconds=int(s), milliseconds=int(ms))

def format_time(td):
    total_seconds = int(td.total_seconds())
    ms = int(td.microseconds / 1000)
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def fix_overlaps(srt_path):
    with open(srt_path, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()

    entries = []
    entry = []
    for line in lines:
        if line.strip() == '':
            if entry:
                entries.append(entry)
                entry = []
        else:
            entry.append(line)
    if entry:
        entries.append(entry)

    changes = []

    for i in range(1, len(entries)):
        prev_time = entries[i - 1][1]
        curr_time = entries[i][1]

        prev_start, prev_end = re.findall(r'\d{2}:\d{2}:\d{2},\d{3}', prev_time)
        curr_start, curr_end = re.findall(r'\d{2}:\d{2}:\d{2},\d{3}', curr_time)

        prev_end_td = parse_time(prev_end)
        curr_start_td = parse_time(curr_start)

        if curr_start_td <= prev_end_td:
            new_start = prev_end_td + timedelta(milliseconds=1)
            changes.append({
                "index": entries[i][0],
                "old": curr_time,
                "new": f"{format_time(new_start)} --> {curr_end}"
            })
            entries[i][1] = f"{format_time(new_start)} --> {curr_end}"

    with open(srt_path, 'w', encoding='utf-8') as f:
        for e in entries:
            f.write("\n".join(e) + "\n\n")

    if changes:
        print("🔧 修正以下重疊區段：")
        for c in changes:
            print(f"\n字幕 #{c['index']}")
            print(f"  原: {c['old']}")
            print(f"  改: {c['new']}")
    else:
        print("✅ 沒有發現重疊時間。")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("用法: python fix_srt_overlap.py <字幕檔.srt>")
    else:
        fix_overlaps(sys.argv[1])
        print(f"\n✅ 已修正重疊時間並覆蓋檔案: {sys.argv[1]}")
