#!/usr/bin/env python3
import re
import sys
import os
import tempfile
import shutil

def add_spaces_between_chinese_english_digits(text: str) -> str:
    # 中文後面接英文或數字 → 加空格
    text = re.sub(r'(?<=[\u4e00-\u9fa5])(?=[A-Za-z0-9])', ' ', text)
    # 英文或數字後面接中文 → 加空格
    text = re.sub(r'(?<=[A-Za-z0-9])(?=[\u4e00-\u9fa5])', ' ', text)
    return text

def process_srt_file(input_path: str):
    # 建立暫存檔，處理後再覆蓋原檔，確保安全
    with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8') as tmp_file:
        with open(input_path, 'r', encoding='utf-8') as infile:
            for line in infile:
                if re.match(r'^\d+$', line.strip()) or '-->' in line or not line.strip():
                    tmp_file.write(line)
                    continue
                new_line = add_spaces_between_chinese_english_digits(line.rstrip())
                tmp_file.write(new_line + '\n')

    shutil.move(tmp_file.name, input_path)
    print(f"✅ 已修正完成：{input_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python add_spaces_srt.py <字幕檔.srt>")
        sys.exit(1)
    process_srt_file(sys.argv[1])
