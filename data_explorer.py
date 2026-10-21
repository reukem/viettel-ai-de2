import os
import sys

def explore_data():
    input_dir = "input"
    file_path = os.path.join(input_dir, "1.txt")
    
    # Kiểm tra xem file có tồn tại không
    if not os.path.exists(file_path):
        print(f"❌ KHÔNG TÌM THẤY DỮ LIỆU: {os.path.abspath(file_path)}")
        print("Aki-kun, cậu đã giải nén 100 file .txt vào thư mục này chưa?")
        sys.exit(1)
        
    print(f"🔍 Đang phân tích file: {os.path.abspath(file_path)}...\n")
    
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
        
    char_count = len(text)
    word_count = len(text.split())
    
    print("=" * 50)
    print("📊 BÁO CÁO THỐNG KÊ DỮ LIỆU (1.txt)")
    print("=" * 50)
    print(f"- Tổng số ký tự : {char_count:,}")
    print(f"- Tổng số từ    : {word_count:,}")
    print("=" * 50 + "\n")
    
    print("👁️‍🗨️ [1000 KÝ TỰ ĐẦU TIÊN]\n" + "-" * 50)
    print(text[:1000])
    print("-" * 50 + "\n")
    
    print("... [NỘI DUNG SIÊU DÀI ĐÃ BỊ ẨN BỞI ANTIGRAVITY IDE] ...\n")
    
    print("👁️‍🗨️ [500 KÝ TỰ CUỐI CÙNG]\n" + "-" * 50)
    if char_count > 500:
        print(text[-500:])
    else:
        print(text)
    print("-" * 50)

if __name__ == "__main__":
    explore_data()
