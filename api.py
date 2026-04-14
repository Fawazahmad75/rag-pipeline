from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from app import process_document, ask

app = FastAPI(title="RAG Document Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    chunk_count = process_document(temp_path)
    os.remove(temp_path)
    return {"filename": file.filename, "chunks": chunk_count}

@app.post("/ask")
async def ask_question(query: str):
    result = ask(query)
    return result

@app.get("/stats")
async def stats():
    from src.embedder import get_collection
    return {
        "total_chunks": get_collection().count(),
        "embedding_model": "all-MiniLM-L6-v2",
        "llm": "llama-3.1-8b-instant via Groq",
        "search": "Hybrid (BM25 + Vector with RRF)"
    }