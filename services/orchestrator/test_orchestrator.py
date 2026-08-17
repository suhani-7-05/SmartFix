"""
Test script for SmartFix Orchestrator Service.
"""

import asyncio
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICES_DIR = REPO_ROOT / "services"
sys.path.insert(0, str(SERVICES_DIR))
sys.path.insert(0, str(SERVICES_DIR / "equipment"))
sys.path.insert(0, str(SERVICES_DIR / "history"))
sys.path.insert(0, str(SERVICES_DIR / "safety"))
sys.path.insert(0, str(SERVICES_DIR / "spare_parts"))
sys.path.insert(0, str(SERVICES_DIR / "tickets"))
sys.path.insert(0, str(SERVICES_DIR / "llm"))
sys.path.insert(0, str(SERVICES_DIR / "rag"))
sys.path.insert(0, str(SERVICES_DIR / "orchestrator"))


from equipment.main import app as equipment_app
from history.main import app as history_app
from safety.main import app as safety_app
from spare_parts.main import app as spare_parts_app
from tickets.main import app as tickets_app
from llm.main import app as llm_app
from rag.main import app as rag_app
from orchestrator.main import app as orchestrator_app, call_service_endpoint

import httpx


async def test_orchestrator_pipeline():
    print("=== Testing SmartFix Orchestrator End-to-End Execution Trace ===")

    # Test direct execution of orchestrator functions
    async with httpx.AsyncClient() as client:
        # 1. Equipment call
        eq_data, t1 = await call_service_endpoint(
            httpx.AsyncClient(transport=httpx.ASGITransport(app=equipment_app), base_url="http://test"),
            "GET",
            "http://test/equipment/EQ-1023",
            "Equipment Service",
        )
        print("1. Orchestrated Step 1 - Equipment:", t1["status"], f"({t1['duration_ms']}ms)")

        # 2. History call
        hist_data, t2 = await call_service_endpoint(
            httpx.AsyncClient(transport=httpx.ASGITransport(app=history_app), base_url="http://test"),
            "GET",
            "http://test/history/EQ-1023",
            "History Service",
        )
        print("2. Orchestrated Step 2 - History:", t2["status"], f"({t2['duration_ms']}ms)")

        # 3. RAG call
        rag_data, t3 = await call_service_endpoint(
            httpx.AsyncClient(transport=httpx.ASGITransport(app=rag_app), base_url="http://test"),
            "POST",
            "http://test/rag/retrieve",
            "RAG Service",
            {"query": "EQ-1023 low pressure", "top_k": 2},
        )
        print("3. Orchestrated Step 3 - RAG:", t3["status"], f"Retrieved {len(t3['output'].get('retrieved_chunks', []))} chunks")

        # 4. Safety call
        safety_data, t4 = await call_service_endpoint(
            httpx.AsyncClient(transport=httpx.ASGITransport(app=safety_app), base_url="http://test"),
            "POST",
            "http://test/safety/evaluate",
            "Safety Engine",
            {"equipment_id": "EQ-1023", "question": "Check hydraulic pressure"},
        )
        print("4. Orchestrated Step 4 - Safety Engine:", t4["status"], "Decision =", safety_data.get("decision"))

        # 5. Spare Parts call
        parts_data, t5 = await call_service_endpoint(
            httpx.AsyncClient(transport=httpx.ASGITransport(app=spare_parts_app), base_url="http://test"),
            "GET",
            "http://test/spare-parts/EQ-1023",
            "Spare Parts Service",
        )
        print("5. Orchestrated Step 5 - Spare Parts:", t5["status"], "Parts count =", parts_data.get("parts_count"))

        # 6. LLM call
        llm_data, t6 = await call_service_endpoint(
            httpx.AsyncClient(transport=httpx.ASGITransport(app=llm_app), base_url="http://test"),
            "POST",
            "http://test/llm/generate",
            "LLM Service",
            {"question": "EQ-1023 low pressure", "equipment_info": eq_data, "safety_info": safety_data},
        )
        print("6. Orchestrated Step 6 - LLM Gateway:", t6["status"], "Mode =", llm_data.get("execution_mode"))

    print("\n✅ SmartFix Orchestrator End-to-End Execution Trace Test Passed!")


if __name__ == "__main__":
    asyncio.run(test_orchestrator_pipeline())
