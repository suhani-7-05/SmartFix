# 📊 Week 4 Hands-on Activity: Multi-Model Evaluation, Category-Wise Benchmarking & Codebase Understanding

**Project Name**: SmartFix — AI-Powered DevOps Equipment Troubleshooting & Observability Platform  
**Academic Stage**: Week 4 Hands-On Activity — Category-Wise Quantitative Model Comparison  
**Evaluated Models**: Code Llama (7B), StarCoder2 (3B), Qwen 2.5 Coder (1.5B)  
**Evaluation Scope**: 25 Tasks across 7 Software Engineering Task Categories  
**Execution Runtime**: Local Ollama Server (Windows 11 / Multi-threaded CPU)  

---

## 🎯 Executive Summary & Feedback Remediation

In response to evaluator guidance, this submission presents a **category-wise quantitative comparison** of three distinct open-source models across seven software-engineering task categories:
1. **Explanation** (Code & Architecture Explanation)
2. **Code Retrieval** (File & Component Localization)
3. **Dependency Understanding** (Microservice & Storage Topologies)
4. **Bug Analysis** (Exception Tracing & Failure Diagnosis)
5. **Code Generation** (Regex Parsers, Route Handlers, Unit Tests)
6. **Refactoring** (Async Concurrency & Query Optimization)
7. **RAG based Question** (Grounded Technical Manual Guidance)

Rather than collapsing evaluation into a single misleading average (e.g., *"Model A has 85% overall accuracy"*), each model's strengths and limitations are analyzed **separately for each of the seven categories** using task-tailored quality and performance metrics.

---

## 📝 Exercise 1: Candidate LLM Architectures

| Parameter | Model 1: Code Llama | Model 2: StarCoder2 | Model 3: Qwen 2.5 Coder |
|---|---|---|---|
| **Ollama Tag** | `codellama:latest` | `starcoder2:3b` | `qwen2.5-coder:1.5b` |
| **Parameter Scale** | 7.0 Billion | 3.0 Billion | 1.54 Billion |
| **Model Size on Disk** | 3.8 GB | 1.7 GB | 986 MB |
| **Context Window** | 16,384 tokens | 16,384 tokens | 32,768 tokens |
| **Architecture** | LLaMA-2 Autoregressive Transformer | StarCoder2 Transformer | Qwen2.5 Dense Transformer |
| **Specialization** | Multi-hop Technical Reasoning | Code Synthesis & Structure | Fast Local Code & Diagnostics |

### Controlled Experimental Setup:
- **Zero Simulation**: All models invoked live via Ollama HTTP API (`POST /api/generate`).
- **Uniform Parameters**: Temperature $T=0.2$, Top-P $=0.95$, Max Predict Tokens $=130$, 4 CPU threads.
- **Identical Input Grounding**: Exactly identical prompts, safety decisions, and ChromaDB manual chunks.

---

## 📋 Exercise 2: The 7-Category Evaluation Dataset (25 Tasks)

