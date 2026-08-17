# SmartFix — AI-Powered DevOps Equipment Troubleshooting Platform

SmartFix is an AI-powered equipment troubleshooting and maintenance platform designed for DevOps environments.

It provides two tailored interfaces:
1. **Technician Interface**: A clean, intuitive troubleshooting dashboard showing diagnosis, recommended actions, safety precautions, spare-part availability, and automated service tickets.
2. **Admin AI/DevOps Observability Dashboard**: A comprehensive observability dashboard exposing real step-by-step orchestrator execution traces, RAG vector similarity search, query embeddings, retrieved context, deterministic safety rules, equipment metadata, maintenance history, spare parts inventory, and LLM gateway metrics.

---

## Architecture Diagram

```text
                               +----------------------------------+
                               |     Vue 3 + Vite Frontend        |
                               |  (Technician UI & Admin UI)      |
                               +-----------------+----------------+
                                                 |
                                                 v
                               +----------------------------------+
                               |    Orchestrator Service (:8000)   |
                               |    Coordinates Microservices     |
                               +-----------------+----------------+
                                                 |
        +------------------+------------------+--+-------------------+------------------+
        |                  |                  |                      |                  |
        v                  v                  v                      v                  v
+---------------+  +---------------+  +---------------+      +---------------+  +---------------+
| Equipment Svc |  |  History Svc  |  |  RAG Service  |      | Safety Engine |  |Spare Parts Svc|
|    (:8002)    |  |    (:8004)    |  |    (:8001)    |      |    (:8003)    |  |    (:8005)    |
+---------------+  +---------------+  +-------+-------+      +---------------+  +---------------+
                                              |
                                              v
                                    +-------------------+
                                    | ChromaDB + SQLite |
                                    | (Local Vector DB) |
                                    +-------------------+
                                              |
        +-------------------------------------+-------------------------------------+
        |                                                                           |
        v                                                                           v
+---------------+                                                           +---------------+
| Ticket Svc    |                                                           | LLM Svc       |
|    (:8006)    |                                                           |    (:8007)    |
+---------------+                                                           +-------+-------+
                                                                                    |
                                                                                    v
                                                                            +---------------+
                                                                            | Local Ollama  |
                                                                            |  Code Llama   |
                                                                            +---------------+
```

---

## Exercise Progression

- **Exercise 1 — Basic LLM Application**: Vue 3 + Vite frontend, FastAPI backend, Ollama + Code Llama integration, execution-flow visualization.
- **Exercise 2 — Technical Knowledge Base & Vector DB**: Technical manual ingestion (`.txt`, `.md`, `.pdf`), text extraction (`pypdf`), fixed-size overlapping chunking, Ollama embeddings (`nomic-embed-text`), SQLite metadata tracking, and ChromaDB persistent vector storage.
- **Exercise 3 — RAG Pipeline**: Question → Query Embedding → Vector Similarity Search → Top-K Relevant Chunks → Context Construction → Code Llama Answer Synthesis. RAG retrieval & similarity score observability.
- **Exercise 4 — Microservices & Orchestrator**: Decoupled microservices architecture across 8 API services with a deterministic Safety Engine (`ALLOWED`, `WARNING`, `BLOCKED`) and real step-by-step orchestrator execution traces.
- **Exercise 5 — Containerization with Docker**: Containerized microservices, Nginx frontend, multi-stage Dockerfiles, and `docker-compose.yml` orchestration.

---

## Microservices API Reference

| Service | Port | Key Endpoints | Description |
|---|---|---|---|
| **Orchestrator** | 8000 | `POST /ask`, `POST /orchestrate` | Coordinates microservices, returns answer & real execution trace |
| **RAG Service** | 8001 | `POST /rag/retrieve`, `POST /documents/upload`, `GET /vectors/{id}` | Manages technical manuals, embeddings, and vector search |
| **Equipment Service** | 8002 | `GET /equipment/{id}` | Returns structured machinery specifications by Equipment ID (`EQ-1023`, `EQ-2045`, `EQ-3081`) |
| **Safety Engine** | 8003 | `POST /safety/evaluate` | Deterministic safety evaluator returning `ALLOWED`, `WARNING`, or `BLOCKED` |
| **History Service** | 8004 | `GET /history/{id}` | Returns historical maintenance events and past failure logs |
| **Spare Parts Service** | 8005 | `GET /spare-parts/{id}` | Returns compatible spare parts inventory & stock availability |
| **Ticket Service** | 8006 | `POST /tickets/create`, `GET /tickets` | Generates & tracks field technician dispatch tickets (`TKT-XXXX`) |
| **LLM Gateway** | 8007 | `POST /llm/generate` | Interfaces with Ollama + Code Llama to synthesize natural language diagnosis |

---

## Running the Application

### Method A: Local Microservices (Development)

1. **Activate Virtual Environment & Install Dependencies**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r services/knowledge-base/requirements.txt
   ```

2. **Ingest Technical Manuals into ChromaDB**:
   ```bash
   python ingest_manuals.py
   ```

3. **Start Local Ollama (Optional for local LLM & Embeddings)**:
   ```bash
   ollama serve
   ollama pull codellama
   ollama pull nomic-embed-text
   ```

4. **Start Microservices**:
   ```bash
   uvicorn services.orchestrator.main:app --port 8000 &
   uvicorn services.rag.main:app --port 8001 &
   uvicorn services.equipment.main:app --port 8002 &
   uvicorn services.safety.main:app --port 8003 &
   uvicorn services.history.main:app --port 8004 &
   uvicorn services.spare_parts.main:app --port 8005 &
   uvicorn services.tickets.main:app --port 8006 &
   uvicorn services.llm.main:app --port 8007 &
   ```

5. **Start Vue 3 Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Open `http://127.0.0.1:5173` in your browser.

---

### Method B: Docker & Docker Compose

1. **Build and Launch Containerized Services**:
   ```bash
   docker-compose up --build
   ```

2. Open `http://localhost:5173` for the Vue 3 Frontend.

---

## Data Sources & Documentation

- **Technical Manuals**: Public/open maintenance specs for industrial hydraulic pressure pumps (`HP-5000`), conveyor belt systems (`CB-200`), and 3-phase electric motors (`IM-750`) stored in `data/documents/uploads/`.
- **Synthetic Project Data**: Project-specific structured equipment records (`EQ-1023`, `EQ-2045`, `EQ-3081`), failure logs, spare part inventory numbers (`HP-FLTR-05`, `HP-SEAL-01`), and ticket records (`TKT-1001`).

---

## License

MIT — see [LICENSE](LICENSE).
