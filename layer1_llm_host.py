import os
import json
from huggingface_hub import hf_hub_download
from llama_cpp import Llama
from layer1_ner import exact_index_matcher, hunt_censored_stars

def download_model():
    print("⏳ Đang kéo quái vật Qwen-2.5-7B-Instruct (GGUF 4-bit) về căn cứ...")
    model_path = hf_hub_download(
        repo_id="bartowski/Qwen2.5-7B-Instruct-GGUF",
        filename="Qwen2.5-7B-Instruct-Q4_K_M.gguf",
        local_dir="models"
    )
    print(f"✅ Download hoàn tất! Model lưu tại: {model_path}")
    return model_path

def process_chunk(text_chunk, llm):
    prompt = f"""<|im_start|>system
Bạn là chuyên gia AI y khoa. Nhiệm vụ: trích xuất các khái niệm y tế từ đoạn văn bản lâm sàng.
Chỉ trả về 1 danh sách JSON hợp lệ chứa các object có 2 key: "text" (từ khóa gốc trong văn bản) và "type" (loại khái niệm).
Các loại "type" cho phép: CHẨN_ĐOÁN, TRIỆU_CHỨNG, TÊN_XÉT_NGHIỆM, KẾT_QUẢ_XÉT_NGHIỆM, THUỐC.
Tuyệt đối không giải thích, không in ký tự markdown (```json). Chỉ xuất JSON.
<|im_end|>
<|im_start|>user
Văn bản cần xử lý:
{text_chunk}
<|im_end|>
<|im_start|>assistant
"""
    
    response = llm(
        prompt,
        max_tokens=1024,
        stop=["<|im_end|>"],
        temperature=0.0,
        echo=False
    )
    
    result_text = response['choices'][0]['text']
    try:
        start_idx = result_text.find('[')
        end_idx = result_text.rfind(']') + 1
        if start_idx != -1 and end_idx != -1:
            json_str = result_text[start_idx:end_idx]
            predictions = json.loads(json_str)
            return predictions
        else:
            print("⚠️ Không tìm thấy JSON hợp lệ trong chunk này!")
            return []
    except Exception as e:
        print(f"❌ Lỗi parse JSON trong chunk: {e}\nOutput: {result_text}")
        return []

def sliding_window_extraction(text, llm, chunk_size=1500, overlap=200):
    all_entities = []
    text_length = len(text)
    start = 0
    
    print(f"🔪 Đang băm nhỏ văn bản (Sliding Window): Kích thước={chunk_size}, Overlap={overlap}...")
    chunk_idx = 1
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]
        print(f"\n▶️ Xử lý Chunk {chunk_idx} ({start} -> {end}):")
        
        entities = process_chunk(chunk, llm)
        print(f"   -> Đã trích xuất {len(entities)} thực thể từ Chunk {chunk_idx}.")
        all_entities.extend(entities)
        
        if end == text_length:
            break
        
        # Dịch chuyển cửa sổ đi một đoạn bằng chunk_size - overlap
        start += (chunk_size - overlap)
        chunk_idx += 1
        
    return all_entities

if __name__ == "__main__":
    print("="*50)
    print("🧠 TẦNG 1: LOCAL LLM HOST (Qwen-2.5-7B-Instruct) + CỬA SỔ TRƯỢT")
    print("="*50)
    
    model_path = download_model()
    
    print("🔥 Đang khởi động Lò Phản Ứng LLM (Offload to GPU)...")
    try:
        llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_gpu_layers=-1,
            verbose=False
        )
    except Exception as e:
        print(f"❌ Lỗi khi tải mô hình: {e}")
        exit(1)
        
    print("📚 Đang đọc dữ liệu 1.txt...")
    with open("input/1.txt", "r", encoding="utf-8") as f:
        sample_text = f.read()
        
    print("⚡ Bắt đầu vòng lặp Cửa Sổ Trượt. Quá trình này sẽ tốn nhiều thời gian hơn...")
    llm_entities = sliding_window_extraction(sample_text, llm, chunk_size=1500, overlap=200)
    
    print(f"\n📦 Kết quả RAW tổng gộp từ LLM: Thu được {len(llm_entities)} thực thể.")
    
    print("\n🛡️ BỌC LÓT BẰNG MODULE REGEX & ĐỊNH VỊ TỌA ĐỘ...")
    censored_stars = hunt_censored_stars(sample_text)
    llm_entities.extend(censored_stars)
    
    final_entities = exact_index_matcher(sample_text, llm_entities)
    
    print("\n✅ KẾT QUẢ ĐÃ CHỐT TỌA ĐỘ (PIPELINE HOÀN CHỈNH):")
    for e in final_entities[:10]:
        print(f" -> {e['text']} [{e['type']}] : Vị trí {e['position']}")
    
    print(f"\n🎯 TỔNG CỘNG ĐÃ ĐỊNH VỊ {len(final_entities)} THỰC THỂ KHÔNG THỂ SAI LỆCH!")
    print("="*50)
