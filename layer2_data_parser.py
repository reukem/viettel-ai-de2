import pandas as pd
import json
import os

def parse_csv(filepath):
    print(f"📄 Đang xử lý file CSV: {filepath}")
    df = pd.read_csv(filepath)
    
    # Auto-detect columns
    actual_code_col = df.columns[0]
    actual_name_col = df.columns[1]
    
    for col in df.columns:
        if 'mã' in col.lower() or 'code' in col.lower() or 'icd' in col.lower():
            actual_code_col = col
        if 'tên' in col.lower() or 'name' in col.lower() or 'bệnh' in col.lower():
            actual_name_col = col
            
    print(f"   -> Đã bóc tách Cột Mã: [{actual_code_col}], Cột Tên: [{actual_name_col}]")
    
    dictionary = {}
    for _, row in df.iterrows():
        code = str(row[actual_code_col]).strip()
        name = str(row[actual_name_col]).strip()
        if code and name and code.lower() != 'nan' and name.lower() != 'nan':
            dictionary[code] = name
            
    return dictionary

def parse_excel(filepath):
    print(f"📊 Đang xử lý file Excel: {filepath}")
    df = pd.read_excel(filepath)
    
    actual_code_col = df.columns[0]
    actual_name_col = df.columns[1]
    
    for col in df.columns:
        if 'mã' in col.lower() or 'code' in col.lower() or 'icd' in col.lower():
            actual_code_col = col
        if 'tên' in col.lower() or 'name' in col.lower() or 'bệnh' in col.lower():
            actual_name_col = col
            
    print(f"   -> Đã bóc tách Cột Mã: [{actual_code_col}], Cột Tên: [{actual_name_col}]")
    
    dictionary = {}
    for _, row in df.iterrows():
        code = str(row[actual_code_col]).strip()
        name = str(row[actual_name_col]).strip()
        if code and name and code.lower() != 'nan' and name.lower() != 'nan':
            dictionary[code] = name
            
    return dictionary

def parse_pdf(filepath):
    print(f"📕 Đang xử lý file PDF: {filepath}")
    try:
        import pdfplumber
    except ImportError:
        print("❌ Thiếu thư viện pdfplumber! Hãy chạy: pip install pdfplumber")
        return {}
        
    dictionary = {}
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                for row in table:
                    if len(row) >= 2:
                        code = str(row[0]).strip()
                        name = str(row[1]).strip()
                        if code and name and code.lower() != 'none' and name.lower() != 'none':
                            dictionary[code] = name
    return dictionary

def parse_data(filepath, output_json="dictionary.json"):
    ext = os.path.splitext(filepath)[1].lower()
    dictionary = {}
    
    try:
        if ext == '.csv':
            dictionary = parse_csv(filepath)
        elif ext in ['.xls', '.xlsx']:
            dictionary = parse_excel(filepath)
        elif ext == '.pdf':
            dictionary = parse_pdf(filepath)
        elif ext == '.json':
            print("🟢 File đã là JSON chuẩn, không cần convert!")
            return True
        else:
            print(f"❌ Định dạng {ext} chưa được hỗ trợ!")
            return False
            
        print(f"✅ Đã trích xuất thành công {len(dictionary)} bản ghi!")
        
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(dictionary, f, ensure_ascii=False, indent=4)
            
        print(f"💾 Đã lưu toàn bộ dữ liệu vào: {output_json} (Sẵn sàng Ingest vào ChromaDB!)")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi bóc tách dữ liệu: {e}")
        return False

if __name__ == "__main__":
    import sys
    print("="*50)
    print("🛠️ LÒ LUYỆN DATA (DATA PARSER) - ĐÃ KHỞI ĐỘNG 🛠️")
    print("="*50)
    if len(sys.argv) > 1:
        parse_data(sys.argv[1])
    else:
        print("💡 Cú pháp: python layer2_data_parser.py <đường_dẫn_file_từ_điển>")
