import json

def calculate_wer(reference, hypothesis):
    ref_words = reference.split()
    hyp_words = hypothesis.split()
    d = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]
    for i in range(len(ref_words) + 1): d[i][0] = i
    for j in range(len(hyp_words) + 1): d[0][j] = j
    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            cost = 0 if ref_words[i-1] == hyp_words[j-1] else 1
            d[i][j] = min(d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + cost)
    if len(ref_words) == 0: return 1.0 if len(hyp_words) > 0 else 0.0
    return d[len(ref_words)][len(hyp_words)] / len(ref_words)

def calculate_jaccard(list1, list2):
    set1, set2 = set(list1), set(list2)
    if len(set1) == 0 and len(set2) == 0: return 1.0
    if len(set1) == 0 and len(set2) != 0: return 0.0
    union = len(set1.union(set2))
    return len(set1.intersection(set2)) / union if union > 0 else 0.0

def evaluate_sample(ground_truth, predictions):
    gt_matched = {i: False for i in range(len(ground_truth))}
    pred_matched = {j: False for j in range(len(predictions))}
    text_scores, assertion_scores, candidate_scores = [], [], []
    
    # 1. Match by position
    for i, gt in enumerate(ground_truth):
        for j, pred in enumerate(predictions):
            if gt['position'] == pred['position']:
                if gt['type'] == pred['type']:
                    gt_matched[i], pred_matched[j] = True, True
                    text_scores.append(1 - calculate_wer(gt['text'], pred['text']))
                    assertion_scores.append(calculate_jaccard(gt.get('assertions', []), pred.get('assertions', [])))
                    if gt['type'] in ['THUỐC', 'CHẨN_ĐOÁN']:
                        candidate_scores.append(calculate_jaccard(gt.get('candidates', []), pred.get('candidates', [])))
                else:
                    # Type mismatch: Do nothing here, let them be unmatched to penalize 0 for both
                    pass 
                    
    # Unmatched GT and Pred -> 0 points (Type Mismatch Penalty & Missing Entities)
    for i, matched in gt_matched.items():
        if not matched:
            text_scores.append(0.0)
            assertion_scores.append(0.0)
            if ground_truth[i]['type'] in ['THUỐC', 'CHẨN_ĐOÁN']: candidate_scores.append(0.0)
    for j, matched in pred_matched.items():
        if not matched:
            text_scores.append(0.0)
            assertion_scores.append(0.0)
            if predictions[j]['type'] in ['THUỐC', 'CHẨN_ĐOÁN']: candidate_scores.append(0.0)
                
    avg_text = sum(text_scores) / len(text_scores) if text_scores else 0
    avg_assert = sum(assertion_scores) / len(assertion_scores) if assertion_scores else 0
    avg_cand = sum(candidate_scores) / len(candidate_scores) if candidate_scores else 0
    return avg_text, avg_assert, avg_cand

def evaluate(ground_truth_list, predictions_list):
    total_text, total_assert, total_cand = 0, 0, 0
    for gt, pred in zip(ground_truth_list, predictions_list):
        t, a, c = evaluate_sample(gt, pred)
        total_text += t
        total_assert += a
        total_cand += c
        
    n = len(ground_truth_list)
    final_text = total_text / n if n > 0 else 0
    final_assert = total_assert / n if n > 0 else 0
    final_cand = total_cand / n if n > 0 else 0
    
    return {
        "text_score": final_text,
        "assertions_score": final_assert,
        "candidates_score": final_cand,
        "final_score": 0.3 * final_text + 0.3 * final_assert + 0.4 * final_cand
    }

if __name__ == "__main__":
    import os
    if os.path.exists("dummy_truth_1.json"):
        with open("dummy_truth_1.json", "r", encoding="utf-8") as f: gt = json.load(f)
        pred = json.loads(json.dumps(gt))
        
        print("="*50)
        print("🎯 TEST 1: PERFECT PREDICTION (Expect 1.0 Final Score)")
        print(evaluate([gt], [pred]))
        
        print("\n" + "="*50)
        print("💀 TEST 2: TYPE MISMATCH PENALTY (Change type of Entity 1)")
        pred[0]['type'] = 'TRIỆU_CHỨNG' if gt[0]['type'] == 'CHẨN_ĐOÁN' else 'CHẨN_ĐOÁN'
        print(evaluate([gt], [pred]))
        print("="*50)
