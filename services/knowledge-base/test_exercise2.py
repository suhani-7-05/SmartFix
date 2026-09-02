"""
Test script for Exercise 2 Technical Knowledge Base pipeline.
"""

import asyncio
import os
from pathlib import Path
import sys

# Add project root and services directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
KB_DIR = PROJECT_ROOT / "services" / "knowledge-base"
sys.path.insert(0, str(KB_DIR))

from extractors import extract_text
from chunker import chunk_text
from embeddings import embed_text
from vector_store import VectorStore
import db


async def main():
    print("=== SmartFix Exercise 2 Pipeline Test ===")
    
    # 1. Init DB & Vector Store
    db.init_db()
    vector_store = VectorStore()
    print(f"Initial DB stats: {db.get_stats()}")
    print(f"Initial ChromaDB count: {vector_store.count()}")

    # 2. Sample Technical Document
    sample_text = """SmartFix Industrial Pump Maintenance Guide:
Model: HP-5000 Hydraulic Pressure Pump.

Safety Warning: Before servicing hydraulic pumps, ensure electrical lock-out and release residual system pressure.
Diagnostic Steps for Low Hydraulic Pressure:
1. Inspect fluid reservoir level and refill ISO VG 46 hydraulic oil if below min line.
2. Check inlet filter for debris accumulation or clogging.
3. Test primary pressure relief valve calibration (standard setpoint: 210 bar).
4. Inspect pump seal rings for fluid leakage or wear.

Spare Parts:
- Part #HP-SEAL-01: Viton High-Pressure Shaft Seal (Compatible with HP-5000)
- Part #HP-FLTR-05: 10-Micron Hydraulic Inlet Filter Element
- Part #HP-VALV-210: 210-Bar Pressure Relief Valve
"""
    
    # Write temporary file
    test_dir = PROJECT_ROOT / "data" / "documents" / "uploads"
    test_dir.mkdir(parents=True, exist_ok=True)
    test_file = test_dir / "test_pump_manual.txt"
    test_file.write_text(sample_text, encoding="utf-8")
    print(f"\n1. Saved sample technical document to {test_file}")

    # 3. Text Extraction
    extracted = extract_text(test_file, ".txt")
    print(f"2. Extracted {len(extracted)} characters of text.")

    # 4. Chunking
    chunks = chunk_text(extracted, chunk_size=300, overlap=50)
    print(f"3. Chunked into {len(chunks)} chunks:")
    for c in chunks:
        print(f"   - Chunk #{c.chunk_index}: Chars {c.char_start}..{c.char_end} ({len(c.text)} chars)")
        print(f"     Snippet: {c.text[:60]}...")

    # 5. Embeddings & Storage
    doc_rec = db.create_document("test_pump_manual.txt", ".txt", str(test_file))
    doc_id = doc_rec["id"]
    print(f"\n4. Created DB Document ID: {doc_id}")

    for c in chunks:
        vector, model_name, dims = await embed_text(c.text)
        vec_id = f"vec_{doc_id}_{c.chunk_index}"
        
        vector_store.add_chunk(
            vector_id=vec_id,
            embedding=vector,
            text=c.text,
            metadata={"document_id": doc_id, "chunk_index": c.chunk_index, "filename": "test_pump_manual.txt"}
        )
        
        db.create_chunk(
            document_id=doc_id,
            chunk_index=c.chunk_index,
            text=c.text,
            char_start=c.char_start,
            char_end=c.char_end,
            embedding_model=model_name,
            embedding_dimensions=dims,
            vector_id=vec_id
        )
        print(f"   Stored chunk #{c.chunk_index} vector {vec_id} (dims={dims}, model='{model_name}')")

    db.update_document(doc_id, status="processed", extracted_text_length=len(extracted), chunk_count=len(chunks))

    # 6. Verification
    print(f"\n5. Final DB stats: {db.get_stats()}")
    print(f"   Final ChromaDB count: {vector_store.count()}")
    
    vec_sample = vector_store.get_vector(f"vec_{doc_id}_0")
    print(f"   Retrieved vector metadata preview: {vec_sample}")

    print("\n[SUCCESS] Exercise 2 Pipeline Test Completed Successfully!")


if __name__ == "__main__":
    asyncio.run(main())
