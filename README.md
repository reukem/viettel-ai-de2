# 🏥 Viettel AI Race 2026 — Track 2: Cỗ Máy EXODIA (Medical NLP & Knowledge Linking)

> **Author**: Ngô Minh Thiên Bảo (reukem) & Chief Strategist Lucy  
> **Affiliation**: reukem's INDUSTRIES  
> **Competition**: Viettel AI Race 2026 (Chặng đua Trí tuệ Nhân tạo Viettel) — Đề 2  
> **Core Theme**: Clinical Named Entity Recognition, ICD-10 & RxNorm Semantic Concept Normalization, and Assertion Classification  

---

## 🎯 1. Mission & Task Description

In clinical informatics, hospital electronic health records (EHR / Bệnh án điện tử) contain unstructured medical notes written by physicians, filled with abbreviations, typos, and patient privacy redactions.

The goal of Viettel AI Race Đề 2:
1. Parse **100 unstructured clinical notes** (`input_turn2_vong1.zip`).
2. **Extract Clinical Entities**: Identify diseases, diagnoses (`CHẨN_ĐOÁN`), clinical symptoms (`TRIỆU_CHỨNG`), and medications (`THUỐC`), locating their exact zero-indexed character offsets (`[start, end]`).
3. **Handle Censored Data**: Unmask and correctly index redacted tokens (`*******`).
4. **Medical Concept Normalization (Linking)**:
   - Map diseases and symptoms to official **ICD-10** codes (Bộ Y Tế / WHO).
   - Map medications to **RxNorm** pharmaceutical concept identifiers.
5. **Clinical Assertion Classification**: Classify clinical status for each entity:
   - `isNegated`: True if the patient does NOT have the condition (e.g., *"không sốt"*, *"chưa phát hiện khối u"*).
   - `isHistorical`: True if the condition occurred in the past (e.g., *"tiền sử đau dạ dày 5 năm trước"*).
   - `isFamily`: True if the condition belongs to a family relative (e.g., *"bố ruột mắc đái tháo đường"*).
   - `isHypothetical`: True if the condition is a suspected rule-out diagnosis (e.g., *"nghi ngờ viêm phổi"*).

---

## 🛡️ 2. The 3-Tier EXODIA Architecture

```
                    ┌────────────────────────────────────────┐
                    │      100 Raw Clinical Notes (.txt)     │
                    └───────────────────┬────────────────────┘
                                        │
┌───────────────────────────────────────▼────────────────────────────────────────┐
│ 🛡️ TẦNG 1: NER & INDEX LOCKING ENGINE (`layer1_ner.py`)                        │
│  • hunt_censored_stars: Defeats the ******* privacy traps                      │
│  • exact_index_matcher: Multi-pass string boundary lock with re.IGNORECASE     │
│  • non_maximum_suppression: Prunes nested, overlapping token spans             │
└───────────────────────────────────────┬────────────────────────────────────────┘
                                        │
┌───────────────────────────────────────▼────────────────────────────────────────┐
│ 🗺️ TẦNG 2: MEDICAL KNOWLEDGE RETRIEVAL & RAG (`layer2_rag_engine.py`)         │
│  • Dense Semantic Embedding: keepitreal/vietnamese-sbert                       │
│  • Vector Database: ChromaDB semantic search for ICD-10 codes                  │
│  • RxNorm API Gateway: layer2_rxnorm_api.py query resolution                  │
└───────────────────────────────────────┬────────────────────────────────────────┘
                                        │
┌───────────────────────────────────────▼────────────────────────────────────────┐
│ 🧠 TẦNG 3: CLINICAL ASSERTION REASONING (`layer3_assertions.py`)               │
│  • Context Window Analysis: [-50 : +50] characters surrounding entity         │
│  • Multi-label status: isNegated, isHistorical, isFamily, isHypothetical       │
└───────────────────────────────────────┬────────────────────────────────────────┘
                                        │
                    ┌───────────────────▼────────────────────┐
                    │  🏭 main.py Batch Assembly Pipeline    │
                    │  Outputs 100 JSONs -> submission.zip   │
                    └────────────────────────────────────────┘
```

---

## ⚡ 3. Key Components & Implementation Files

- **[main.py](main.py)**: Central orchestrator reading 100 clinical notes from `input/`, executing Tier 1 $\rightarrow$ Tier 2 $\rightarrow$ Tier 3, producing structured JSON outputs, and archiving directly into `submission.zip`.
- **[layer1_ner.py](layer1_ner.py)**: Core entity extraction, zero-index offset coordinate mapper, and Non-Maximum Suppression algorithm.
- **[layer2_rag_engine.py](layer2_rag_engine.py)**: ChromaDB vector retrieval system for ICD-10 medical terminology.
- **[layer2_rxnorm_api.py](layer2_rxnorm_api.py)**: NIH RxNav API integration for pharmaceutical normalization.
- **[layer3_assertions.py](layer3_assertions.py)**: Clinical context assertion detector.
- **[evaluator.py](evaluator.py)**: Competition scoring engine evaluating exact-match F1, partial-match F1, assertion accuracy, and code linking precision.

---

## 🚀 4. Usage & Execution

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the complete pipeline
python main.py

# 3. Output
# Generated: output/*.json
# Archive: submission.zip (Ready for Viettel AI Portal upload)
```

---
*Viettel AI Race 2026 — Track 2 Solution Archive*
