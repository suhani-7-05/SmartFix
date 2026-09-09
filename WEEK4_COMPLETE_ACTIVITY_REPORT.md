# SmartFix: Week 4 Hands-On Activity Complete Report
## Category-Wise Quantitative LLM Evaluation, RAG Pipeline Analysis & Repository Codebase Understanding

**Project Name**: SmartFix — Intelligent DevOps & Field Equipment Troubleshooting Assistant  
**Academic Stage**: Week 4 Hands-On Activity — Multi-Model Comparison & Evaluation  
**Evaluation Models**: Code Llama (7B), StarCoder2 (3B), Qwen 2.5 Coder (1.5B)  
**Evaluation Categories**: 7 Software Engineering Categories (25 Total Evaluation Tasks)  
**Execution Environment**: Local Ollama Runtime (Windows 11 / CPU Execution)  
**Knowledge Base Foundation**: 542 ChromaDB Vector Embeddings with `nomic-embed-text`  

---

## Table of Contents
1. [Executive Summary & Addressing Feedback](#1-executive-summary--addressing-feedback)
2. [SmartFix System Architecture](#2-smartfix-system-architecture)
3. [EXERCISE 1 – Evaluated Candidate LLM Models](#3-exercise-1--evaluated-candidate-llm-models)
4. [EXERCISE 2 – The 7-Category Evaluation Dataset (25 Tasks)](#4-exercise-2--the-7-category-evaluation-dataset-25-tasks)
5. [EXERCISE 3 – Quantitative Evaluation Methodology & Metric Formulations](#5-exercise-3--quantitative-evaluation-methodology--metric-formulations)
6. [EXERCISE 4 – Category-Wise Quantitative Comparison Matrix (All 7 Categories)](#6-exercise-4--category-wise-quantitative-comparison-matrix-all-7-categories)
7. [EXERCISE 5 – Answers to Professor Kiran's 7 Analytical Questions](#7-exercise-5--answers-to-professor-kirans-7-analytical-questions)
8. [EXERCISE 6 – RAG Pipeline End-to-End Trace Analysis](#8-exercise-6--rag-pipeline-end-to-end-trace-analysis)
9. [EXERCISE 7 – Repository Architecture & Frontend Multi-Model Calling](#9-exercise-7--repository-architecture--frontend-multi-model-calling)
10. [Reproduction & Verification Guide](#10-reproduction--verification-guide)
11. [Conclusion & Recommendations](#11-conclusion--recommendations)

---

## 1. Executive Summary & Addressing Feedback

In Week 4, the SmartFix platform progressed from a functional microservice prototype into an empirically benchmarked AI engineering system. 

### Addressing Critical Evaluation Feedback:
As emphasized in the Week 4 evaluation notes, previous submissions across groups mistakenly reported only monolithic, aggregate performance numbers (e.g., *"Model A has 85% overall accuracy"*). 

In this comprehensive submission, we strictly adhere to the true academic objective:
1. **Deliberate 7-Category Division**: The 25 evaluation tasks are systematically partitioned into the seven distinct software engineering categories:
   - **Explanation**
   - **Code Retrieval**
   - **Dependency Understanding**
   - **Bug Analysis**
   - **Code Generation**
   - **Refactoring**
   - **RAG based Question**
2. **Category-Wise Quantitative Comparison**: The performance of all three candidate models is evaluated and contrasted **separately for each of the seven categories** using task-appropriate metrics:
   - *Accuracy / Correctness (%)*
   - *Semantic Relevance (0.0 to 1.0)*
   - *Hallucination Rate (%)*
   - *Vector Retrieval Quality (Cosine Similarity / MRR)*
   - *Code Test-Pass Rate (%)* (via dynamic runtime sandbox execution)
   - *Response Latency (seconds)*
   - *Token Usage and Hardware Footprint (RAM MB, CPU %)*
3. **Explicit Answers to the 7 Core Analytical Questions**: We directly answer which model performs best for each of the 7 software engineering task types, supported by empirical data and architectural analysis.
4. **Interactive Multi-Model Frontend**: Upgraded the Vue 3 dashboard to call all three local Ollama models with live side-by-side comparison, fixed model resolution, and a dedicated 7-Category Benchmark Dashboard tab.

---

## 2. SmartFix System Architecture

SmartFix coordinates an event-driven, decoupled microservice mesh built on FastAPI and Vue 3:

```
                                    +-----------------------------------+
                                    |     Vite + Vue 3 Web Frontend     |
                                    |     (Port 5173 / Glassmorphic UI) |
                                    +-----------------+-----------------+
                                                      |
                                                      v HTTP Proxy
                                    +-----------------------------------+
                                    |   API Gateway / Orchestrator      |
                                    |        (Port 8000 / FastAPI)      |
                                    +--------+--------+--------+--------+
                                             |        |        |
             +-------------------------------+        |        +-------------------------------+
             |                                        |                                        |
             v (async)                                v (async)                                v (async)
+-------------------------+              +-------------------------+              +-------------------------+
|    Equipment Service    |              |  Knowledge Base & RAG   |              |  Safety Engine Service  |
|       (Port 8002)       |              |       (Port 8001)       |              |       (Port 8003)       |
| - Machine metadata      |              | - ChromaDB Vector Store |              | - Deterministic Rules   |
| - Electrical ratings    |              | - nomic-embed-text      |              | - BLOCKED / WARNING     |
| - Operating specs       |              | - Genuine PDF Manuals   |              | - High Voltage / LOTO   |
+-------------------------+              +-------------------------+              +-------------------------+
             |                                        |                                        |
             v (async)                                v (async)                                v (async)
+-------------------------+              +-------------------------+              +-------------------------+
| Maintenance History Svc |              |   Spare Parts Catalog   |              |   LLM Gateway Service   |
|       (Port 8004)       |              |       (Port 8005)       |              |       (Port 8007)       |
| - Historical work orders|              | - OEM Part Numbers      |              | - Ollama REST Interface |
| - Past component wear   |              | - Stock & Specifications|              | - Multi-Model Switching |
+-------------------------+              +-------------------------+              +-------------------------+
                                                      |
                                                      v (async dispatch)
                                         +-------------------------+
                                         |     Tickets Service     |
                                         |       (Port 8006)       |
                                         | - Auto work-order dispatch
                                         | - Priority classification|
                                         +-------------------------+
```

---

## 3. EXERCISE 1 – Evaluated Candidate LLM Models

To assess how parameter scale, pretraining objectives, and context windows impact diverse software engineering tasks, three distinct models were installed and executed locally via Ollama:

| Model Attribute | Model 1: Code Llama | Model 2: StarCoder2 | Model 3: Qwen 2.5 Coder |
|---|---|---|---|
| **Ollama Model ID** | `codellama:latest` | `starcoder2:3b` | `qwen2.5-coder:1.5b` |
| **Parameter Scale** | 7.0 Billion | 3.0 Billion | 1.54 Billion |
| **Disk Footprint** | 3.8 GB | 1.7 GB | 986 MB |
| **Context Window** | 16,384 tokens | 16,384 tokens | 32,768 tokens |
| **Primary Focus** | Deep Reasoning & Code Synthesis | Code Completion & Structure | Fast Instruction-Following & Code |
| **Developer** | Meta AI | BigCode / ServiceNow / HF | Alibaba Cloud |

### Rigorous Experimental Controls:
- **Zero Simulation**: All models were executed through live HTTP POST calls to `http://localhost:11434/api/generate`.
- **Identical Decoding Hyperparameters**: Temperature $T=0.2$, Top-P $=0.95$, Max Predict Tokens $=130$, Thread Allocation $=4$.
- **Unified Prompt Assembly**: Standardized prompts providing identical equipment specs, safety decisions, and retrieved manual chunks.

---

## 4. EXERCISE 2 – The 7-Category Evaluation Dataset (25 Tasks)

The standardized dataset is persisted in [`eval/dataset_25_questions.json`](file:///c:/Users/suhan/Desktop/SmartFix/SmartFix/eval/dataset_25_questions.json) and [`evaluation/dataset.json`](file:///c:/Users/suhan/Desktop/SmartFix/SmartFix/evaluation/dataset.json). It contains exactly 25 tasks mapped across the 7 deliberate software-engineering categories:

```
                                  [25 Evaluation Tasks]
                                            |
         +----------+----------+----------+----------+----------+----------+
         |          |          |          |          |          |          |
         v          v          v          v          v          v          v
   [Explanation] [Code Retr] [Dependency]  [Bug Anal] [CodeGen]  [Refactor] [RAG Task]
     Q01–Q03     Q04–Q06      Q07–Q09     Q10–Q13    Q14–Q16    Q17–Q19    Q20–Q25
```

### Complete Dataset Specification:

#### Category 1: Explanation (Tasks Q01 – Q03)
* **Q01** (*Vector Store Similarity*):
  - *Question*: "What does the search_similar() function in vector_store.py do?"
  - *Ground Truth*: Queries ChromaDB collection with cosine distance, calculates similarity as `(1.0 - distance)`, and formats returned chunk metadata.
* **Q02** (*Safety Engine Evaluation*):
  - *Question*: "How does the Safety Engine service evaluate safety rules in services/safety/main.py?"
  - *Ground Truth*: Evaluates explicit deterministic rules (400V live access, high hydraulic pressure) returning ALLOWED, WARNING, or BLOCKED with required precautions.
* **Q03** (*Orchestrator Lifecycle*):
  - *Question*: "What is the purpose of the Orchestrator Service in services/orchestrator/main.py?"
  - *Ground Truth*: Coordinates sequential microservice calls, aggregates contextual data, and records execution trace duration latencies.

#### Category 2: Code Retrieval (Tasks Q04 – Q06)
* **Q04** (*Text Chunker Location*):
  - *Question*: "Which file handles text chunking and character offset tracking for uploaded documents?"
  - *Ground Truth*: `services/knowledge-base/chunker.py` (400-char chunks, 50-char overlap, start/end offsets).
* **Q05** (*Trace Component Location*):
  - *Question*: "Which file defines the Vue 3 component for rendering the real step-by-step service trace timeline?"
  - *Ground Truth*: `frontend/src/components/admin/ExecutionTraceViewer.vue`.
* **Q06** (*Tickets Endpoint Location*):
  - *Question*: "Which backend file defines the REST endpoint for creating automated service tickets?"
  - *Ground Truth*: `services/tickets/main.py` (`POST /tickets/create`).

#### Category 3: Dependency Understanding (Tasks Q07 – Q09)
* **Q07** (*Service Call Graph*):
  - *Question*: "Which microservices call the Equipment Service on port 8002?"
  - *Ground Truth*: The Orchestrator Service (`services/orchestrator/main.py`) during Step 1 of the troubleshooting flow.
* **Q08** (*Embedding Persistence Storage*):
  - *Question*: "Which external library and database store the dense text embeddings for RAG retrieval?"
  - *Ground Truth*: ChromaDB stores persistent vector embeddings under `data/chroma`, while SQLite tracks metadata in `data/knowledge-base.db`.
* **Q09** (*LLM Gateway Communication*):
  - *Question*: "How does the LLM Gateway Service interact with Ollama?"
  - *Ground Truth*: `services/llm/main.py` sends HTTP POST requests to `http://localhost:11434/api/generate` with augmented RAG and safety prompt payloads.

#### Category 4: Bug Analysis (Tasks Q10 – Q13)
* **Q10** (*Empty Vector Search Edge Case*):
  - *Question*: "What would happen if the ChromaDB vector search returns empty results for a RAG query?"
  - *Ground Truth*: `constructed_context` gracefully falls back to "No manual context found." without unhandled exceptions.
* **Q11** (*Hydraulic Pressure Drop Diagnosis*):
  - *Question*: "What causes hydraulic pressure drop below 160 bar in EQ-1023 according to the technical manual?"
  - *Ground Truth*: Clogging of the 10-micron inlet suction filter (`HP-FLTR-05`) or miscalibration of relief valve `HP-VALV-210`.
* **Q12** (*High-Voltage Terminal Arc Flash*):
  - *Question*: "Why does attempting to open the 400V terminal box on EQ-3081 while live result in a BLOCKED decision?"
  - *Ground Truth*: Live 400V 3-phase contact carries lethal electrical arc flash and electrocution hazards; requires deterministic lockout.
* **Q13** (*NumPy Array Truthiness Exception*):
  - *Question*: "What error occurs if an array truthiness check is evaluated on a NumPy vector returned by ChromaDB?"
  - *Ground Truth*: Raises `ValueError: The truth value of an array with more than one element is ambiguous`, resolved via explicit `is not None and len() > 0`.

#### Category 5: Code Generation (Tasks Q14 – Q16)
* **Q14** (*Regex ID Parser*):
  - *Question*: "Write a Python function to parse equipment IDs like EQ-1023 from a query string."
  - *Ground Truth*: `def extract_equipment_id(text: str, default_id: str = 'EQ-1023') -> str: ...`
* **Q15** (*Safety Unit Test*):
  - *Question*: "Write a unit test for verifying the Safety Engine ALLOWED decision on basic queries."
  - *Ground Truth*: Defines test function asserting `res.json()['decision'] == 'ALLOWED'`.
* **Q16** (*FastAPI Health Check Route*):
  - *Question*: "Write a FastAPI health check endpoint returning service name and status."
  - *Ground Truth*: `@app.get('/health') async def health_check(): return {'status': 'ok', ...}`

#### Category 6: Refactoring (Tasks Q17 – Q19)
* **Q17** (*Batching Vector Search*):
  - *Question*: "How can vector search performance in vector_store.py be optimized for bulk queries?"
  - *Ground Truth*: Pass query batches to a single `collection.query()` call to leverage SIMD vector parallelism.
* **Q18** (*Concurrent Async Microservice Calls*):
  - *Question*: "Suggest an improvement to the HTTP service calls in orchestrator/main.py to improve latency."
  - *Ground Truth*: Execute independent service calls (Equipment, History, RAG, Safety) concurrently via `asyncio.gather()`.
* **Q19** (*Semantic Chunking Enhancement*):
  - *Question*: "How can text chunking in chunker.py be enhanced beyond fixed character length?"
  - *Ground Truth*: Implement semantic boundary chunking (splitting on markdown headings and paragraphs).

#### Category 7: RAG based Question (Tasks Q20 – Q25)
* **Q20** (*Filter Replacement LOTO*): "What is the mandatory safety precaution before replacing part HP-FLTR-05 on EQ-1023?" (LOTO, depressurize to 0 bar).
* **Q21** (*Tail Pulley Belt Tension*): "What is the tail pulley belt tension specification for CB-200 conveyor (EQ-2045)?" (45 kN via `CB-BOLT-M20`).
* **Q22** (*Megger Insulation Test*): "What insulation resistance value is required during Megger testing on motor IM-750 (EQ-3081)?" (100 MΩ at 1000V DC).
* **Q23** (*Hydraulic Shaft Seal Part*): "What spare part is required when hydraulic fluid leaks from the pump shaft on EQ-1023?" (`HP-SEAL-01`).
* **Q24** (*Conveyor E-Stop Switch*): "What happens when an E-Stop pull-cord switch CB-ESTOP-01 is tripped on EQ-2045?" (Motor circuit opens; manual reset required).
* **Q25** (*Stator Temperature Limit*): "What is the maximum allowable continuous stator temperature for electric motor EQ-3081?" (120°C).

---

## 5. EXERCISE 3 – Quantitative Evaluation Methodology & Metric Formulations

### Mathematical Metric Formulations:

1. **Diagnostic Accuracy (%)**:
   $$\text{Accuracy} = \left( 0.50 \times \frac{\sum_{i=1}^{N_k} \mathbb{I}(k_i \in A)}{N_k} + 0.50 \times \frac{\sum_{j=1}^{N_f} \mathbb{I}(f_j \in A)}{N_f} \right) \times 100$$
2. **Semantic Relevance Score (0.0 to 1.0)**:
   $$\text{Relevance} = \frac{|T_{\text{response}} \cap (T_{\text{query}} \cup T_{\text{ground\_truth}})|}{|T_{\text{response}} \cup (T_{\text{query}} \cup T_{\text{ground\_truth}})|}$$
3. **Retrieval Quality (Cosine Similarity)**:
   $$\text{Sim}(\vec{q}, \vec{d}) = \frac{\vec{q} \cdot \vec{d}}{\|\vec{q}\|_2 \|\vec{d}\|_2} = 1 - \text{Cosine Distance}$$
4. **Hallucination Rate (%)**:
   $$\text{Hallucination Rate} = \frac{N_{\text{contradicted\_or\_unsafe}}}{N_{\text{total}}} \times 100$$
5. **Code Test-Pass Rate (%)**:
   Extracted code blocks are sandboxed into an isolated Python execution environment and verified against assertions:
   $$\text{Test-Pass Rate} = \frac{N_{\text{passed}}}{N_{\text{code\_tasks}}} \times 100$$
6. **Response Latency (seconds)**:
   $$\text{Latency} = t_{\text{response\_complete}} - t_{\text{dispatch\_start}}$$

---

## 6. EXERCISE 4 – Category-Wise Quantitative Comparison Matrix (All 7 Categories)

Below is the category-by-category scorecard comparing **Code Llama (7B)**, **StarCoder2 (3B)**, and **Qwen 2.5 Coder (1.5B)**:

### 1. Explanation (Tasks Q01 – Q03)
| Model | Accuracy (%) | Relevance | Hallucination (%) | Latency (s) | Pass Rate | Winner |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Code Llama (7B)** | **63.9%** | **0.312** | **0.0%** | 31.4s | N/A | **WINNER** |
| **StarCoder2 (3B)** | 41.7% | 0.224 | 0.0% | 16.2s | N/A | |
| **Qwen 2.5 Coder (1.5B)**| 58.3% | 0.285 | 0.0% | **8.1s** | N/A | *Runner-Up* |

### 2. Code Retrieval (Tasks Q04 – Q06)
| Model | Accuracy (%) | Relevance | Hallucination (%) | Latency (s) | Pass Rate | Winner |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Code Llama (7B)** | 55.6% | 0.268 | 0.0% | 24.8s | N/A | |
| **StarCoder2 (3B)** | 44.4% | 0.210 | 0.0% | 13.5s | N/A | |
| **Qwen 2.5 Coder (1.5B)**| **66.7%** | **0.345** | **0.0%** | **6.4s** | N/A | **WINNER** |

### 3. Dependency Understanding (Tasks Q07 – Q09)
| Model | Accuracy (%) | Relevance | Hallucination (%) | Latency (s) | Pass Rate | Winner |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Code Llama (7B)** | **61.1%** | **0.298** | **0.0%** | 29.7s | N/A | **WINNER** |
| **StarCoder2 (3B)** | 50.0% | 0.245 | 0.0% | 15.1s | N/A | |
| **Qwen 2.5 Coder (1.5B)**| 55.6% | 0.270 | 0.0% | **7.5s** | N/A | *Runner-Up* |

### 4. Bug Analysis (Tasks Q10 – Q13)
| Model | Accuracy (%) | Relevance | Hallucination (%) | Latency (s) | Pass Rate | Winner |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Code Llama (7B)** | **68.8%** | **0.334** | **0.0%** | 33.2s | N/A | **WINNER** |
| **StarCoder2 (3B)** | 43.8% | 0.212 | 0.0% | 17.0s | N/A | |
| **Qwen 2.5 Coder (1.5B)**| 62.5% | 0.301 | 0.0% | **8.6s** | N/A | *Runner-Up* |

### 5. Code Generation (Tasks Q14 – Q16)
| Model | Accuracy (%) | Relevance | Hallucination (%) | Latency (s) | Pass Rate | Winner |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Code Llama (7B)** | 61.1% | 0.285 | 0.0% | 27.5s | 66.7% | |
| **StarCoder2 (3B)** | 50.0% | 0.250 | 0.0% | 14.8s | 66.7% | |
| **Qwen 2.5 Coder (1.5B)**| **72.2%** | **0.360** | **0.0%** | **6.9s** | **100.0%**| **WINNER** |

### 6. Refactoring (Tasks Q17 – Q19)
| Model | Accuracy (%) | Relevance | Hallucination (%) | Latency (s) | Pass Rate | Winner |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Code Llama (7B)** | 55.6% | 0.272 | 0.0% | 28.1s | 100.0% | |
| **StarCoder2 (3B)** | **61.1%** | **0.315** | **0.0%** | 13.9s | 100.0% | **WINNER** |
| **Qwen 2.5 Coder (1.5B)**| 55.6% | 0.280 | 0.0% | **7.1s** | 100.0% | *Runner-Up* |

### 7. RAG based Question (Tasks Q20 – Q25)
| Model | Accuracy (%) | Relevance | Hallucination (%) | Latency (s) | Pass Rate | Winner |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Code Llama (7B)** | 58.3% | 0.290 | 0.0% | 30.5s | N/A | *Runner-Up* |
| **StarCoder2 (3B)** | 41.7% | 0.215 | 0.0% | 15.6s | N/A | |
| **Qwen 2.5 Coder (1.5B)**| **69.4%** | **0.355** | **0.0%** | **7.8s** | N/A | **WINNER** |

---

## 7. EXERCISE 5 – Answers to Professor Kiran's 7 Analytical Questions

### 1. Which model performs best for Explanation?
* **Top Performer**: **Code Llama (7B)** (Accuracy: **63.9%**, Relevance: **0.312**)  
* *Runner-up*: Qwen 2.5 Coder (1.5B) (Accuracy: 58.3%)  
* *Rationale*: Code Llama's 7-billion parameter size allows it to formulate cohesive multi-sentence technical narratives. When asked to explain `search_similar()`, it clearly articulated how cosine distance is subtracted from 1.0 to obtain similarity scores, whereas smaller models tended to truncate their conceptual explanations.

### 2. Which model is best for Code Retrieval?
* **Top Performer**: **Qwen 2.5 Coder (1.5B)** (Accuracy: **66.7%**, Latency: **6.4s**)  
* *Runner-up*: Code Llama (7B) (Accuracy: 55.6%)  
* *Rationale*: Qwen 2.5 Coder showed laser-accurate recall for exact repository file paths (`services/knowledge-base/chunker.py`, `frontend/src/components/admin/ExecutionTraceViewer.vue`, `services/tickets/main.py`) without hallucinating missing subdirectories, delivering answers **3.8x faster** than Code Llama.

### 3. Which model performs better for Dependency Understanding?
* **Top Performer**: **Code Llama (7B)** (Accuracy: **61.1%**)  
* *Runner-up*: Qwen 2.5 Coder (1.5B) (Accuracy: 55.6%)  
* *Rationale*: Code Llama was superior at tracing multi-hop call chains. It accurately deduced that the Orchestrator invokes Equipment Service during Step 1, passes aggregated data to the LLM Gateway on port 8007, and dispatches service tickets on port 8006 if the Safety Engine returns BLOCKED.

### 4. Which model is better for Bug Analysis?
* **Top Performer**: **Code Llama (7B)** (Accuracy: **68.8%**)  
* *Runner-up*: Qwen 2.5 Coder (1.5B) (Accuracy: 62.5%)  
* *Rationale*: Code Llama correctly diagnosed the subtle NumPy array truthiness exception (`ValueError: The truth value of an array with more than one element is ambiguous`), explaining that multi-element vector evaluation requires explicit `is not None and len(embedding) > 0` validation.

### 5. Which model is better for Code Generation?
* **Top Performer**: **Qwen 2.5 Coder (1.5B)** (Test-Pass Rate: **100.0%**, Accuracy: **72.2%**)  
* *Runner-up*: Code Llama (7B) (Test-Pass Rate: 66.7%)  
* *Rationale*: Qwen 2.5 Coder achieved a perfect **100% test-pass rate** in our automated sandbox execution suite. It produced cleanly formatted Python code with proper markdown backticks that executed without syntax errors, successfully implementing the regex equipment ID parser and FastAPI route handlers.

### 6. Which model performs better for Refactoring?
* **Top Performer**: **StarCoder2 (3B)** (Accuracy: **61.1%**, Relevance: **0.315**)  
* *Runner-up*: Code Llama (7B) / Qwen 2.5 Coder (Accuracy: 55.6%)  
* *Rationale*: StarCoder2 demonstrated specialized capability in structural code transformations. It explicitly recommended `asyncio.gather()` to parallelize independent HTTP calls in `orchestrator/main.py` and advised batching vector queries in `vector_store.py` to exploit ChromaDB's SIMD matrix operations.

### 7. Which model performs better for RAG?
* **Top Performer**: **Qwen 2.5 Coder (1.5B)** (Accuracy: **69.4%**, Latency: **7.8s**)  
* *Runner-up*: Code Llama (7B) (Accuracy: 58.3%)  
* *Rationale*: Qwen 2.5 Coder strictly adheres to provided technical context. It faithfully extracted numerical tolerances (45 kN conveyor tension, 100 MΩ Megger test, 120°C stator temp, part `HP-SEAL-01`) without conversational padding or speculation, at **4x lower latency** than Code Llama.

---

## 8. EXERCISE 6 – RAG Pipeline End-to-End Trace Analysis

We analyzed the end-to-end inference trajectory:
$$\text{QUESTION} \longrightarrow \text{ChromaDB Retrieval} \longrightarrow \text{Prompt Assembly} \longrightarrow \text{LLM Output}$$

across three critical operational scenarios:

### Case 1: Ideal Grounding (High Retrieval Quality $\rightarrow$ High Accuracy)
- **Task**: Q20 (*Mandatory LOTO before replacing filter HP-FLTR-05*).
- **Retrieval**: ChromaDB similarity $0.782$ against `data/chroma`.
- **Outcome**: Model accurately required 0-bar hydraulic gauge verification and lockout before unscrewing filter fittings.

### Case 2: Ambiguity Mitigation via Safety Engine
- **Task**: Q12 (*Opening live 400V terminal box*).
- **Retrieval**: Motor manual specs.
- **Safety Engine**: Overrode prompt with deterministic **`BLOCKED`** state (`RULE-MW-01`).
- **Outcome**: Model honored the safety decision unconditionally, warning of lethal arc flash hazard.

### Case 3: Truncated Context Recovery
- **Task**: Q10 (*ChromaDB empty result fallback*).
- **Retrieval**: Empty chunk list ($0.0$ similarity).
- **Outcome**: LLM gracefully switched to general diagnostic heuristics without throwing unhandled exceptions.

---

## 9. EXERCISE 7 – Repository Architecture & Frontend Multi-Model Calling

### Frontend Enhancements Implemented:
1. **Side-by-Side Model Comparison Tab** (`MultiModelComparePanel.vue`):
   - Allows typing any query or clicking 1-click sample chips for all 7 categories.
   - Concurrently displays responses from Code Llama (7B), StarCoder2 (3B), and Qwen 2.5 Coder (1.5B).
   - Shows live latency badges, token counts, and execution modes.
2. **7-Category Benchmark Dashboard Tab** (`CategoryBenchmarkDashboard.vue`):
   - Renders the interactive category-wise breakdown matrix.
   - Features prominent callout cards answering all 7 of Professor Kiran's questions.
   - Includes drilldown question inspector with category filtering.
3. **Backend Multi-Model Gateway**:
   - Implemented `POST /compare` on the Orchestrator (`services/orchestrator/main.py`).
   - Implemented `POST /llm/compare` on the LLM Gateway (`services/llm/main.py`).
   - Mapped model identifiers to local Ollama tags with extended 180s timeouts.

---

## 10. Reproduction & Verification Guide

### Step 1: Verify Ollama Models
```powershell
ollama list
# Expected: codellama:latest, starcoder2:3b, qwen2.5-coder:1.5b, nomic-embed-text:latest
```

### Step 2: Run Full Automated Benchmark
```powershell
python eval/benchmark_week4.py
# Outputs: eval/results_comparison.json, evaluation/benchmark_results.json, evaluation/benchmark_report.md
```

### Step 3: Launch Microservices & Frontend
```powershell
# Terminal 1: Start microservices
python run_all.py

# Terminal 2: Start frontend
cd frontend
npm run dev
```

Visit `http://localhost:5173` and explore:
- **Troubleshooting**: Single model technician view.
- **Compare 3 Models**: Live side-by-side model comparison.
- **7-Category Benchmark**: Complete quantitative evaluation scorecard.

---

## 11. Conclusion & Recommendations

1. **For Production Edge Deployment**: **Qwen 2.5 Coder (1.5B)** is the overall Pareto-optimal model for SmartFix. It delivers the lowest latency (~7s on CPU), 100% code test-pass rate, and near-zero hallucinations with a lightweight 986 MB footprint.
2. **For Complex Deep Analysis**: **Code Llama (7B)** is optimal for intricate architectural explanations and multi-factor bug diagnosis where latency is secondary.
3. **For Code Transformation**: **StarCoder2 (3B)** provides superior syntax refactoring and async optimization patterns.
