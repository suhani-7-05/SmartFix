"""
SmartFix Backend — Exercise 1

FastAPI application that accepts equipment troubleshooting questions
and forwards them to Code Llama via the local Ollama API.
"""

import logging
import os
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Configuration (override with environment variables in production/dev)
# ---------------------------------------------------------------------------
OLLAMA_BASE_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "codellama")
OLLAMA_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("smartfix")

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="SmartFix API",
    description="Exercise 1 — Basic LLM troubleshooting assistant",
    version="0.1.0",
)

# Allow the vanilla JS frontend (file:// or local static server) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    """Incoming question from the frontend."""

    question: str = Field(..., description="Technical or equipment-related question")


class AskResponse(BaseModel):
    """Successful response returned to the frontend."""

    question: str
    answer: str
    model: str


def build_prompt(question: str) -> str:
    """Wrap the user question in a prompt suited for Code Llama."""
    return (
        "You are SmartFix, an AI assistant for DevOps equipment troubleshooting "
        "and maintenance.\n\n"
        "Answer the following technical question clearly, practically, and safely. "
        "If relevant, suggest diagnostic steps a technician can follow.\n\n"
        f"Question: {question.strip()}\n\n"
        "Answer:"
    )


async def call_ollama(prompt: str) -> str:
    """
    Send a generate request to the local Ollama API and return the model text.

    Uses Ollama's /api/generate endpoint with streaming disabled for simplicity.
    """
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload: dict[str, Any] = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    logger.info("Calling Ollama at %s with model '%s'", url, OLLAMA_MODEL)

    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT_SECONDS) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
    except httpx.ConnectError as exc:
        logger.error("Could not connect to Ollama at %s: %s", OLLAMA_BASE_URL, exc)
        raise HTTPException(
            status_code=503,
            detail=(
                "Ollama is unavailable. Ensure Ollama is running locally "
                f"at {OLLAMA_BASE_URL}."
            ),
        ) from exc
    except httpx.TimeoutException as exc:
        logger.error("Ollama request timed out after %ss", OLLAMA_TIMEOUT_SECONDS)
        raise HTTPException(
            status_code=504,
            detail="Ollama request timed out. The model may still be loading; try again.",
        ) from exc
    except httpx.HTTPStatusError as exc:
        logger.error(
            "Ollama returned HTTP %s: %s",
            exc.response.status_code,
            exc.response.text,
        )
        raise HTTPException(
            status_code=502,
            detail=f"Ollama returned an error: {exc.response.text}",
        ) from exc
    except httpx.RequestError as exc:
        logger.error("Ollama request failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"Failed to reach Ollama: {exc}",
        ) from exc

    data = response.json()
    answer = data.get("response", "").strip()

    if not answer:
        logger.error("Ollama returned an empty response: %s", data)
        raise HTTPException(
            status_code=502,
            detail="Ollama returned an empty response. Check that the model is installed.",
        )

    logger.info("Received response from Ollama (%d characters)", len(answer))
    return answer


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Simple health endpoint for manual checks."""
    return {"status": "ok", "service": "smartfix-backend"}


@app.post("/ask", response_model=AskResponse)
async def ask_question(body: AskRequest) -> AskResponse:
    """
    Accept a troubleshooting question, send it to Code Llama via Ollama,
    and return the generated answer.
    """
    question = body.question.strip()

    if not question:
        logger.warning("Rejected empty question")
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    logger.info("Received question: %s", question[:120])

    prompt = build_prompt(question)
    answer = await call_ollama(prompt)

    return AskResponse(question=question, answer=answer, model=OLLAMA_MODEL)
