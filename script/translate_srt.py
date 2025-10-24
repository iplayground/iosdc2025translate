#!/usr/bin/env python3
import sys
import os
import subprocess

# === 自動安裝缺少的套件 ===
def ensure_package(package_name):
    try:
        __import__(package_name)
    except ImportError:
        print(f"📦 偵測到未安裝套件 '{package_name}'，正在自動安裝中...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                package_name, "--break-system-packages"
            ])
            print(f"✅ 已成功安裝 {package_name}")
        except subprocess.CalledProcessError as e:
            print(f"❌ 安裝 {package_name} 失敗：{e}")
            sys.exit(1)

# 檢查必要套件
ensure_package("srt")
ensure_package("openai")
ensure_package("python-dotenv")

import srt
from openai import OpenAI
from dotenv import load_dotenv

# === 載入 .env ===
load_dotenv()

# === 檢查參數 ===
if len(sys.argv) < 2:
    print("用法：python translate_srt.py <input.srt>")
    sys.exit(1)

input_path = sys.argv[1]
if not os.path.exists(input_path):
    print(f"找不到檔案: {input_path}")
    sys.exit(1)

# === 自動設定輸出路徑 ===
base, ext = os.path.splitext(input_path)
output_path = f"{base}.zh.srt"

# === 初始化 OpenAI ===
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ 找不到 OPENAI_API_KEY，請在 .env 檔中設定或 export 環境變數。")
    sys.exit(1)
client = OpenAI(api_key=api_key)

# === 讀取字幕 ===
with open(input_path, "r", encoding="utf-8") as f:
    subs = list(srt.parse(f.read()))

# === 批次翻譯設定 ===
batch_size = 100

for start in range(0, len(subs), batch_size):
    end = min(start + batch_size, len(subs))
    subs_batch = subs[start:end]
    print(f"正在翻譯第 {start+1}～{end} 行...")

    if all(not s.content.strip() for s in subs_batch):
        continue

    batch_text = "\n\n".join(
        [f"{i+1}. {sub.content.strip()}" for i, sub in enumerate(subs_batch)]
    )

    prompt = f"""你是一個專業的日中字幕翻譯者。

以下是一段日本iOS開發研討會的逐字稿字幕（SRT格式）。
請將其中的日文台詞翻譯成自然、流暢的繁體中文。

【重要規則】
- 保留每一行的編號與時間軸格式（例如 “1”, “00:00:00,000 --> 00:00:05,000”）。
- 只翻譯台詞內容，不要修改或刪除任何時間碼。
- 不要新增或合併行數。
- 不要加入任何說明、括號、標註或空行。
- 技術用語（例如 Swift, UIKit, API, UIView, カスタムUI, Xcode, Apple）請保留原文。
- 若有日語語助詞或語氣詞（例如「ですね」「かな」「っていう」），請自然轉化為中文語氣。
- 請確保中文句子自然且口語化，但不失專業感。
- 僅輸出完整的翻譯後 SRT 內容，不要多餘文字。

範例：
原文：
1
00:00:00,000 --> 00:00:03,000
カスタムUIを作るのは大変です。

輸出：
1
00:00:00,000 --> 00:00:03,000
製作自訂UI是件很不容易的事。

以下是要翻譯的內容：
"""

    try:
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[{"role": "user", "content": prompt + "\n\n" + batch_text}],
        )
        translated_text = response.choices[0].message.content.strip()
        translated_lines = [
            line.strip() for line in translated_text.splitlines() if line.strip()
        ]
        for sub, line in zip(subs_batch, translated_lines):
            sub.content = line
    except Exception as e:
        print(f"⚠️ 第 {start+1}～{end} 行翻譯失敗：{e}")
        continue

# === 寫出結果 ===
with open(output_path, "w", encoding="utf-8") as f:
    f.write(srt.compose(subs))

print(f"\n✅ 翻譯完成！輸出檔案：{output_path}")
