# SmartFix

SmartFix is an AI-powered DevOps equipment troubleshooting and maintenance platform. It provides a simple troubleshooting dashboard for technicians and a rich technical observability dashboard for administrators to inspect the full AI pipeline (document ingestion, text extraction, chunking, Ollama embeddings, vector similarity search, safety rules, and LLM reasoning).

---

## Current Status

- **Exercise 1 — Basic LLM Application** (Complete & Working)
- **Exercise 2 — Technical Knowledge Base & Vector DB Observability** (Complete & Working)

---

## Architecture

```text
                               +----------------------------------+
                               |     Vue 3 + Vite Frontend        |
                               |  (Technician UI & Admin UI)      |
                               +-----------------+----------------+
                                                 |
                                     +-----------+-----------+
                                     |                       |
                                     v                       v
                         +-----------------------+ +-----------------------+
                         | Exercise 1 Backend    | | KB Service (Ex. 2)    |
                         | (FastAPI :8000)       | | (FastAPI :8001)       |
                         +-----------+-----------+ +-----------+-----------+
                                     |                       |
                                     v                       v
                         +-------------------------------------------------+
                         |                 Ollama API                      |
                         |  (Code Llama for LLM, nomic-embed-text for Embed) |
                         +-------------------------------------------------+
                                                             |
                                                             v
                                                   +-------------------+
                                                   | ChromaDB + SQLite |
                                                   | (Local Vector DB) |
                                                   +-------------------+
```

---

## Features

### 1. Technician Dashboard (User UI)
- Seamless, clean troubleshooting user interface hiding background technical complexity.
- Ask technical maintenance questions and receive answers from Code Llama via local Ollama.
- Sample diagnostic questions, real-time status loading, error handling, and visual execution flow tracker.

### 2. Admin / AI Observability Dashboard (Admin UI)
- Full visibility into the technical knowledge base pipeline.
- **Document Ingestion**: Upload `.txt`, `.md`, and `.pdf` technical manuals and specifications.
- **Text Extraction & Chunking**: Automatic plain-text extraction and fixed-size overlapping chunking (500 chars, 50 overlap).
- **Ollama Embeddings**: Dense vector generation using `nomic-embed-text` (with transparent offline fallback).
- **Vector DB Persistence**: ChromaDB persistent vector store and SQLite metadata tracking.
- **Observability Inspectors**:
  - Live document status table and file management.
  - Chunk Inspector (index, character start/end boundaries, text preview).
  - Embedding Vector Inspector (dimensions, vector ID, distance metric, float array samples).
  - Vector store collection metrics.

---

## Setup & Running

### 1. Virtual Environment Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r services/knowledge-base/requirements.txt
```

### 2. Start Ollama (Optional for local LLM & embeddings)

```bash
ollama serve
ollama pull codellama
ollama pull nomic-embed-text
```

### 3. Start the Backend Services

#### Exercise 1 Backend (Port 8000)
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

#### Exercise 2 Technical Knowledge Base Service (Port 8001)
```bash
uvicorn services.knowledge-base.main:app --reload --host 127.0.0.1 --port 8001
```

### 4. Start the Vue 3 Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173` in your browser. Use the top navigation bar to toggle between **Technician Dashboard** and **Admin / AI Observability**.

---

## API Documentation

### Knowledge Base Service (`http://127.0.0.1:8001`)

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Knowledge Base service health check |
| `/kb/stats` | GET | Overall statistics (document count, chunk count, ChromaDB vector count) |
| `/kb/documents` | GET | List all ingested documents |
| `/kb/documents/upload` | POST | Upload and process a technical document file (`.txt`, `.md`, `.pdf`) |
| `/kb/documents/{id}` | GET | Get specific document metadata |
| `/kb/documents/{id}/chunks` | GET | List extracted chunks for a document |
| `/kb/chunks/{id}` | GET | Get chunk details and vector ID |
| `/kb/vectors/{vector_id}` | GET | Retrieve vector metadata and embedding float array preview from ChromaDB |
| `/kb/documents/{id}` | DELETE | Delete document, SQLite metadata, and ChromaDB vector embeddings |

### Exercise 1 Backend Service (`http://127.0.0.1:8000`)

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Backend health check |
| `/ask` | POST | Submit question to Code Llama via Ollama |

---

## Project Structure

```text
SmartFix/
├── backend/
│   ├── main.py                     # Exercise 1 FastAPI app (port 8000)
│   └── requirements.txt            # Core backend dependencies
├── services/
│   ├── knowledge-base/             # Exercise 2: Technical Knowledge Base Service
│   │   ├── main.py                 # FastAPI service for KB (port 8001)
│   │   ├── config.py               # Paths, chunk size, vector DB config
│   │   ├── extractors.py           # Text extraction (.txt, .md, .pdf)
│   │   ├── chunker.py              # Overlapping text chunker
│   │   ├── embeddings.py           # Ollama embedding generator
│   │   ├── vector_store.py         # Persistent ChromaDB vector store
│   │   ├── db.py                   # SQLite metadata store
│   │   ├── test_exercise2.py       # Pipeline automated test script
│   │   ├── test_api.py             # ASGI endpoint test script
│   │   └── requirements.txt        # KB service dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/             # Shared Navbar & View Switcher
│   │   │   │   └── Navbar.vue
│   │   │   ├── technician/         # User/Technician Dashboard (Ex. 1)
│   │   │   │   ├── QuestionPanel.vue
│   │   │   │   ├── ResponsePanel.vue
│   │   │   │   └── ExecutionFlow.vue
│   │   │   └── admin/              # Admin Observability Dashboard (Ex. 2)
│   │   │       ├── DocumentManager.vue
│   │   │       ├── ChunkViewer.vue
│   │   │       ├── EmbeddingViewer.vue
│   │   │       └── VectorStoreStats.vue
│   │   ├── api/
│   │   │   ├── askApi.js           # Exercise 1 API client
│   │   │   └── kbApi.js            # Exercise 2 Knowledge Base API client
│   │   ├── App.vue                 # Main view container with tab switcher
│   │   ├── style.css
│   │   └── main.js
│   ├── index.html
│   ├── vite.config.js              # Proxy rules for port 8000 and 8001
│   └── package.json
├── data/                           # Local database & vector store storage
│   ├── documents/uploads/
│   ├── chroma/
│   └── knowledge-base.db
├── README.md
└── LICENSE
```

---

## Future Roadmap

- **Exercise 3**: RAG pipeline integration (Query embedding -> Vector similarity search -> Context retrieval -> Code Llama reasoning).
- **Exercise 4**: Service decomposition into microservices (Equipment Service, Safety Engine, History Service, Spare Parts Service, Service Ticket Service, Orchestrator).
- **Exercise 5**: Containerization with Docker & Docker Compose setup.

---

## License

MIT — see [LICENSE](LICENSE).
