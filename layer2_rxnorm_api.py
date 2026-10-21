import requests
import json
import time

class RxNormAPI:
    def __init__(self):
        self.base_url = "https://rxnav.nlm.nih.gov/REST"
        # Bộ nhớ đệm (Cache) để tránh gọi API trùng lặp cho cùng một loại thuốc
        self.cache = {}

    def get_rxcui(self, drug_name):
        """
        Gửi yêu cầu tới RxNorm REST API để lấy mã RxCUI chuẩn.
        Sử dụng approximateTerm để quét toàn bộ chuỗi liều lượng.
        """
        if drug_name in self.cache:
            return self.cache[drug_name]
            
        try:
            # Gọi API approximateTerm để xử lý cả cụm từ phức tạp
            url = f"{self.base_url}/approximateTerm.json?term={drug_name}&maxEntries=3"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if "approximateGroup" in data and "candidate" in data["approximateGroup"]:
                    candidates = data["approximateGroup"]["candidate"]
                    if candidates:
                        # Lấy mã rxcui của top 1 candidate có điểm số cao nhất
                        rxcui = candidates[0]["rxcui"]
                        self.cache[drug_name] = [rxcui]
                        return [rxcui]
                        
            # Nếu không tìm thấy, lưu cache rỗng để lần sau không phải gọi lại
            self.cache[drug_name] = []
            return []
            
        except Exception as e:
            print(f"❌ Lỗi khi gọi API RxNorm cho '{drug_name}': {e}")
            return []

if __name__ == "__main__":
    print("="*50)
    print("💊 NÂNG CẤP MẠNG LƯỚI RxNORM: TÌM KIẾM THEO LIỀU LƯỢNG 💊")
    print("="*50)
    api = RxNormAPI()
    
    # Test với đúng chuỗi của đề bài Viettel AI
    test_drugs = [
        "amlodipine 10 mg po daily",
        "aspirin 81 mg po daily",
        "clonazepam 1.5 mg po qhs"
    ]
    
    for drug in test_drugs:
        print(f"⏳ Đang truy vấn mã cho: '{drug}'...")
        codes = api.get_rxcui(drug)
        if codes:
            print(f"   -> ✅ Thành công! Mã RxNorm (RxCUI): {codes}")
        else:
            print(f"   -> ❌ Không tìm thấy mã cho '{drug}'")
        time.sleep(0.5) # Tránh bị rate limit
