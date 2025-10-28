#!/usr/bin/env python3
import re
import sys
from pathlib import Path

def clean_subtitle_numbers(input_path):
    input_path = Path(input_path)

    if not input_path.exists():
        print(f"❌ 找不到檔案: {input_path}")
        return

    with input_path.open("r", encoding="utf-8") as f:
        content = f.read()

    # 1️⃣ 移除字幕行開頭的「數字+點+空白」
    cleaned = re.sub(r'(?m)^\d+\.\s*', '', content)

    # 2️⃣ 移除每行結尾的全形或半形標點（。，）
    cleaned = re.sub(r'(?m)[，。]+$', '', cleaned)

    with input_path.open("w", encoding="utf-8") as f:
        f.write(cleaned)

    print(f"✅ 已清除字幕編號並覆蓋原檔：{input_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python clean_subtitle_numbers.py <檔案路徑>")
        sys.exit(1)

    clean_subtitle_numbers(sys.argv[1])
