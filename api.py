from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
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