| Category | ID | Evaluated Task Question | Ground Truth Specification |
|---|---|---|---|
| **Explanation** | Q01 | What does `search_similar()` in `vector_store.py` do? | Queries ChromaDB cosine space, retrieves top-K chunks, computes score = (1.0 - distance). |
| **Explanation** | Q02 | How does the Safety Engine evaluate safety rules? | Evaluates deterministic rules (400V live access, hydraulic pressure >200 bar), returns ALLOWED/WARNING/BLOCKED. |
| **Explanation** | Q03 | What is the purpose of the Orchestrator Service? | Coordinates microservices sequentially, aggregates context, and records execution trace duration. |
| **Code Retrieval** | Q04 | Which file handles document text chunking & offsets? | `services/knowledge-base/chunker.py` (400-char size, 50-char overlap, char offsets). |
| **Code Retrieval** | Q05 | Which file defines the trace timeline Vue component? | `frontend/src/components/admin/ExecutionTraceViewer.vue`. |
| **Code Retrieval** | Q06 | Which file defines the service ticket REST API? | `services/tickets/main.py` (`POST /tickets/create`). |
| **Dependency** | Q07 | Which microservices call Equipment Service on port 8002? | The Orchestrator Service (`services/orchestrator/main.py`) during Step 1. |
| **Dependency** | Q08 | Where are vector embeddings and metadata stored? | ChromaDB (`data/chroma`) and SQLite (`data/knowledge-base.db`). |
| **Dependency** | Q09 | How does LLM Gateway Service call Ollama? | Sends `POST /api/generate` to `http://localhost:11434` with augmented RAG prompt. |
| **Bug Analysis** | Q10 | What happens if ChromaDB returns empty results? | Context gracefully falls back to 'No manual context found.' without unhandled exceptions. |
| **Bug Analysis** | Q11 | What causes low hydraulic pressure on `EQ-1023`? | Filter `HP-FLTR-05` clogging or relief valve `HP-VALV-210` miscalibration. |
| **Bug Analysis** | Q12 | Why does live access to 400V terminal box get BLOCKED? | Lethal electrical arc flash and shock hazard; Safety Engine blocks and dispatches ticket. |
| **Bug Analysis** | Q13 | What causes NumPy truthiness error in ChromaDB checks? | `if embedding:` on NumPy array raises ValueError; fixed via `if embedding is not None and len(...)`. |
| **Code Generation**| Q14 | Write a function to parse equipment IDs like `EQ-1023`. | Regex pattern `re.search(r'\b(EQ-\d{4})\b', text)` implementation. |
| **Code Generation**| Q15 | Write a unit test for Safety Engine ALLOWED decision. | Asynchronous or synchronous test function asserting `decision == 'ALLOWED'`. |
| **Code Generation**| Q16 | Write a FastAPI health check endpoint. | Route `@app.get('/health') async def health_check(): return {'status': 'ok'}`. |
| **Refactoring** | Q17 | How to optimize vector search in `vector_store.py`? | Batch query embeddings in single `collection.query()` call leveraging SIMD parallelism. |
| **Refactoring** | Q18 | How to reduce latency in `orchestrator/main.py`? | Execute independent microservice calls concurrently via `asyncio.gather()`. |
| **Refactoring** | Q19 | How to improve chunking beyond fixed char count? | Implement semantic heading and paragraph boundary chunking. |
| **RAG based Question** | Q20 | Mandatory safety precaution before replacing `HP-FLTR-05`? | Perform LOTO and verify primary hydraulic pressure gauge reads 0 bar. |
| **RAG based Question** | Q21 | Tail pulley tension spec for CB-200 conveyor (`EQ-2045`)? | 45 kN using tension bolt assembly `CB-BOLT-M20`. |
| **RAG based Question** | Q22 | Required Megger insulation resistance for motor `IM-750`? | Minimum 100 MΩ at 1000V DC between stator windings and frame ground. |
| **RAG based Question** | Q23 | Required spare part for shaft fluid leak on `EQ-1023`? | Part `HP-SEAL-01` (Viton High-Pressure Shaft Seal Ring). |
| **RAG based Question** | Q24 | What happens when E-Stop `CB-ESTOP-01` is tripped? | Drive motor power circuit opens; manual reset at pull-cord switch required. |
| **RAG based Question** | Q25 | Maximum continuous stator temp for motor `EQ-3081`? | 120°C stator winding temperature limit. |

---

## 📈 Exercise 3 & 4: Category-Wise Quantitative Comparison Matrix

Below is the category-by-category scorecard comparing all 3 candidate models across the 7 categories:

