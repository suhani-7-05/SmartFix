"""
Test script for RAG Service.
"""

import asyncio
from pathlib import Path
import sys

RAG_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(RAG_DIR))

import httpx
from main import app


async def test_rag_service():
    print("=== Testing SmartFix RAG Service (Exercise 3) ===")
    
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Health check
        r_health = await client.get("/health")
        print("1. GET /health:", r_health.status_code, r_health.json())
        assert r_health.status_code == 200

        # 2. RAG Retrieval test
        query = "How do I fix low hydraulic pressure in HP-5000 pump?"
        r_rag = await client.post("/rag/retrieve", json={"query": query, "top_k": 3})
        print("\n2. POST /rag/retrieve status:", r_rag.status_code)
        
        data = r_rag.json()
        print(f"   Query: '{data['query']}'")
        print(f"   Retrieved {data['retrieved_count']} chunks:")
        for idx, chunk in enumerate(data['retrieved_chunks']):
            print(f"   [{idx+1}] Document: {chunk['document_filename']} | Similarity Score: {chunk['similarity_score']}")
            print(f"       Snippet: {chunk['text'][:100]}...")

        print("\n3. Constructed RAG Context preview:")
        print(data['constructed_context'][:250] + "...\n")

    print("✅ Exercise 3 RAG Service Test Completed Successfully!")


if __name__ == "__main__":
    asyncio.run(test_rag_service())
