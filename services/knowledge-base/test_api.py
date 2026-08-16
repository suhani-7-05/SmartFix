"""
Direct ASGI endpoint test for Exercise 2 Knowledge Base FastAPI service.
"""

import asyncio
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
KB_DIR = PROJECT_ROOT / "services" / "knowledge-base"
sys.path.insert(0, str(KB_DIR))

import httpx
from main import app


async def test_api():
    print("=== Testing Knowledge Base Service FastAPI Endpoints ===")
    
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Health Check
        r_health = await client.get("/health")
        print("GET /health:", r_health.status_code, r_health.json())
        assert r_health.status_code == 200

        # 2. Stats
        r_stats = await client.get("/kb/stats")
        print("GET /kb/stats:", r_stats.status_code, r_stats.json())
        assert r_stats.status_code == 200

        # 3. List Documents
        r_docs = await client.get("/kb/documents")
        print("GET /kb/documents:", r_docs.status_code, f"Found {len(r_docs.json())} documents")
        assert r_docs.status_code == 200
        
        docs = r_docs.json()
        if docs:
            doc_id = docs[0]["id"]
            # 4. Get Doc Detail
            r_doc = await client.get(f"/kb/documents/{doc_id}")
            print(f"GET /kb/documents/{doc_id}:", r_doc.status_code, r_doc.json()["filename"])
            
            # 5. Get Chunks
            r_chunks = await client.get(f"/kb/documents/{doc_id}/chunks")
            print(f"GET /kb/documents/{doc_id}/chunks:", r_chunks.status_code, f"Found {len(r_chunks.json())} chunks")
            
            chunks = r_chunks.json()
            if chunks and chunks[0].get("vector_id"):
                vec_id = chunks[0]["vector_id"]
                # 6. Get Vector Metadata
                r_vec = await client.get(f"/kb/vectors/{vec_id}")
                print(f"GET /kb/vectors/{vec_id}:", r_vec.status_code, "Dims:", r_vec.json()["dimensions"])

    print("✅ All Knowledge Base API Endpoints Verified Successfully!")


if __name__ == "__main__":
    asyncio.run(test_api())