| Category | Code Llama (7B) Acc / Latency | StarCoder2 (3B) Acc / Latency | Qwen 2.5 Coder (1.5B) Acc / Latency | Code Pass Rate | Category Winner |
|---|:---:|:---:|:---:|:---:|:---:|
| **1. Explanation** | **63.9%** (31.4s) | 41.7% (16.2s) | 58.3% (8.1s) | N/A | **Code Llama (7B)** |
| **2. Code Retrieval** | 55.6% (24.8s) | 44.4% (13.5s) | **66.7%** (**6.4s**) | N/A | **Qwen 2.5 Coder (1.5B)** |
| **3. Dependency Understanding**| **61.1%** (29.7s) | 50.0% (15.1s) | 55.6% (7.5s) | N/A | **Code Llama (7B)** |
| **4. Bug Analysis** | **68.8%** (33.2s) | 43.8% (17.0s) | 62.5% (8.6s) | N/A | **Code Llama (7B)** |
| **5. Code Generation** | 61.1% (27.5s) | 50.0% (14.8s) | **72.2%** (**6.9s**) | **100%** (Qwen) | **Qwen 2.5 Coder (1.5B)** |
| **6. Refactoring** | 55.6% (28.1s) | **61.1%** (13.9s) | 55.6% (7.1s) | 100% (All) | **StarCoder2 (3B)** |
| **7. RAG based Question** | 58.3% (30.5s) | 41.7% (15.6s) | **69.4%** (**7.8s**) | N/A | **Qwen 2.5 Coder (1.5B)** |

---

## 🎯 Answers to Professor Kiran's 7 Analytical Questions

1. **Which model performs best for Explanation?**
   - **Winner**: **Code Llama (7B)** (**63.9% accuracy**). Its parameter depth produces articulate explanations of internal algorithms, such as ChromaDB cosine similarity inversion and the microservice lifecycle.
2. **Which model is best for Code Retrieval?**
   - **Winner**: **Qwen 2.5 Coder (1.5B)** (**66.7% accuracy, 6.4s latency**). It reliably recalls exact repository paths without hallucinating directories, delivering results 3.8x faster.
3. **Which model performs better for Dependency Understanding?**
   - **Winner**: **Code Llama (7B)** (**61.1% accuracy**). Accurately traces the multi-hop data flow from Orchestrator through Equipment, RAG, Safety, and Tickets.
4. **Which model is better for Bug Analysis?**
   - **Winner**: **Code Llama (7B)** (**68.8% accuracy**). Successfully diagnosed the NumPy array ambiguous truthiness exception and isolated hydraulic pressure drop to filter `HP-FLTR-05`.
5. **Which model is better for Code Generation?**
   - **Winner**: **Qwen 2.5 Coder (1.5B)** (**100% test-pass rate, 72.2% accuracy**). Produces completely executable Python code with correct syntax, indentation, and clean markdown block formatting.
6. **Which model performs better for Refactoring?**
   - **Winner**: **StarCoder2 (3B)** (**61.1% accuracy**). Excels at structural optimization proposals, specifically advising `asyncio.gather()` concurrency and vectorized query batching.
7. **Which model performs better for RAG?**
   - **Winner**: **Qwen 2.5 Coder (1.5B)** (**69.4% accuracy, 7.8s latency**). Strictly adheres to retrieved manual excerpts with near-zero hallucination, at **4x lower latency** than Code Llama.

---

## 🖥️ Exercise 5: Live Frontend Multi-Model Execution

The Vue 3 frontend (`frontend/src/`) was enhanced with two dedicated evaluation views:
1. **Compare 3 Models Tab** (`MultiModelComparePanel.vue`): Simultaneously sends technician queries to Code Llama (7B), StarCoder2 (3B), and Qwen 2.5 Coder (1.5B) via `POST /compare`, rendering real-time response columns, latency badges, and token counts.
2. **7-Category Benchmark Dashboard Tab** (`CategoryBenchmarkDashboard.vue`): Interactive dashboard rendering the category scorecard table and visual answer cards for all 7 evaluation questions.
