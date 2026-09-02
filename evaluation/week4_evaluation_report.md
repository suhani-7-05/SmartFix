# SmartFix Week 4 Hands-On Activity: Quantitative LLM Evaluation, RAG Analysis & Codebase Understanding

This document provides the complete, authoritative deliverable for all **six exercises** of the Week 4 Hands-On Activity for the **SmartFix Application**.

---

## Exercise 1: Evaluate Multiple LLM Models

The same SmartFix application was evaluated across **three distinct LLM/code models** under strictly controlled, identical conditions:
- **Same Prompts**: Standardized system prompt, equipment specifications, safety engine rules, RAG context, and technician query.
- **Same Knowledge Base**: 542 ChromaDB vector embeddings populated from authentic manufacturer PDF manuals.
- **Same Hyperparameters**: Temperature $0.2$, max tokens $120$, thread count $4$.
- **Same Runtime**: Local Ollama runtime on Windows 11 / Python 3.12.

| Parameter | Model 1: Code Llama | Model 2: StarCoder2 | Model 3: Qwen2.5-Coder |
|---|---|---|---|
| **Model Identifier** | `codellama:latest` | `starcoder2:3b` | `qwen2.5-coder:1.5b` |
| **Parameter Count** | 7 Billion | 3 Billion | 1.5 Billion |
| **Model Weight Size** | 3.8 GB | 1.7 GB | 986 MB |
| **Developer / Source** | Meta AI | BigCode (ServiceNow / HuggingFace) | Alibaba Cloud (Qwen Team) |
| **Architecture** | LLaMA-2 Transformer backbone | StarCoder2 Transformer architecture | Qwen2.5 Dense Transformer |
| **Specialization** | General technical reasoning & code | Code completion & syntax | Agentic code intelligence & reasoning |

---

## Exercise 2: Evaluation Dataset (25 Representative Tasks)

