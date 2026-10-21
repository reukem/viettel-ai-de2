import json

with open("input/1.txt", "r", encoding="utf-8") as f:
    text = f.read()

def find_entity(query, entity_type, candidates=[], assertions=[]):
    start = text.find(query)
    if start == -1:
        print(f"⚠️ Warning: '{query}' not found in 1.txt.")
        return None
    return {
        "text": query,
        "type": entity_type,
        "candidates": candidates,
        "assertions": assertions,
        "position": [start, start + len(query)]
    }

entities = []
entities.append(find_entity("Thiếu men G6PD", "CHẨN_ĐOÁN", candidates=["D55.0"]))
entities.append(find_entity("Sốt cao", "TRIỆU_CHỨNG"))
entities.append(find_entity("*******", "THUỐC", candidates=["313782"], assertions=["isNegated"]))

entities = [e for e in entities if e is not None]

with open("dummy_truth_1.json", "w", encoding="utf-8") as f:
    json.dump(entities, f, ensure_ascii=False, indent=4)

print(f"✅ Đã tạo dummy_truth_1.json thành công với {len(entities)} thực thể chuẩn!")
