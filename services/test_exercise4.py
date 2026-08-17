"""
Integration test script for Exercise 4 Microservices & Orchestrator.
"""

import asyncio
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "services" / "equipment"))
sys.path.insert(0, str(PROJECT_ROOT / "services" / "history"))
sys.path.insert(0, str(PROJECT_ROOT / "services" / "safety"))
sys.path.insert(0, str(PROJECT_ROOT / "services" / "spare-parts"))
sys.path.insert(0, str(PROJECT_ROOT / "services" / "tickets"))
sys.path.insert(0, str(PROJECT_ROOT / "services" / "llm"))
sys.path.insert(0, str(PROJECT_ROOT / "services" / "rag"))
sys.path.insert(0, str(PROJECT_ROOT / "services" / "orchestrator"))

import httpx
from equipment.main import app as equipment_app
from history.main import app as history_app
from safety.main import app as safety_app
from spare_parts.main import app as spare_parts_app
from tickets.main import app as tickets_app
from llm.main import app as llm_app
from rag.main import app as rag_app
from orchestrator.main import app as orchestrator_app


async def test_microservices():
    print("=== Testing SmartFix Exercise 4 Microservices & Safety Engine ===")

    # 1. Test Equipment Service
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=equipment_app), base_url="http://test") as client:
        r = await client.get("/equipment/EQ-1023")
        print("1. Equipment Service (EQ-1023):", r.status_code, r.json()["name"])
        assert r.status_code == 200

    # 2. Test History Service
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=history_app), base_url="http://test") as client:
        r = await client.get("/history/EQ-1023")
        print("2. History Service (EQ-1023):", r.status_code, f"Events: {r.json()['event_count']}")
        assert r.status_code == 200

    # 3. Test Safety Engine (WARNING case)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=safety_app), base_url="http://test") as client:
        r = await client.post("/safety/evaluate", json={"equipment_id": "EQ-1023", "question": "Check hydraulic pressure"})
        print("3. Safety Engine (Hydraulic Check): Decision =", r.json()["decision"], "| Precautions:", len(r.json()["required_precautions"]))
        assert r.json()["decision"] == "WARNING"

        # Test Safety Engine (BLOCKED case - 400V live terminal)
        r_blocked = await client.post("/safety/evaluate", json={"equipment_id": "EQ-3081", "question": "Open terminal box while live"})
        print("   Safety Engine (400V Live Access): Decision =", r_blocked.json()["decision"])
        assert r_blocked.json()["decision"] == "BLOCKED"

    # 4. Test Spare Parts Service
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=spare_parts_app), base_url="http://test") as client:
        r = await client.get("/spare-parts/EQ-1023")
        print("4. Spare Parts Service (EQ-1023): Parts count =", r.json()["parts_count"])
        assert r.status_code == 200

    # 5. Test Ticket Service
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=tickets_app), base_url="http://test") as client:
        r = await client.post("/tickets/create", json={"equipment_id": "EQ-1023", "issue_summary": "Pressure drop"})
        print("5. Ticket Service: Ticket ID =", r.json()["ticket_id"], "| Status =", r.json()["status"])
        assert r.status_code == 200

    # 6. Test LLM Service
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=llm_app), base_url="http://test") as client:
        r = await client.post("/llm/generate", json={"question": "Troubleshoot hydraulic pressure", "safety_info": {"decision": "WARNING"}})
        print("6. LLM Gateway Service: Mode =", r.json()["execution_mode"], "| Model =", r.json()["model"])
        assert r.status_code == 200

    print("✅ All Exercise 4 Microservices & Deterministic Safety Engine Verified Successfully!")


if __name__ == "__main__":
    asyncio.run(test_microservices())
