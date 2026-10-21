import json
import re
from evaluator import evaluate
from layer1_ner import exact_index_matcher, hunt_censored_stars, non_maximum_suppression

# ---------------------------------------------------------
# 1. THIẾT KẾ PROMPT KHẮC NGHIỆT (CHO LLM THẬT SAU NÀY)
# ---------------------------------------------------------
def llm_assertion_prompting(entity_text, context_text, llm):
    """
    Prompt được thiết kế nghiêm ngặt để triệt tiêu bệnh ảo giác (hallucination).
    Bắt buộc LLM phải tuân thủ đúng 3 nhãn của Viettel AI, trả về JSON chuẩn.
    """
    prompt = f"""<|im_start|>system
Bạn là chuyên gia phân tích bệnh án. Nhiệm vụ: Xác định trạng thái của thực thể y tế "{entity_text}" dựa vào đoạn ngữ cảnh.
Chỉ trả về 1 danh sách JSON hợp lệ chứa các nhãn trạng thái. Tối đa 3 nhãn sau:
- "isNegated": Bị phủ định (không bị bệnh này).
- "isFamily": Bệnh của người nhà.
- "isHistorical": Tiền sử bệnh.
Nếu bệnh nhân HIỆN TẠI đang bị bệnh này (không phủ định, không của người nhà), TRẢ VỀ DANH SÁCH RỖNG [].
Tuyệt đối chỉ xuất chuỗi JSON (ví dụ: ["isNegated"] hoặc []). Không in markdown (```json).<|im_end|>
<|im_start|>user
Ngữ cảnh: "{context_text}"
Thực thể: "{entity_text}"<|im_end|>
<|im_start|>assistant
"""
    # Code gọi Llama CPP inference sẽ được đặt ở đây khi cài xong CUDA Toolkit
    pass

# ---------------------------------------------------------
# 2. CHẾ ĐỘ MOCK TEST (BYPASS CUDA BẰNG REGEX)
# ---------------------------------------------------------
def mock_llm_assertion(entity_text, context_text):
    """
    Giả lập Suy Luận Ngữ Cảnh bằng Regex đơn giản để bypass CUDA.
    Quét khu vực xung quanh thực thể để tìm từ khóa.
    """
    assertions = []
    context_lower = context_text.lower()
    
    # Tìm index của thực thể trong ngữ cảnh
    idx = context_lower.find(entity_text.lower())
    if idx != -1:
        # Lấy bán kính 40 ký tự phía trước thực thể
        prefix = context_lower[max(0, idx - 40):idx]
        
        # Bắt "isNegated"
        if re.search(r'\b(không|chưa|loại trừ)\b', prefix):
            assertions.append("isNegated")
            
        # Bắt "isHistorical"
        if re.search(r'\b(tiền sử|trước đây|đã từng|năm ngoái)\b', prefix):
            assertions.append("isHistorical")
            
        # Bắt "isFamily"
        if re.search(r'\b(bố|mẹ|anh|chị|em|gia đình|con)\b', prefix):
            assertions.append("isFamily")
            
    return list(set(assertions))

# ---------------------------------------------------------
# 3. HỢP THỂ EXODIA & CHẠY UNIT TEST
# ---------------------------------------------------------
def run_exodia_test():
    print("="*50)
    print("🔥 CHIẾN DỊCH HỢP THỂ EXODIA: TẦNG 1 + TẦNG 3")
    print("="*50)
    
    with open("input/1.txt", "r", encoding="utf-8") as f:
        text = f.read()
        
    # --- TẦNG 1: NER & ĐỊNH VỊ ---
    print("🛡️ [TẦNG 1] Khởi động NER và đếm Index...")
    mock_ner_output = [
        {"text": "Thiếu men G6PD", "type": "CHẨN_ĐOÁN"},
        {"text": "Sốt cao", "type": "TRIỆU_CHỨNG"}
    ]
    raw_preds = exact_index_matcher(text, mock_ner_output)
    raw_preds.extend(hunt_censored_stars(text))
    layer1_entities = non_maximum_suppression(raw_preds)
    print(f"📍 Tầng 1 đã định vị xong {len(layer1_entities)} thực thể.\n")
    
    # --- TẦNG 3: ASSERTIONS ---
    print("🧠 [TẦNG 3] Khởi động Não Bộ Suy Luận (Mock Regex)...")
    for entity in layer1_entities:
        start_idx = entity['position'][0]
        end_idx = entity['position'][1]
        
        # Cắt ngữ cảnh xung quanh thực thể (trước 50 char, sau 50 char)
        ctx_start = max(0, start_idx - 50)
        ctx_end = min(len(text), end_idx + 50)
        context = text[ctx_start:ctx_end]
        
        # Bắn vào Mock LLM
        assertions = mock_llm_assertion(entity['text'], context)
        entity['assertions'] = assertions
        
        # Gán candidates mặc định để Lò luyện đan không báo lỗi field
        if entity['type'] == 'CHẨN_ĐOÁN':
            entity['candidates'] = ["D55.0"]
            
        if assertions:
            print(f"   -> 💡 Suy luận được [{', '.join(assertions)}] cho '{entity['text']}' tại {entity['position']}")
            
    # Tự động tạo Dummy Truth hoàn hảo làm barem chấm điểm
    with open("dummy_truth_1.json", "w", encoding="utf-8") as f:
        json.dump(layer1_entities, f, ensure_ascii=False, indent=4)
        
    # --- CHẤM ĐIỂM ---
    print("\n🔥 ĐƯA VÀO LÒ LUYỆN ĐAN (EVALUATOR) 🔥")
    with open("dummy_truth_1.json", "r", encoding="utf-8") as f:
        ground_truth = json.load(f)
        
    # [HACK] Sửa sai thử 1 cái trong prediction để kiểm tra logic trừ điểm
    if len(layer1_entities) > 0:
        print(f"⚠️ [MOCK ERROR] Cố tình làm sai Assertion của thực thể đầu tiên để test luật trừ điểm!")
        layer1_entities[0]['assertions'] = ["isNegated"] if "isHistorical" not in layer1_entities[0].get('assertions', []) else []

    results = evaluate([ground_truth], [layer1_entities])
    
    print("\n📊 BẢNG ĐIỂM TỔNG KẾT EXODIA:")
    print(f"   - Word Error Rate (Text Score) : {results['text_score']*100:.2f} %")
    print(f"   - Assertions Score             : {results['assertions_score']*100:.2f} %")
    print(f"   - Candidates Score             : {results['candidates_score']*100:.2f} %")
    print(f"   - FINAL SCORE                  : {results['final_score']*100:.2f} %")
    
    if results['assertions_score'] < 1.0:
        print("\n🏆 TUYỆT VỜI! HỆ THỐNG ĐÃ TRỪ ĐIỂM ASSERTION CHÍNH XÁC KHI BỊ NHIỄU! CỖ MÁY ĐÃ HOÀN HẢO!")
    else:
        print("\n❌ LỖI: Điểm Assertion vẫn 100% dù có kết quả sai!")

if __name__ == "__main__":
    run_exodia_test()
