# 🏥 Viettel AI Race 2026 — Track 2: Cỗ Máy EXODIA (Medical NLP & Knowledge Linking)
## Clinical Named Entity Recognition, Concept Normalization & Assertion Reasoning

[![Competition](https://img.shields.io/badge/Competition-Viettel%20AI%20Race%202026-ED1C24?style=for-the-badge&logo=target&logoColor=white)](https://viettel.vn)
[![Track](https://img.shields.io/badge/Track-2%3A%20Medical%20Knowledge%20Retrieval-blue?style=for-the-badge)](https://viettel.vn)
[![Team](https://img.shields.io/badge/Team-reukem-gold?style=for-the-badge)](https://github.com/reukem)
[![Score](https://img.shields.io/badge/Official%20Score-0.9833%20%2F%20100-red?style=for-the-badge)](https://github.com/reukem/viettel-ai-de2)
[![Rank](https://img.shields.io/badge/Leaderboard%20Rank-%23363%20(Dead%20Last)-critical?style=for-the-badge)](https://github.com/reukem/viettel-ai-de2)
[![Validation](https://img.shields.io/badge/Validation%20Benchmark-1.0%20%2F%201.0-brightgreen?style=for-the-badge)](https://github.com/reukem/viettel-ai-de2)

> **Lead Architect**: Ngô Minh Thiên Bảo ([reukem](https://github.com/reukem))   
> **Affiliation**: reukem's INDUSTRIES  
> **Competition**: Viettel AI Race 2026 — Vòng 1: Sơ loại (02/07/2026 – 31/07/2026)  
> **Core Theme**: Clinical Named Entity Recognition, ICD-10 & RxNorm Semantic Concept Normalization, and Assertion Classification  

---

## 🤦‍♂️ Post-Mortem & Honest Reflection: "Why Did I Even Enroll in This?!"

> *"Why did I even enroll in this?? I spent so much time for it and I received nothing... Worse yet, there were a lot of interesting and easier competitions for high school students I could have used my summer for at the time.. Urgh. And no, that's 0.9833 / 100, my dear... Literally dead last because well, you know!"*  
> — **Ngô Minh Thiên Bảo (reukem)**, Lead Builder

### 💀 The Brutal Reality Check:
1. **0.9833 Out of 100 (Dead Last `#363`)**: The leaderboard was NOT on an $F_1 \in [0.0, 1.0]$ decimal scale — it was out of **100 total points**! That means our score was **0.9833%**, landing dead last on the national board. Pure pain!
2. **Wrong Weight Class**: A solo 11th-grade high school builder armed with rule-based regex and keepitreal/vietnamese-sbert going up against hospital bioinformatics teams, enterprise health-tech labs, and university medical NLP researchers. 
3. **Summer Opportunity Cost**: Wasting precious summer weeks reading ICD-10 ontology docs and debugging privacy redaction asterisks (`*******`) when there were plenty of awesome, accessible high-school hackathons and AI competitions available.
4. **The Silver Lining**: At least our pipeline didn't crash — **100/100 JSONs passed schema validation** with zero formatting rejections. And we learned the hard truth: enterprise clinical EHR requires massive fine-tuned LLMs / BioBERT, not late-night regex heuristics!

---

## 🏆 Official Competition Results & Leaderboard Performance

### Official Leaderboard Metrics (Viettel AI Race Portal)
| Metric | Result | System Status / Notes |
| :--- | :---: | :--- |
| **Official Score** | **`0.9833 / 100`** | 💀 Literally dead last! Initial baseline submission with regex & semantic retrieval |
| **Leaderboard Rank** | **`#363`** | Officially dead last on the Viettel AI Portal national leaderboard |
| **Notes Scored (`num_scored`)** | **`100 / 100`** | 100% of submitted EHR notes accepted and evaluated (format succeeded!) |
| **Records Processed (`num_records`)** | **`100 / 100`** | Flawless batch pipeline throughput |
| **Schema Compliance** | **100% Valid JSON** | **0 Format Errors** — Zero formatting rejections or schema violations |
| **Submission Archive** | `submission.zip` | 100 structured clinical JSON predictions (`1.json` - `100.json`) |
| **Submission Timestamp** | `31/07/2026, ~00:06 - 00:18` | Completed and graded on the final day of Vòng 1 |

### Local Ground Truth Validation (`evaluator.py`)
When evaluated against the official competition validation ground truth (`dummy_truth_1.json`):
- **Clinical Text Entity Score (`text_score`)**: **`1.0`** (100% Precision & Recall)
- **Assertion Classification Score (`assertions_score`)**: **`1.0`** (100% Accuracy across 4 assertion tags)
- **Candidate Normalization Score (`candidates_score`)**: **`1.0`** (100% ICD-10 & RxNorm Mapping)
- **Final Validation Score**: **`1.0 / 1.0`** ($0.3 \times \text{text} + 0.3 \times \text{assertion} + 0.4 \times \text{candidates}$)

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
*Viettel AI Race 2026 — Track 2 Solution Archive | Authored by Ngô Minh Thiên Bảo (reukem)*
