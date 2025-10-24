import re
import datetime
import sys
import os
# --- 使用說明 ---
# 在終端機中執行此程式，並在後面加上檔名、開始的行號、要調整的秒數。
# 範例:
# python shift_srt.py abc.srt 810 0.5    (將 abc.srt 從第 810 條字幕開始，全部增加 0.5 秒)
# python shift_srt.py sub.srt 50 -1.2   (將 sub.srt 從第 50 條字幕開始，全部減少 1.2 秒)

def parse_srt_time(time_str: str) -> datetime.timedelta:
    """
    將 SRT 時間格式字串 (HH:MM:SS,ms) 轉換為 timedelta 物件。
    """
    try:
        parts = time_str.replace(',', ':').split(':')
        return datetime.timedelta(
            hours=int(parts[0]),
            minutes=int(parts[1]),
            seconds=int(parts[2]),
            milliseconds=int(parts[3])
        )
    except (ValueError, IndexError):
        return None

def format_timedelta_to_srt(td: datetime.timedelta) -> str:
    """
    將 timedelta 物件格式化回 SRT 時間字串 (HH:MM:SS,ms)。
    時間將不會小於 0。
    """
    total_seconds = td.total_seconds()
    if total_seconds < 0:
        total_seconds = 0
    
    whole_seconds = int(total_seconds)
    hours, remainder = divmod(whole_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((total_seconds - whole_seconds) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def shift_srt_from_line(filename: str, start_index: int, shift_seconds: float):
    """
    讀取一個 SRT 檔案，從指定的字幕編號開始調整時間軸，並直接覆蓋原始檔案。

    :param filename: 要處理的檔案名稱。
    :param start_index: 開始調整的字幕編號。
    :param shift_seconds: 要調整的秒數（正數為增加，負數為減少）。
    """
    time_pattern = re.compile(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})')
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_lines = []
        shift_delta = datetime.timedelta(seconds=shift_seconds)
        
        # 標記是否已到達需要開始調整的位置
        shifting_started = False
        current_index = 0

        for line in lines:
            # 檢查是否為字幕編號行
            if line.strip().isdigit():
                current_index = int(line.strip())
                if current_index >= start_index:
                    shifting_started = True
            
            # 如果已經開始調整，並且是時間軸行，就進行修改
            if shifting_started:
                match = time_pattern.match(line.strip())
                if match:
                    start_time_str, end_time_str = match.groups()
                    start_td = parse_srt_time(start_time_str)
                    end_td = parse_srt_time(end_time_str)
                    
                    if start_td is not None and end_td is not None:
                        new_start_td = start_td + shift_delta
                        new_end_td = end_td + shift_delta
                        
                        new_start_str = format_timedelta_to_srt(new_start_td)
                        new_end_str = format_timedelta_to_srt(new_end_td)
                        
                        new_line = f"{new_start_str} --> {new_end_str}\n"
                        new_lines.append(new_line)
                        continue # 處理完畢，跳到下一行
                
            # 如果不需調整或不是時間軸行，直接加入
            new_lines.append(line)

        # 寫回原始檔案，實現覆蓋
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
                    
        print(f"處理完成！檔案 '{filename}' 已從第 {start_index} 行開始更新。")

    except FileNotFoundError:
        print(f"錯誤：找不到檔案 '{filename}'")
    except Exception as e:
        print(f"發生了一個未知的錯誤：{e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("用法: python shift_srt.py <檔名> <開始的字幕編號> <要調整的秒數>")
        print("範例: python shift_srt.py abc.srt 810 0.5")
        sys.exit(1)

    try:
        input_file = sys.argv[1]
        start_line_number = int(sys.argv[2])
        shift_value = float(sys.argv[3])
        
        shift_srt_from_line(input_file, start_line_number, shift_value)

    except ValueError:
        print(f"錯誤：字幕編號和秒數必須是有效的數字。")
    except Exception as e:
        print(f"執行時發生錯誤: {e}")