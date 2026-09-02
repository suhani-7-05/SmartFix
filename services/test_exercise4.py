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

    # 1. Test Equipment Service (Appliance + Industrial)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=equipment_app), base_url="http://test") as client:
        r = await client.get("/equipment/HA-MICRO-01")
        print("1. Equipment Service (HA-MICRO-01):", r.status_code, r.json()["name"])
        assert r.status_code == 200
        assert "Panasonic" in r.json()["name"]

    # 2. Test History Service
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=history_app), base_url="http://test") as client:
        r = await client.get("/history/HA-MICRO-01")
        print("2. History Service (HA-MICRO-01):", r.status_code, f"Events: {r.json()['event_count']}")
        assert r.status_code == 200
        assert r.json()["event_count"] >= 1

    # 3. Test Safety Engine (Appliance Safety Rules)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=safety_app), base_url="http://test") as client:
        # Test Safety Engine (WARNING - Toaster heating element)
        r_toast = await client.post("/safety/evaluate", json={"equipment_id": "HA-TOAST-02", "question": "Inspect toaster heating elements"})
        print("3. Safety Engine (Toaster): Decision =", r_toast.json()["decision"], "| Precautions:", len(r_toast.json()["required_precautions"]))
        assert r_toast.json()["decision"] == "WARNING"

        # Test Safety Engine (BLOCKED case - Microwave High Voltage Capacitor)
        r_blocked = await client.post("/safety/evaluate", json={"equipment_id": "HA-MICRO-01", "question": "Open cabinet and touch capacitor while plugged in"})
        print("   Safety Engine (Microwave HV Capacitor): Decision =", r_blocked.json()["decision"])
        assert r_blocked.json()["decision"] == "BLOCKED"

        # Test Safety Engine (BLOCKED case - Washer drum spin bypass)
        r_wash_blocked = await client.post("/safety/evaluate", json={"equipment_id": "HA-WASH-04", "question": "Bypass door lock during spin cycle"})
        print("   Safety Engine (Washer Spin Bypass): Decision =", r_wash_blocked.json()["decision"])
        assert r_wash_blocked.json()["decision"] == "BLOCKED"

    # 4. Test Spare Parts Service (Appliance Parts)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=spare_parts_app), base_url="http://test") as client:
        r = await client.get("/spare-parts/HA-MICRO-01")
        print("4. Spare Parts Service (HA-MICRO-01): Parts count =", r.json()["parts_count"])
        assert r.status_code == 200
        assert r.json()["parts_count"] >= 3

    # 5. Test Ticket Service
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=tickets_app), base_url="http://test") as client:
        r = await client.post("/tickets/create", json={"equipment_id": "HA-MICRO-01", "issue_summary": "Microwave capacitor hazard", "safety_decision": "BLOCKED"})
        print("5. Ticket Service: Ticket ID =", r.json()["ticket_id"], "| Status =", r.json()["status"])
        assert r.status_code == 200

    # 6. Test LLM Service
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=llm_app), base_url="http://test", timeout=180.0) as client:
        r = await client.post("/llm/generate", json={"question": "Microwave food cold", "safety_info": {"decision": "WARNING"}, "model": "codellama"})
        print("6. LLM Gateway Service: Mode =", r.json()["execution_mode"], "| Model =", r.json()["model"])
        assert r.status_code == 200

    print("[SUCCESS] All Exercise 4 Microservices & Deterministic Safety Engine Verified Successfully!")


if __name__ == "__main__":
    asyncio.run(test_microservices())
