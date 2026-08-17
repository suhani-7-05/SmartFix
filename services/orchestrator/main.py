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


def extract_equipment_id(text: str, explicit_id: str | None = None) -> str:
    if explicit_id:
        return explicit_id.upper()
    match = re.search(r"\b(EQ-\d{4})\b", text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    # Default to EQ-1023 if unspecified
    return "EQ-1023"


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
            resp = await client.post(url, json=json_body, timeout=120.0)

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
        "model": llm_data.get("model", "codellama"),
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