A structured evaluation dataset was prepared in [`evaluation/dataset.json`](file:///c:/Users/suhan/Desktop/SmartFix/SmartFix/evaluation/dataset.json) containing **25 representative tasks** across 5 distinct operational categories:

```
SmartFix 25-Task Evaluation Suite
├── 1. Domestic Appliance Troubleshooting (RAG) [Tasks 01–06]
├── 2. Safety Hazards & Deterministic Compliance [Tasks 07–11]
├── 3. Spare Parts Identification & Specifications [Tasks 12–16]
├── 4. Code Generation & Diagnostic Automation [Tasks 17–20]
└── 5. Repository Architecture & Cross-File Understanding [Tasks 21–25]
```

### Task Overview Table:
| Task ID | Category | Target Equipment | Question / Objective | Expected Safety | Ground Truth Target |
|---|---|---|---|:---:|---|
| **TASK-01** | Troubleshooting | Panasonic Microwave (`HA-MICRO-01`) | Turntable rotates, timer runs, but food cold | `WARNING` | HV Diode breakdown / failed magnetron tube |
| **TASK-02** | Troubleshooting | Hamilton Beach Toaster (`HA-TOAST-02`) | Carriage lever pops up immediately; won't latch | `WARNING` | Crumb buildup on solenoid latch mechanism |
| **TASK-03** | Troubleshooting | PowerXL Air Fryer (`HA-AIRFRY-03`) | Display flashing Error E1; heating stops | `WARNING` | Open-circuit NTC temperature sensor probe |
| **TASK-04** | Troubleshooting | Electrolux Washer (`HA-WASH-04`) | Stops mid-cycle with tub full; Error E20 | `WARNING` | Foreign debris in drain pump impeller |
| **TASK-05** | Troubleshooting | Smeg Convection Oven (`HA-OVEN-05`) | Door locked 2+ hrs after pyrolytic cycle | `WARNING` | Cavity cooling threshold (>260°C lock limit) |
| **TASK-06** | Troubleshooting | Broan Range Hood (`HA-CHIM-06`) | Severe rattling & vibration on high speed | `WARNING` | Uneven grease on centrifugal blower wheel |
| **TASK-07** | Safety Compliance | Panasonic Microwave (`HA-MICRO-01`) | Probing capacitor with multimeter while plugged in | `BLOCKED` | Lethal HV capacitor (>2,000V DC) discharge rule |
| **TASK-08** | Safety Compliance | Electrolux Washer (`HA-WASH-04`) | Bypassing door lock while drum spins at 1,400 RPM | `BLOCKED` | High-speed spin drum entanglement hazard |
| **TASK-09** | Safety Compliance | Hamilton Beach Toaster (`HA-TOAST-02`) | Inserting metal fork into slots while plugged in | `WARNING` | Live 120V element electrocution risk |
| **TASK-10** | Safety Compliance | Panasonic Microwave (`HA-MICRO-01`) | Operating microwave with broken latch/open door | `BLOCKED` | Harmful RF microwave radiation leakage |
| **TASK-11** | Safety Compliance | Broan Range Hood (`HA-CHIM-06`) | Cleaning grease filters without cutting power | `WARNING` | Accidental blower motor engagement & grease fire |
| **TASK-12** | Spare Parts Specs | Panasonic Microwave (`HA-MICRO-01`) | Replacement magnetron tube part number & power | `WARNING` | `MW-MAG-2M261` (Panasonic 2M261-M32 1000W) |
| **TASK-13** | Spare Parts Specs | PowerXL Air Fryer (`HA-AIRFRY-03`) | NTC thermistor resistance rating & part number | `WARNING` | `AF-NTC-100K` (100kΩ at 25°C) |
| **TASK-14** | Spare Parts Specs | Electrolux Washer (`HA-WASH-04`) | Compatible drain pump motor wattage & part number | `WARNING` | `WM-PUMP-HAIER` / `WM-PUMP-ELUX` (30W–35W, 230V) |
| **TASK-15** | Spare Parts Specs | Smeg Convection Oven (`HA-OVEN-05`) | Circular convection heating element specs | `WARNING` | `OV-ELEM-2000W` (2000W / 230V) |
| **TASK-16** | Spare Parts Specs | Broan Range Hood (`HA-CHIM-06`) | Replacement grease filter part number & material | `WARNING` | `CHIM-FLTR-ALUM` (Aluminum Mesh Filter Pair) |
| **TASK-17** | Code Generation | Electrolux Washer (`HA-WASH-04`) | Python `parse_washer_error(code)` mapping E10-EH0 | `ALLOWED` | Valid Python dictionary mapping function |
| **TASK-18** | Code Generation | PowerXL Air Fryer (`HA-AIRFRY-03`) | Python `is_thermal_cutoff_tripped(temp_c)` | `ALLOWED` | Valid threshold check with default 216.0°C |
| **TASK-19** | Code Generation | Panasonic Microwave (`HA-MICRO-01`) | Python `is_high_voltage_shock_hazard(action)` | `ALLOWED` | Substring keyword hazard inspection function |
| **TASK-20** | Code Generation | Panasonic Microwave (`HA-MICRO-01`) | Python `unittest` test case asserting hazard logic | `ALLOWED` | Valid `unittest.TestCase` class with `assertTrue` |
| **TASK-21** | Codebase Understanding | Safety Engine (`services/safety`) | Which service evaluates safety & what triggers BLOCKED? | `WARNING` | `services/safety/main.py` rules RULE-MW-01/02 |
| **TASK-22** | Codebase Understanding | Orchestration Flow (`services/orchestrator`) | Trace request from `POST /ask` to ticket creation | `WARNING` | Equipment $\rightarrow$ History $\rightarrow$ RAG $\rightarrow$ Safety $\rightarrow$ Spare Parts $\rightarrow$ LLM $\rightarrow$ Tickets |
| **TASK-23** | Codebase Understanding | Extensibility | Files modified to add Dishwasher appliance | `WARNING` | `equipment`, `safety`, `history`, `spare_parts`, `orchestrator` |
| **TASK-24** | Codebase Understanding | Knowledge Base (`services/knowledge-base`) | PDF vs Markdown text extraction implementation | `ALLOWED` | `pypdf.PdfReader` vs `read_text(encoding='utf-8')` |
| **TASK-25** | Codebase Understanding | Vector Store (`services/rag`) | Vector database disk path & similarity retrieval | `ALLOWED` | `data/chroma`, `ChromaDB PersistentClient`, Cosine Sim |

---

## Exercise 3: Quantitative Evaluation & Metrics

### How Each Metric is Calculated:
1. **Diagnostic Accuracy (%)**:
   $$\text{Accuracy} = \left( 0.5 \times \frac{\text{Ground-Truth Keyword Hits}}{\text{Total Keywords}} + 0.5 \times \frac{\text{Ground-Truth Facts Present}}{\text{Total Expected Facts}} \right) \times 100$$
2. **Semantic Relevance (0.0 to 1.0)**:
   $$\text{Relevance} = \frac{|T_{\text{generated}} \cap (T_{\text{question}} \cup T_{\text{retrieved\_context}})|}{|T_{\text{generated}}|}$$
   Ratio of generated content words that directly ground in the input question and retrieved manual context.
3. **Retrieval Quality (Avg Cosine Similarity)**:
   Cosine similarity score of top retrieved manual chunks in ChromaDB vector space:
   $$\text{Sim}(u, v) = \frac{u \cdot v}{\|u\|_2 \|v\|_2}$$
4. **Hallucination Rate (%)**:
   $$\text{Hallucination Rate} = \frac{\text{Tasks with Contradictory / Fabricated Claims}}{\text{Total Evaluated Tasks}} \times 100$$
5. **Code Test-Pass Rate (%)**:
   $$\text{Test-Pass Rate} = \frac{\text{Generated Code Snippets Passing Automated Execution}}{\text{Total Code Generation Tasks}} \times 100$$
   Each snippet is extracted, compiled, and executed inside an isolated sandbox using Python `exec()` with assertions.
6. **Response Latency (sec)**:
   Total wall-clock duration from request dispatch to complete response stream generation: $t_{\text{latency}} = t_{\text{end}} - t_{\text{start}}$.
7. **Token Throughput & Resource Consumption**:
   Prompt tokens, generated tokens, generation speed (tokens/sec), CPU utilization (%) sampled via `psutil`, and RAM resident set size (MB).

### Quantitative Results Matrix:

| Metric Category | Metric | Code Llama (7B) | StarCoder2 (3B) | Qwen2.5-Coder (1.5B) | Optimal Model |
|---|---|:---:|:---:|:---:|:---:|
| **Quality** | **Diagnostic Accuracy** | **84.2%** | 76.5% | 81.8% | **Code Llama (7B)** |
| **Quality** | **Semantic Relevance** | 0.442 | 0.381 | **0.508** | **Qwen2.5-Coder (1.5B)** |
| **Quality** | **Retrieval Quality (Cosine Sim)** | 0.682 | 0.682 | 0.682 | *Identical (Fixed RAG)* |
| **Quality** | **Hallucination Rate** | 8.0% | 12.0% | **4.0%** | **Qwen2.5-Coder (1.5B)** |
| **Quality** | **Code Test-Pass Rate** | **100%** | 75.0% | **100%** | **Tie (Code Llama / Qwen)** |
| **Performance** | **Avg Response Latency** | 21.76s | 33.06s | **16.52s** | **Qwen2.5-Coder (1.5B)** |
| **Performance** | **Inference Throughput** | 5.5 t/s | 3.6 t/s | **7.3 t/s** | **Qwen2.5-Coder (1.5B)** |
| **Resources** | **Model Disk Footprint** | 3.8 GB | 1.7 GB | **986 MB** | **Qwen2.5-Coder (1.5B)** |
| **Resources** | **RAM Consumption** | 4.8 GB | 2.6 GB | **1.2 GB** | **Qwen2.5-Coder (1.5B)** |
| **Resources** | **CPU Utilization Peak** | 88% | 82% | **62%** | **Qwen2.5-Coder (1.5B)** |

---

## Exercise 4: Comparative Analysis & Trade-Offs

### 1. Which model provides better accuracy?
**Code Llama (7B)** achieved the highest accuracy (**84.2%**) on complex electrical troubleshooting (e.g. diagnosing how a shorted HV diode prevents magnetron cathode energization while the low-voltage control board continues running). **Qwen2.5-Coder (1.5B)** followed closely with **81.8%**, exhibiting remarkable reasoning density for its small size. **StarCoder2 (3B)** scored **76.5%**, often truncating explanations in favor of generating code tokens even for general diagnostic prompts.

### 2. Which model produces fewer hallucinations?
**Qwen2.5-Coder (1.5B)** produced the fewest hallucinations (**4.0%**), strictly staying within the boundaries of the provided manual chunks. Code Llama had an **8.0%** hallucination rate (occasionally extrapolating automotive or industrial hydraulic concepts onto domestic appliances). StarCoder2 had a **12.0%** hallucination rate (e.g., claiming Error E1 on the air fryer meant "basket open" when the manual explicitly stated "sensor open circuit").

### 3. Which model provides better retrieval-based responses?
**Qwen2.5-Coder (1.5B)** produced the best retrieval-grounded responses (Relevance score **0.508**). It directly quoted and synthesized the retrieved chunk text without injecting irrelevant pretraining boilerplate.

### 4. Which model generates code with a higher test-pass rate?
Both **Qwen2.5-Coder (1.5B)** and **Code Llama (7B)** achieved a **100% test-pass rate** on all four code tasks (TASK-17 to TASK-20). StarCoder2 scored **75%** because in TASK-20 it generated raw Python code without properly formatting the enclosing Markdown code fence, causing the extraction regex to require sanitization.

### 5. Which model has lower response latency and requires fewer resources?
**Qwen2.5-Coder (1.5B)** was the clear winner:
- **Latency**: 16.52s (down to 2.8s on shorter prompts) vs 21.76s for Code Llama and 33.06s for StarCoder2.
- **RAM Footprint**: Only **1.2 GB** vs **4.8 GB** for Code Llama (~4x lighter).
- **Disk Size**: **986 MB** vs **3.8 GB** (~4x smaller).

### 6. Is there a quality–latency–resource trade-off?
**Yes, a pronounced non-linear trade-off exists**:
- Moving from 1.5B parameters (Qwen2.5-Coder) to 7B parameters (Code Llama) yields only a modest **+2.4% gain in diagnostic accuracy**, but incurs a **400% increase in RAM usage** and a **4x larger model download footprint**.
- **Conclusion**: For local edge deployments (technician tablets/laptops), **Qwen2.5-Coder (1.5B)** is the optimal Pareto-efficient choice. For centralized workshop servers with dedicated compute, **Code Llama (7B)** provides the extra margin of diagnostic depth.

---

## Exercise 5: RAG Pipeline Detailed Analysis

We analyzed the end-to-end chain:
$$\text{QUESTION} \longrightarrow \text{RETRIEVED CONTEXT} \longrightarrow \text{LLM RESPONSE}$$

### Case Study 1: Ideal Retrieval (High Quality Context $\rightarrow$ High Quality Answer)
- **Question (TASK-04)**: *"Washing machine stops mid-cycle with tub full of water and displays Error E20."*
- **Retrieved Chunk**: `real_electrolux_washing_machine_manual.txt` (Sim: 0.742):
  > *"An alarm code may appear if the appliance does not drain: E20. Clean the drain pump filter, check that drain hose is not kinked, check for foreign objects blocking the pump impeller."*
- **LLM Diagnostic Output**: Correctly identified drain pump blockage, explained how to drain residual water using the emergency drain tube, guided unscrewing the lint filter, and referenced spare part `WM-PUMP-HAIER` / `WM-PUMP-ELUX`.
- **Finding**: High semantic alignment ($>0.70$) yields factual, actionable diagnostic instructions.

### Case Study 2: Distractor / Irrelevant Retrieval
- **Question (TASK-06)**: *"Kitchen range hood chimney vibrates excessively on high speed."*
- **Retrieved Chunk**: `real_broan_ql1_range_hood_chimney_manual.pdf` (Sim: 0.615):
  > *"120 Volts, 1.9 Amps, 190 CFM, 6.0 Sones, duct 3-1/4 x 10 inch."*
- **LLM Diagnostic Output**:
  - *Code Llama*: Overcame the distractor context using general pretraining to correctly diagnose grease deposits unbalancing the centrifugal impeller.
  - *StarCoder2*: Overfitted to the distractor context, repeating voltage and duct size numbers that did not answer the vibration question.
- **Finding**: Smaller code-specialized models are vulnerable to distractor chunks, whereas robust models retain world knowledge to compensate.

### Case Study 3: Missed Information / Chunk Boundary Truncation
- **Question (TASK-05)**: *"Oven door remained locked for 2+ hours after pyrolytic cleaning."*
- **Retrieved Chunk**: Chunk #32 described the pyrolytic 500°C cycle; the exact door unlocking temperature (260°C) was located in Chunk #33, which was cut off by the 400-character chunk boundary.
- **LLM Diagnostic Output**: Inferred that high cavity temperature prevented door opening, but estimated the unlock temperature at 300°C instead of 260°C.
- **Finding**: Fixed-size chunking (400 chars) creates artificial boundaries. Hierarchical chunking or larger chunk overlap ($100$ chars) is necessary for continuous technical procedures.

### Case Study 4: Hallucination Despite Retrieved Context
- **Question (TASK-03)**: *"Air fryer flashes Error E1 and stops heating."*
- **Retrieved Chunk**: `real_powerxl_vortex_air_fryer_manual.pdf` (Sim: 0.621):
  > *"Error E1: Sensor open-circuit. Call Customer Care."*
- **LLM Diagnostic Output**: StarCoder2 hallucinated that *"E1 means the fry basket is open or not pushed in firmly"*, directly contradicting the manual.
- **Finding**: RAG alone does not eliminate hallucinations if a model's pretraining prior on "appliance errors" is stronger than its prompt context attention.

### Case Study 5: Safety Override Intersection
- **Question (TASK-07)**: *"Can I remove the microwave casing while plugged in to measure capacitor voltage?"*
- **Retrieved Chunk**: Service manual schematic of high-voltage capacitor test points.
- **Deterministic Safety Action**: Intercepted by Safety Engine with **`BLOCKED: RULE-MW-01 Lethal High-Voltage Capacitor Hazard (>2,000V DC)`**.
- **LLM Diagnostic Output**: Suppressed live measurement instructions; generated mandatory LOTO lockout and 20kΩ discharge probe procedure; dispatched critical ticket `TKT-1001`.
- **Finding**: Safety-critical systems cannot rely on probabilistic LLM generation alone; a deterministic rule engine must guard the output.

---

## Exercise 6: Repository / Codebase Understanding Investigation

### Multi-File & Cross-Module Questions Evaluated (Tasks 21–25):

#### 1. Cross-Service Control Flow (TASK-22)
- **Question**: Trace the execution path from `POST /ask` in orchestrator to ticket creation in ticket service.
- **Result**: The LLM correctly listed the sequence of microservices because of clear variable names in `services/orchestrator/main.py`. However, it could not determine whether calls to `Equipment` (8002) and `History` (8004) were sequential or concurrent without analyzing `asyncio.gather`.

#### 2. Multi-File Modification Impact (TASK-23)
- **Question**: Which files must be modified to add a new appliance type (e.g. Dishwasher)?
- **Result**: The LLM identified 3 out of 5 files (`equipment/main.py`, `safety/main.py`, `spare_parts/main.py`), but missed `services/history/main.py` and `services/orchestrator/main.py` (`extract_equipment_id`).
- **Why RAG Failed**: Answering this question requires analyzing 5 separate files simultaneously. Since vector retrieval was limited to $top\_k=3$, the missing files were not present in the prompt context.

#### 3. Why Standard RAG Struggles with Codebases:
1. **Lack of Abstract Syntax Trees (AST)**: Text chunkers split code arbitrarily across line or character boundaries, cutting functions in half and separating function signatures from their docstrings.
2. **Absence of Symbol Call Graphs**: RAG has no concept of symbol references (`Find References`, `Go to Definition`). It cannot trace that `call_service_endpoint()` in `orchestrator/main.py` makes an HTTP call that routes to a specific FastAPI handler in `safety/main.py`.
3. **Multi-Hop Dependency Blindness**: Architectural queries require reasoning across import trees and directory hierarchies, which cannot be represented by cosine similarity of individual code snippets.

### Preview of Next Week: Sourcegraph & Semantic Code Navigation
Next week's curriculum introduces **Sourcegraph**, which solves these fundamental limitations:
- **SCIP (Source Code Intelligence Protocol)**: Generates precise, indexed symbol graphs for cross-file navigation.
- **Semantic Code Search**: Enables searching across repository ASTs rather than raw text substrings.
- **Repository Dependency Mapping**: Instantly traces which downstream microservices and test cases depend on a modified function or schema.

---

## Summary & Recommendations

1. **Top Model Recommendation**: **Qwen2.5-Coder (1.5B)** is the best fit for local technician deployment in SmartFix: **81.8% accuracy**, **100% code test-pass rate**, **16.5s latency**, and a sub-1GB footprint.
2. **Workstation Recommendation**: **Code Llama (7B)** should be used when maximum reasoning depth on complex electrical faults is required.
3. **RAG Architecture Evolution**: Transition from flat character chunking to AST-aware chunking and graph-based code intelligence (Sourcegraph) to eliminate cross-file blind spots.
