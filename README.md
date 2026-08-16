# SmartFix

SmartFix is an AI-powered DevOps equipment troubleshooting and maintenance assistant. It helps technicians ask technical questions about equipment and receive guidance powered by a local large language model.

## Current Exercise

**Exercise 1 — Basic LLM Application**

This version accepts a user question, sends it through a FastAPI backend to Ollama, uses Code Llama to generate an answer, and displays the result in a simple web frontend with an execution flow visualization.

## Architecture

```
User
  ↓
Frontend (Vue 3 + Vite)
  ↓
FastAPI Backend (POST /ask)
  ↓
Ollama (local HTTP API)
  ↓
Code Llama
  ↓
Response
  ↓
Frontend
```

## Features

- Vue 3 + Vite frontend with Composition API and component structure
- Dark DevOps-themed UI with execution flow visualization
- Technical question input, sample questions, loading, errors, and response display
- FastAPI REST API with input validation and error handling
- Ollama integration using the local `/api/generate` endpoint
- Code Llama response generation
- Execution flow visualization with pending / processing / completed / error states
- Basic backend logging

## Setup

These steps assume macOS and that Ollama is installed separately on your machine.

### 1. Clone or open the project

```bash
cd SmartFix
```

### 2. Create and activate a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install backend requirements

```bash
pip install -r backend/requirements.txt
```

### 4. Start Ollama

If Ollama is not already running, start it from your Applications folder or terminal:

```bash
ollama serve
```

### 5. Pull Code Llama

Download the model once:

```bash
ollama pull codellama
```

You can use a specific variant if you prefer, for example:

```bash
ollama pull codellama:7b
```

If you use a different tag, set `OLLAMA_MODEL` when starting the backend.

### 6. Start the FastAPI backend

From the project root with the virtual environment activated:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Optional environment variables:

```bash
export OLLAMA_URL="http://localhost:11434"
export OLLAMA_MODEL="codellama"
export OLLAMA_TIMEOUT_SECONDS="120"
```

### 7. Install and start the Vue frontend

The frontend is a **Vue 3 + Vite** app. Install dependencies once, then start the dev server:

```bash
cd frontend
npm install
npm run dev
```

Then open the URL shown in the terminal (default):

```text
http://127.0.0.1:5173
```

Vite proxies `/ask` and `/health` to the FastAPI backend at `http://127.0.0.1:8000`, so the backend must be running before you submit a question.

Optional production build:

```bash
npm run build
npm run preview
```

### 8. Test the application

#### Browser test

1. Enter a question such as: `How should I troubleshoot low hydraulic pressure?`
2. Click **Ask SmartFix**
3. Watch the execution flow update
4. Read the response from Code Llama

#### API test with curl

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "How should I troubleshoot low hydraulic pressure?"}'
```

Example response:

```json
{
  "question": "How should I troubleshoot low hydraulic pressure?",
  "answer": "... Code Llama generated answer ...",
  "model": "codellama"
}
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## API

### `POST /ask`

Accepts a troubleshooting question and returns a Code Llama answer.

**Request body**

```json
{
  "question": "How should I troubleshoot low hydraulic pressure?"
}
```

**Success response (`200 OK`)**

```json
{
  "question": "How should I troubleshoot low hydraulic pressure?",
  "answer": "Check for leaks, inspect the pump inlet filter, verify fluid level ...",
  "model": "codellama"
}
```

**Error responses**

| Status | When |
|--------|------|
| `400` | Empty or missing question |
| `502` | Ollama returned an error or empty response |
| `503` | Ollama is not reachable |
| `504` | Ollama request timed out |

### `GET /health`

Simple service health check.

## Project Structure

```text
SmartFix/
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ExecutionFlow.vue
│   │   │   ├── QuestionPanel.vue
│   │   │   └── ResponsePanel.vue
│   │   ├── api.js
│   │   ├── App.vue
│   │   ├── flowStages.js
│   │   ├── main.js
│   │   └── style.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── README.md
├── LICENSE
└── .gitignore
```

## Future Development

Later exercises will extend SmartFix with:

- Knowledge base ingestion
- Chunking
- Embeddings
- Vector similarity search
- RAG retrieval
- Equipment Service
- Safety Engine
- Equipment History Service
- Spare Parts Service
- Service Ticket Service
- Orchestration across services
- Docker and complete application architecture

Those modules are intentionally **not** part of Exercise 1.

## License

MIT — see [LICENSE](LICENSE).
