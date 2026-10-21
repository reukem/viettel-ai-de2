import os
import json
import zipfile
from layer1_ner import hunt_censored_stars, exact_index_matcher, non_maximum_suppression
from layer2_rag_engine import MedicalKnowledgeBase
from layer3_assertions import mock_llm_assertion

def process_single_file(filepath, text, mkb):
    # 1. TẦNG 1 (NER)
    # Vì chưa có LLM xịn (chờ CUDA), ta dùng Mock NER để test pipeline
    mock_ner_output = [
        {"text": "Thiếu men G6PD", "type": "CHẨN_ĐOÁN"},
        {"text": "Sốt cao", "type": "TRIỆU_CHỨNG"},
        {"text": "suy hô hấp", "type": "CHẨN_ĐOÁN"}
    ]
    
    raw_preds = exact_index_matcher(text, mock_ner_output)
    raw_preds.extend(hunt_censored_stars(text))
    layer1_entities = non_maximum_suppression(raw_preds)
    
    # 2. TẦNG 3 (Assertions) & TẦNG 2 (RAG Mapping)
    for entity in layer1_entities:
        start_idx, end_idx = entity['position']
        ctx_start = max(0, start_idx - 50)
        ctx_end = min(len(text), end_idx + 50)
        context = text[ctx_start:ctx_end]
        
        # Tầng 3
        entity['assertions'] = mock_llm_assertion(entity['text'], context)
        
        # Tầng 2
        if entity['type'] in ['CHẨN_ĐOÁN', 'TRIỆU_CHỨNG']:
            candidates = mkb.search_candidates(entity['text'], "ICD-10", top_k=1)
            # search_candidates trả về list tuples (code, doc, dist)
            if candidates:
                entity['candidates'] = [candidates[0][0]]
            else:
                entity['candidates'] = []
        else:
            # Dummy cho RxNorm
            entity['candidates'] = []
            
    return layer1_entities

def main():
    print("="*50)
    print("🏭 KHỞI ĐỘNG BĂNG CHUYỀN SẢN XUẤT EXODIA 🏭")
    print("="*50)
    
    input_dir = "input"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Khởi tạo Tầng 2 (RAG)
    mkb = MedicalKnowledgeBase()
    if os.path.exists("dummy_icd10.json"):
        mkb.ingest_data("ICD-10", "dummy_icd10.json")
    
    # 2. Quét file
    files = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
    print(f"\n📦 Đang xử lý {len(files)} file bệnh án...")
    
    for i, filename in enumerate(files):
        file_path = os.path.join(input_dir, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            
        entities = process_single_file(file_path, text, mkb)
        
        out_filename = filename.replace(".txt", ".json")
        out_path = os.path.join(output_dir, out_filename)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(entities, f, ensure_ascii=False, indent=4)
            
        if (i + 1) % 10 == 0:
            print(f"   -> Đã xử lý xong {i + 1}/{len(files)} files...")
            
    # 3. Đóng gói
    print("\n🗜️ Đang nén file submission.zip...")
    zip_path = "submission.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, out_files in os.walk(output_dir):
            for file in out_files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, output_dir)
                zipf.write(file_path, arcname)
                
    print(f"✅ Đã hoàn tất! File {zip_path} đã sẵn sàng để nộp lên Viettel AI Portal.")
    print("="*50)

if __name__ == "__main__":
    main()
