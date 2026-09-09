"""
SmartFix LLM Service — Exercise 4

Interfaces with Ollama + Code Llama API to generate natural language troubleshooting guidance
from structured context (Equipment, History, RAG Chunks, Safety Decision, Spare Parts).
"""

import logging
import os
from typing import Any
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

OLLAMA_BASE_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "180"))

ALLOWED_MODELS = [
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
DEFAULT_MODEL = "qwen2.5-coder:1.5b"

BENCHMARK_MODELS = [
    {"id": "codellama:latest", "alias": "codellama", "name": "Code Llama (7B)"},
    {"id": "starcoder2:3b", "alias": "starcoder2", "name": "StarCoder2 (3B)"},
    {"id": "qwen2.5-coder:1.5b", "alias": "qwen2.5-coder", "name": "Qwen 2.5 Coder (1.5B)"},
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("smartfix.llm-service")

app = FastAPI(title="SmartFix LLM Gateway Service", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def resolve_model(requested_model: str | None) -> str:
    fallback = OLLAMA_MODEL if OLLAMA_MODEL in ALLOWED_MODELS else DEFAULT_MODEL
    model = requested_model or fallback
    m_lower = model.lower()
    if "codellama" in m_lower:
        return "codellama:latest"
    elif "starcoder" in m_lower:
        return "starcoder2:3b"
    elif "qwen" in m_lower:
        return "qwen2.5-coder:1.5b"
        
    if model not in ALLOWED_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported model '{model}'. Allowed models: {', '.join(ALLOWED_MODELS)}",
        )
    return model


class LLMGenerateRequest(BaseModel):
    question: str = Field(..., description="User troubleshooting question")
    model: str | None = Field(default=None, description="Ollama model to use for generation")
    equipment_info: dict[str, Any] = Field(default_factory=dict)
    history_info: dict[str, Any] = Field(default_factory=dict)
    rag_info: dict[str, Any] = Field(default_factory=dict)
    safety_info: dict[str, Any] = Field(default_factory=dict)
    spare_parts_info: dict[str, Any] = Field(default_factory=dict)


def build_augmented_prompt(req: LLMGenerateRequest) -> str:
    safety_dec = req.safety_info.get("decision", "ALLOWED")
    safety_warnings = req.safety_info.get("warnings", [])
    precautions = req.safety_info.get("required_precautions", [])
    rag_context = req.rag_info.get("constructed_context", "No manual context found.")
    eq_name = req.equipment_info.get("name", "Unknown Machinery")
    eq_model = req.equipment_info.get("model", "N/A")
    eq_id = req.equipment_info.get("equipment_id", "N/A")

    prompt = (
        "You are SmartFix, an expert AI DevOps equipment troubleshooting assistant.\n"
        "Analyze the supplied equipment metadata, maintenance history, RAG manual context, safety rules, and spare parts inventory to generate clear diagnostic guidance.\n\n"
        f"=== TARGET EQUIPMENT ===\n"
        f"Equipment ID: {eq_id} | Name: {eq_name} | Model: {eq_model}\n"
        f"Specifications: {req.equipment_info.get('specifications', {})}\n\n"
        f"=== SAFETY ENGINE EVALUATION (MANDATORY) ===\n"
        f"Decision: {safety_dec}\n"
        f"Warnings: {safety_warnings}\n"
        f"Required Precautions: {precautions}\n"
        "CRITICAL INSTRUCTION: You MUST honor the Safety Engine decision. Do NOT override or contradict the safety decision.\n\n"
        f"=== MAINTENANCE & FAILURE HISTORY ===\n"
        f"Past Events Count: {req.history_info.get('event_count', 0)}\n"
        f"Recent History: {req.history_info.get('history', [])}\n\n"
        f"=== RETRIEVED TECHNICAL MANUAL CHUNKS (RAG) ===\n"
        f"{rag_context}\n\n"
        f"=== COMPATIBLE SPARE PARTS INVENTORY ===\n"
        f"Parts: {req.spare_parts_info.get('parts', [])}\n\n"
        f"=== TECHNICIAN QUESTION ===\n"
        f"{req.question}\n\n"
        "Provide a structured, step-by-step diagnostic answer. Include safety warnings, root cause analysis, diagnostic steps, and compatible spare part numbers if applicable."
    )
    return prompt


def generate_fallback_synthesis(req: LLMGenerateRequest, prompt: str) -> str:
    safety_dec = req.safety_info.get("decision", "ALLOWED")
    precautions = req.safety_info.get("required_precautions", [])
    eq_name = req.equipment_info.get("name", "Equipment")
    eq_id = req.equipment_info.get("equipment_id", "EQ")
    parts = req.spare_parts_info.get("parts", [])

    lines = []
    lines.append(f"### SmartFix Diagnostic Report for {eq_name} ({eq_id})")
    lines.append(f"**Safety Status**: {safety_dec}")

    if safety_dec == "BLOCKED":
        lines.append("\n⚠️ **OPERATION BLOCKED BY SAFETY ENGINE**")
        lines.append("The requested action poses severe safety risks. Mandatory safety protocols must be followed:")
        for p in precautions:
            lines.append(f"- {p}")
        lines.append("\nA service ticket has been dispatched for an on-site technician.")
        return "\n".join(lines)

    lines.append("\n**Mandatory Safety Precautions:**")
    for p in precautions:
        lines.append(f"- {p}")

    lines.append("\n**Diagnostic & Troubleshooting Steps:**")
    lines.append("1. **Visual & Sensor Check**: Inspect fluid level, pressure gauge readouts, and line connections.")
    lines.append("2. **Filter & Valve Inspection**: Inspect inlet suction filter for clogging or debris accumulation. Check relief valve calibration.")
    lines.append("3. **Historical Pattern**: Review past corrective actions for similar pressure drops.")

    if parts:
        lines.append("\n**Compatible Replacement Parts Inventory:**")
        for pt in parts:
            lines.append(f"- **{pt.get('part_number')}**: {pt.get('name')} (Status: {pt.get('stock_status')}, Qty: {pt.get('quantity_available')})")

    return "\n".join(lines)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "smartfix-llm-service", "ollama_url": OLLAMA_BASE_URL, "model": OLLAMA_MODEL}


@app.post("/llm/generate")
async def generate_response(body: LLMGenerateRequest) -> dict[str, Any]:
    prompt = build_augmented_prompt(body)
    model = resolve_model(body.model)
    url = f"{OLLAMA_BASE_URL}/api/generate"

    candidate_models = [model]
    if ":" in model:
        base_name = model.split(":")[0]
        if base_name not in candidate_models:
            candidate_models.append(base_name)
        if f"{base_name}:latest" not in candidate_models:
            candidate_models.append(f"{base_name}:latest")
    else:
        if f"{model}:latest" not in candidate_models:
            candidate_models.append(f"{model}:latest")

    if "codellama" in model.lower():
        for m in ["codellama:latest", "codellama", "codellama:7b"]:
            if m not in candidate_models:
                candidate_models.append(m)
    elif "qwen" in model.lower():
        for m in ["qwen2.5-coder:1.5b", "qwen2.5-coder", "qwen:1.8b"]:
            if m not in candidate_models:
                candidate_models.append(m)
    elif "starcoder" in model.lower():
        for m in ["starcoder2:3b", "starcoder2"]:
            if m not in candidate_models:
                candidate_models.append(m)

    for cand in candidate_models:
        payload = {
            "model": cand,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": 250, "temperature": 0.2},
        }
        try:
            async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 404:
                    logger.info("Model '%s' not found on Ollama, trying next candidate...", cand)
                    continue
                resp.raise_for_status()
                data = resp.json()
                answer = data.get("response", "").strip()
                if answer:
                    return {
                        "answer": answer,
                        "model": cand,
                        "prompt_length": len(prompt),
                        "execution_mode": "ollama",
                    }
        except Exception as exc:
            logger.warning("Ollama call with model '%s' failed (%s).", cand, exc)

    logger.warning("All Ollama model candidates failed. Generating fallback LLM synthesis.")
    fallback_answer = generate_fallback_synthesis(body, prompt)
    return {
        "answer": fallback_answer,
        "model": f"{model} (offline-synthesis)",
        "prompt_length": len(prompt),
        "execution_mode": "offline-fallback-synthesis",
    }


@app.post("/llm/compare")
async def compare_models_response(body: LLMGenerateRequest) -> dict[str, Any]:
    """Invokes all 3 candidate models on the same prompt and returns comparative outputs."""
    import time
    prompt = build_augmented_prompt(body)
    results = {}

    for m_def in BENCHMARK_MODELS:
        m_id = m_def["id"]
        m_alias = m_def["alias"]
        m_name = m_def["name"]
        t0 = time.time()
        payload = {
            "model": m_id,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": 180, "temperature": 0.2},
        }
        try:
            async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
                resp = await client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    answer = data.get("response", "").strip()
                    duration_ms = round((time.time() - t0) * 1000, 2)
                    results[m_alias] = {
                        "name": m_name,
                        "model_id": m_id,
                        "answer": answer,
                        "latency_ms": duration_ms,
                        "prompt_eval_count": data.get("prompt_eval_count", len(prompt) // 4),
                        "eval_count": data.get("eval_count", len(answer) // 4),
                        "execution_mode": "ollama",
                        "status": "success",
                    }
                else:
                    duration_ms = round((time.time() - t0) * 1000, 2)
                    results[m_alias] = {
                        "name": m_name,
                        "model_id": m_id,
                        "answer": f"Ollama HTTP {resp.status_code}: {resp.text}",
                        "latency_ms": duration_ms,
                        "execution_mode": "error",
                        "status": "error",
                    }
        except Exception as exc:
            duration_ms = round((time.time() - t0) * 1000, 2)
            results[m_alias] = {
                "name": m_name,
                "model_id": m_id,
                "answer": f"Error contacting model: {exc}",
                "latency_ms": duration_ms,
                "execution_mode": "error",
                "status": "error",
            }

    return {
        "prompt_length": len(prompt),
        "models": results,
    }

