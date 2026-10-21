import re

def non_maximum_suppression(entities):
    """
    Thuật toán Thanh Trừng (NMS)
    Lọc bỏ các thực thể bị chồng chéo (Overlap). 
    Nếu thực thể A nằm gọn trong thực thể B, tiêu diệt A, giữ lại B.
    """
    if not entities:
        return []
        
    # Sắp xếp theo start_index tăng dần, nếu bằng thì ưu tiên end_index giảm dần (dài nhất trước)
    entities.sort(key=lambda x: (x["position"][0], -x["position"][1]))
    
    nms_results = []
    for current in entities:
        if not nms_results:
            nms_results.append(current)
            continue
            
        last = nms_results[-1]
        last_start, last_end = last["position"]
        curr_start, curr_end = current["position"]
        
        # Nếu current bị lọt thỏm hoặc cắt ngang bên trong last -> Bỏ qua (tiêu diệt)
        if curr_start < last_end:
            continue
        else:
            nms_results.append(current)
            
    return nms_results

def hunt_censored_stars(text):
    """Bắt các chuỗi *** bị giấu"""
    pattern = re.compile(r'\*{3,}')
    results = []
    for match in pattern.finditer(text):
        results.append({
            "text": match.group(0),
            "type": "THUỐC",
            "position": [match.start(), match.end()]
        })
    return results

def exact_index_matcher(text, predicted_entities):
    """Dò ngược vị trí với cờ chống mù chữ hoa (IGNORECASE)"""
    results = []
    seen_matches = set()
    
    for entity in predicted_entities:
        keyword = entity.get("text", "")
        e_type = entity.get("type", "UNKNOWN")
        
        if not keyword:
            continue
            
        # [Liều Thuốc 1]: Thêm cờ re.IGNORECASE
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        
        for match in pattern.finditer(text):
            pos_tuple = (match.start(), match.end())
            if pos_tuple not in seen_matches:
                seen_matches.add(pos_tuple)
                # Lấy text gốc từ văn bản để không bị sai chữ hoa/thường
                results.append({
                    "text": text[match.start():match.end()],
                    "type": e_type,
                    "position": list(pos_tuple)
                })
                
    return results
