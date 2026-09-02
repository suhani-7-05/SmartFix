"""
SmartFix Orchestrator Service — Exercise 4

Central orchestrator coordinating microservices via REST APIs.
Captures real execution traces, timing, HTTP status, service calls, safety decisions,
RAG retrieval, and ticket generation.
"""

import logging
import os
import re
import time
from typing import Any
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Service URL configuration (override via env variables or defaults)
EQUIPMENT_SERVICE_URL = os.getenv("EQUIPMENT_SERVICE_URL", "http://127.0.0.1:8002").rstrip("/")
SAFETY_SERVICE_URL = os.getenv("SAFETY_SERVICE_URL", "http://127.0.0.1:8003").rstrip("/")
HISTORY_SERVICE_URL = os.getenv("HISTORY_SERVICE_URL", "http://127.0.0.1:8004").rstrip("/")
SPARE_PARTS_SERVICE_URL = os.getenv("SPARE_PARTS_SERVICE_URL", "http://127.0.0.1:8005").rstrip("/")
TICKET_SERVICE_URL = os.getenv("TICKET_SERVICE_URL", "http://127.0.0.1:8006").rstrip("/")
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://127.0.0.1:8001").rstrip("/")
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://127.0.0.1:8007").rstrip("/")

ALLOWED_LLM_MODELS = [
    "codellama:7b",
    "codellama",
    "codellama:latest",
    "starcoder2:3b",
    "starcoder2",
    "qwen2.5-coder:1.5b",
    "qwen2.5-coder",
    "qwen:1.8b",
    "deepseek-r1:1.5b",
]
DEFAULT_LLM_MODEL = "codellama"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("smartfix.orchestrator")

