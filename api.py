from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import json
import numpy as np
from app import process_document, ask
from src.chunker import extract_text, chunk_text

app = FastAPI(title="RAG Document Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class URLRequest(BaseModel):
    url: str

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    chunk_count = process_document(temp_path)
    os.remove(temp_path)
    return {"filename": file.filename, "chunks": chunk_count}

@app.post("/ingest-url")
async def ingest_url(request: URLRequest):
    if not (request.url.startswith("http://") or request.url.startswith("https://")):
        raise HTTPException(status_code=400, detail="Invalid URL — must start with http:// or https://")
    try:
        chunk_count = process_document(request.url)
        return {"source": request.url, "chunks": chunk_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(query: str):
    result = ask(query)
    return result

@app.get("/stats")
async def stats():
    from src.embedder import get_collection
    from app import ingested_sources
    return {
        "total_chunks": get_collection().count(),
        "embedding_model": "all-MiniLM-L6-v2",
        "llm": "llama-3.1-8b-instant via Groq",
        "search": "Hybrid (BM25 + Vector with RRF)",
        "ingested_sources": ingested_sources
    }

@app.get("/metrics")
async def get_metrics():
    metrics_file = "metrics.json"
    if not os.path.exists(metrics_file):
        return {"metrics": [], "summary": {}}
    with open(metrics_file) as f:
        metrics = json.load(f)
    if not metrics:
        return {"metrics": [], "summary": {}}

    latencies = [m["total_ms"] for m in metrics]
    p50 = round(float(np.percentile(latencies, 50)), 1)
    p95 = round(float(np.percentile(latencies, 95)), 1)
    total = len(metrics)
    cited = sum(1 for m in metrics if m["cited"])
    declined = sum(1 for m in metrics if m["declined"])

    return {
        "metrics": metrics[-20:],
        "summary": {
            "total_queries": total,
            "citation_rate": round(cited / total * 100, 1),
            "decline_rate": round(declined / total * 100, 1),
            "p50_latency_ms": p50,
            "p95_latency_ms": p95,
            "avg_retrieval_ms": round(sum(m["retrieval_ms"] for m in metrics) / total, 1),
            "avg_generation_ms": round(sum(m["generation_ms"] for m in metrics) / total, 1)
        }
    }