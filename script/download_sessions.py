# 在 iosdc2025translate/script/ 資料夾中執行：
# python3 download_sessions.py
# 影片就會自動下載到與 session.txt 同層的各個對應資料夾中。

# 範例檔案結構
# iosdc2025translate/
# ├── 「iPhoneのマイナンバーカード」のすべて/
# │   └── iOSDC Japan 2025_「iPhoneのマイナンバーカード」のすべて - Daiki Matsudate.mp4
# ├── ハイパフォーマンスなGIFアニメ再生を実現する工夫/
# ├── 5000萬ダウンロードを超える漫畫サービスを支えるログ基盤の設計開発の全て/
# ├── session.txt
# └── script/
#     └── download_sessions.py

#!/usr/bin/env python3
import subprocess
import os
import sys
import shutil

# === 檢查環境 ===
current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)
session_file = os.path.join(parent_dir, "session.txt")

# 檢查是否在 script 資料夾
if os.path.basename(current_dir) != "script":
    print("⚠️ 請在 'script' 資料夾內執行此腳本。")
    print(f"目前位置：{current_dir}")
    sys.exit(1)

# 檢查上一層是否有 session.txt
if not os.path.exists(session_file):
    print("❌ 找不到 session.txt，請確認它存在於上一層。")
    print(f"預期位置：{session_file}")
    sys.exit(1)

# 檢查是否安裝 yt-dlp
if shutil.which("yt-dlp") is None:
    print("❌ 找不到 yt-dlp，請先安裝後再執行。")
    print("\n安裝方式：")
    print("macOS / Linux:")
    print("  brew install yt-dlp    或    pip install yt-dlp")
    print("\nWindows:")
    print("  pip install yt-dlp")
    sys.exit(1)

print("✅ 檢查通過，開始下載...\n")

# === 讀取 session.txt ===
with open(session_file, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

# === 每兩行一組：資料夾名稱 + URL ===
for i in range(0, len(lines), 2):
    folder_name = lines[i]
    url = lines[i + 1] if i + 1 < len(lines) else None

    if not url or not url.startswith("http"):
        print(f"⚠️ 跳過：{folder_name}（URL 無效）")
        continue

    # 對應資料夾（在上一層）
    folder_path = os.path.join(parent_dir, folder_name)
    if not os.path.isdir(folder_path):
        print(f"📁 建立資料夾：{folder_name}")
        os.makedirs(folder_path, exist_ok=True)

    # 安全檔名
    safe_name = "".join(c for c in folder_name if c not in r'\/:*?"<>|').strip()
    output_mp4 = os.path.join(folder_path, f"{safe_name}.mp4")

    # 若已存在，先刪除舊檔
    if os.path.exists(output_mp4):
        print(f"🗑️ 刪除舊檔：{safe_name}.mp4")
        os.remove(output_mp4)

    # yt-dlp 輸出設定
    output_template = os.path.join(folder_path, f"{safe_name}.%(ext)s")

    print(f"🎬 下載：{folder_name}")
    subprocess.run([
        "yt-dlp",
        "-f", "bestvideo+bestaudio/best",
        "--merge-output-format", "mp4",
        "-o", output_template,
        "--no-continue",      # 不繼續未完成下載
        "--no-part",          # 不保留暫存片段
        "--no-warnings",  
        url
    ], check=False)

print("\n✅ 全部影片下載完成")