app = FastAPI(title="SmartFix Orchestrator Service", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OrchestrationRequest(BaseModel):
    question: str = Field(..., description="Troubleshooting question from technician")
    equipment_id: str | None = Field(default=None, description="Optional Equipment ID (e.g., EQ-1023)")
    model: str | None = Field(default=None, description="Ollama model to use for LLM generation")


def extract_equipment_id(text: str, explicit_id: str | None = None) -> str:
    if explicit_id:
        return explicit_id.upper()

    # Match explicit IDs like HA-MICRO-01 or EQ-1023
    match_ha = re.search(r"\b(HA-[A-Z]+-\d{2})\b", text, re.IGNORECASE)
    if match_ha:
        return match_ha.group(1).upper()

    match_eq = re.search(r"\b(EQ-\d{4})\b", text, re.IGNORECASE)
    if match_eq:
        return match_eq.group(1).upper()

    # Keyword-based natural language mapping for domestic appliances
    t_lower = text.lower()
    if "microwave" in t_lower:
        return "HA-MICRO-01"
    elif "toaster" in t_lower:
        return "HA-TOAST-02"
    elif "air fryer" in t_lower or "airfryer" in t_lower:
        return "HA-AIRFRY-03"
    elif "washing machine" in t_lower or "washer" in t_lower or "drum" in t_lower:
        return "HA-WASH-04"
    elif "oven" in t_lower:
        return "HA-OVEN-05"
    elif "chimney" in t_lower or "range hood" in t_lower or "hood" in t_lower:
        return "HA-CHIM-06"
    elif "pump" in t_lower or "hydraulic" in t_lower:
        return "EQ-1023"
    elif "conveyor" in t_lower or "belt" in t_lower:
        return "EQ-2045"
    elif "motor" in t_lower:
        return "EQ-3081"

    # Default to HA-MICRO-01 for household appliance queries
    return "HA-MICRO-01"


async def call_service_endpoint(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    step_name: str,
    json_body: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Helper to execute HTTP service call and return (result_data, trace_step_metadata)."""
    start_t = time.time()
    trace = {
        "step_name": step_name,
        "method": method.upper(),
        "url": url,
        "status": "PENDING",
        "http_code": 0,
        "duration_ms": 0,
        "input": json_body or {},
        "output": {},
        "error": None,
    }

    try:
        if method.upper() == "GET":
            resp = await client.get(url, timeout=10.0)
        else:
            resp = await client.post(url, json=json_body, timeout=180.0)

        duration = round((time.time() - start_t) * 1000, 2)
        trace["duration_ms"] = duration
        trace["http_code"] = resp.status_code

        if resp.status_code == 200:
            data = resp.json()
            trace["status"] = "COMPLETED"
            trace["output"] = data
            return data, trace
        else:
            trace["status"] = "ERROR"
            trace["error"] = f"HTTP {resp.status_code}: {resp.text}"
            return {}, trace

    except Exception as exc:
        duration = round((time.time() - start_t) * 1000, 2)
        trace["duration_ms"] = duration
        trace["status"] = "ERROR"
        trace["error"] = str(exc)
        logger.error("Step '%s' call to %s failed: %s", step_name, url, exc)
        return {}, trace


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "smartfix-orchestrator", "version": "0.4.0"}


@app.post("/ask")
@app.post("/orchestrate")
async def orchestrate_request(body: OrchestrationRequest) -> dict[str, Any]:
    """
    Main Orchestration Endpoint.

    Coordinates microservice execution flow:
    Request -> Equipment -> History -> RAG -> Safety Engine -> Spare Parts -> LLM -> Ticket -> Response
    """
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    selected_model = body.model if body.model in ALLOWED_LLM_MODELS else DEFAULT_LLM_MODEL
    eq_id = extract_equipment_id(question, body.equipment_id)
    execution_trace = []
    total_start = time.time()

    async with httpx.AsyncClient() as client:
        # Step 1: Equipment Service
        eq_data, trace1 = await call_service_endpoint(
            client, "GET", f"{EQUIPMENT_SERVICE_URL}/equipment/{eq_id}", "Equipment Service"
        )
        execution_trace.append(trace1)

        # Step 2: History Service
        hist_data, trace2 = await call_service_endpoint(
            client, "GET", f"{HISTORY_SERVICE_URL}/history/{eq_id}", "History Service"
        )
        execution_trace.append(trace2)

        # Step 3: RAG Retrieval Service
        rag_data, trace3 = await call_service_endpoint(
            client, "POST", f"{RAG_SERVICE_URL}/rag/retrieve", "RAG Service", {"query": question, "top_k": 3}
        )
        execution_trace.append(trace3)

        # Step 4: Safety Engine Service
        safety_data, trace4 = await call_service_endpoint(
            client,
            "POST",
            f"{SAFETY_SERVICE_URL}/safety/evaluate",
            "Safety Engine",
            {"equipment_id": eq_id, "question": question, "equipment_data": eq_data},
        )
        execution_trace.append(trace4)

        # Step 5: Spare Parts Service
        parts_data, trace5 = await call_service_endpoint(
            client, "GET", f"{SPARE_PARTS_SERVICE_URL}/spare-parts/{eq_id}", "Spare Parts Service"
        )
        execution_trace.append(trace5)

        # Step 6: LLM Gateway Service
        llm_input = {
            "question": question,
            "model": selected_model,
            "equipment_info": eq_data,
            "history_info": hist_data,
            "rag_info": rag_data,
            "safety_info": safety_data,
            "spare_parts_info": parts_data,
        }
        llm_data, trace6 = await call_service_endpoint(
            client, "POST", f"{LLM_SERVICE_URL}/llm/generate", "LLM Service", llm_input
        )
        execution_trace.append(trace6)

        # Step 7: Ticket Service (If Safety is BLOCKED or dispatch required)
        ticket_data = {}
        safety_decision = safety_data.get("decision", "ALLOWED")
        if safety_decision == "BLOCKED" or "ticket" in question.lower() or "dispatch" in question.lower():
            ticket_input = {
                "equipment_id": eq_id,
                "issue_summary": f"Automated ticket for {eq_id}: {question[:100]}",
                "priority": "CRITICAL" if safety_decision == "BLOCKED" else "HIGH",
                "safety_decision": safety_decision,
            }
            ticket_data, trace7 = await call_service_endpoint(
                client, "POST", f"{TICKET_SERVICE_URL}/tickets/create", "Ticket Service", ticket_input
            )
            execution_trace.append(trace7)

    total_duration_ms = round((time.time() - total_start) * 1000, 2)

    return {
        "question": question,
        "equipment_id": eq_id,
        "answer": llm_data.get("answer", "No answer generated."),
        "model": llm_data.get("model", selected_model),
        "safety_decision": safety_decision,
        "equipment": eq_data,
        "history": hist_data,
        "rag": rag_data,
        "safety": safety_data,
        "spare_parts": parts_data,
        "ticket": ticket_data,
        "total_duration_ms": total_duration_ms,
        "execution_trace": execution_trace,
    }


# Transparent gateway proxies for frontend tabs
@app.get("/kb/stats")
async def proxy_kb_stats():
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{RAG_SERVICE_URL}/kb/stats")
        return r.json()


@app.get("/kb/documents")
async def proxy_kb_documents():
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{RAG_SERVICE_URL}/kb/documents")
        return r.json()


@app.get("/equipment")
async def proxy_equipment():
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{EQUIPMENT_SERVICE_URL}/equipment")
        return r.json()


@app.get("/tickets")
async def proxy_tickets():
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{TICKET_SERVICE_URL}/tickets")
        return r.json()
