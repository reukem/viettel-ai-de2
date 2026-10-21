import os
import json
import chromadb
from sentence_transformers import SentenceTransformer

class MedicalKnowledgeBase:
    def __init__(self, db_path="medical_vector_db"):
        print("⏳ Khởi tạo Căn Cứ Lưu Trữ ChromaDB...")
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        
        print("⏳ Đang tải Lò Rèn Khái Niệm (Embedding Model: keepitreal/vietnamese-sbert)...")
        # Sử dụng mô hình tiếng Việt chuyên dụng gọn nhẹ (chạy bằng CPU/GPU đều mượt)
        self.encoder = SentenceTransformer("keepitreal/vietnamese-sbert")
        print("✅ Lò Rèn Vector đã sẵn sàng!")
        
        # Khởi tạo Collections (Bảng) cho Bệnh (ICD-10) và Thuốc (RxNorm)
        self.collections = {
            "ICD-10": self.chroma_client.get_or_create_collection(name="icd10_dictionary"),
            "RxNorm": self.chroma_client.get_or_create_collection(name="rxnorm_dictionary")
        }

    def ingest_data(self, dictionary_type, filepath):
        """
        Đọc file từ điển JSON và nhúng vào bộ nhớ Vector.
        """
        if dictionary_type not in self.collections:
            raise ValueError("Chỉ hỗ trợ dictionary_type là 'ICD-10' hoặc 'RxNorm'")
            
        print(f"📦 Đang chuẩn bị Khai Quật Thánh Kinh cho {dictionary_type} từ {filepath}...")
        
        if not os.path.exists(filepath):
            print(f"⚠️ CẢNH BÁO: Không tìm thấy file {filepath}! Xin chờ dữ liệu từ Bộ Tư Lệnh.")
            return False
            
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        ids = list(data.keys())
        texts = list(data.values())
        
        print(f"🔄 Đang nhúng (Embed) {len(texts)} khái niệm vào Vector Space...")
        embeddings = self.encoder.encode(texts).tolist()
        
        print(f"💾 Đang lưu trữ vào ChromaDB...")
        self.collections[dictionary_type].add(ids=ids, embeddings=embeddings, documents=texts)
        
        print(f"✅ Đã nhúng toàn bộ dữ liệu {dictionary_type} vào Vector Database thành công!")
        return True

    def search_candidates(self, query_text, dictionary_type, top_k=3):
        """
        Tìm kiếm các mã code gần nghĩa nhất.
        """
        if dictionary_type not in self.collections:
            return []
            
        collection = self.collections[dictionary_type]
        
        if collection.count() == 0:
            print(f"⚠️ Database {dictionary_type} đang trống! Hãy Ingest Data trước khi tìm kiếm.")
            return []
            
        # Nhúng (embed) cụm từ query thành dãy số Vector
        query_vector = self.encoder.encode([query_text]).tolist()
        
        # Quét qua ChromaDB bằng thuật toán HNSW tìm láng giềng gần nhất (Semantic Search)
        # N_results không được vượt quá số lượng item trong DB
        actual_top_k = min(top_k, collection.count())
        
        results = collection.query(
            query_embeddings=query_vector,
            n_results=actual_top_k
        )
        
        candidates = results['ids'][0] if results['ids'] else []
        documents = results['documents'][0] if results.get('documents') else []
        distances = results['distances'][0] if results.get('distances') else []
        
        return list(zip(candidates, documents, distances))

if __name__ == "__main__":
    import shutil
    # Reset db test
    if os.path.exists("medical_vector_db"):
        shutil.rmtree("medical_vector_db")
        
    print("="*50)
    print("🗺️ CHIẾN DỊCH MOCK DATA: UNIT TEST TẦNG 2")
    print("="*50)
    
    try:
        mkb = MedicalKnowledgeBase()
        
        # Kích hoạt Lò Rèn
        mkb.ingest_data("ICD-10", "dummy_icd10.json")
        
        # Thử Thách Bắn Tỉa
        query = "Bệnh nhân bị sốt rất cao"
        print(f"\n🔍 Thử Thách Bắn Tỉa (Semantic Search):")
        print(f"Truy vấn: '{query}'")
        
        results = mkb.search_candidates(query, "ICD-10", top_k=3)
        print("\n🎯 Kết quả xếp hạng khoảng cách (Càng nhỏ càng giống):")
        for i, (code, doc, dist) in enumerate(results):
            print(f"Top {i+1} -> Mã: {code} | Bệnh chuẩn: {doc} | Distance: {dist:.4f}")
            
        if results and results[0][0] == "R50.9":
            print("\n🏆 TUYỆT VỜI! MÔ HÌNH ĐÃ TÌM ĐÚNG MÃ R50.9 LÊN TOP 1! CHROMA DB HOẠT ĐỘNG HOÀN HẢO! 🏆")
        else:
            print("\n❌ LỖI: Mô hình không tìm thấy hoặc xếp sai mã R50.9!")
            
    except Exception as e:
        print(f"❌ Lỗi khởi tạo: {e}")
        
    print("="*50)
