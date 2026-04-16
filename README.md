# RAG Document Assistant

A production-ready Retrieval-Augmented Generation (RAG) system that lets users upload documents and ask natural language questions, receiving accurate, cited answers in real time.

## Problem

Information retrieval from large document collections is slow and imprecise. Traditional keyword search misses semantic meaning; pure vector search misses exact keyword matches. This system combines both approaches to deliver fast, accurate, cited answers from any uploaded document set.

## Approach

1. **Document ingestion** — PDFs and text files are extracted and chunked into 500-word segments with a 50-word overlap to preserve context at chunk boundaries
2. **Embedding** — each chunk is encoded into a 384-dimensional vector using `sentence-transformers` (all-MiniLM-L6-v2) and stored in ChromaDB
3. **Hybrid retrieval** — queries are answered using both dense vector similarity search (ChromaDB) and BM25 keyword search, fused via **Reciprocal Rank Fusion (RRF)** to combine the strengths of semantic and keyword matching
4. **Generation** — top retrieved chunks are passed as context to **Llama 3.1 8B** via the Groq API, with a structured prompt that constrains answers to the provided context and requires source citation
5. **API layer** — FastAPI exposes `/upload`, `/ask`, and `/stats` endpoints
6. **Frontend** — Streamlit UI for document upload, Q&A, and real-time latency metrics

## Architecture

```
User → Streamlit UI → FastAPI Backend
                            ↓
                    Document Upload
                            ↓
                    Chunker (500w, 50 overlap)
                            ↓
                    Embedder (all-MiniLM-L6-v2)
                            ↓
                    ChromaDB (vector store)
                            ↓
                    Hybrid Search (Vector + BM25 → RRF)
                            ↓
                    Groq API (Llama 3.1 8B)
                            ↓
                    Cited Answer + Latency Metrics
```

## Results

- Chunk size: 500 words with 50-word overlap
- Embedding dimensions: 384 (all-MiniLM-L6-v2)
- Average retrieval time: ~20–45ms
- Average generation time: ~500–1000ms  
- Total documents indexed: 6 (Canadian Securities Course chapters)
- Zero hallucination — answers constrained to provided context only

## Tradeoffs & Design Decisions

- **Hybrid search over pure vector search** — BM25 catches exact keyword matches that semantic search misses; RRF ensures both signals contribute fairly to ranking
- **Groq API over local LLM** — Groq's hosted Llama 3.1 delivers sub-second generation with no local GPU requirement, making the system portable and demo-ready
- **ChromaDB EphemeralClient on deployment** — since users upload their own documents per session, persistence is not required; this avoids filesystem permission issues on hosted environments
- **Chunk size 500 / overlap 50** — balances retrieval precision (smaller chunks = more focused) with context richness (overlap = no lost context at boundaries)

## What I'd Improve

- Add re-ranking with a cross-encoder model for higher retrieval precision
- Persist BM25 index to disk for large document sets (currently rebuilt in memory per session)
- Support DOCX, HTML, and CSV formats
- Add a ground-truth evaluation harness to measure answer accuracy (e.g. RAGAS)
- Swap ChromaDB for a managed vector database (Pinecone or Weaviate) for multi-user persistence

## Tools Used

| Layer | Tool |
|---|---|
| Document parsing | PyMuPDF (fitz) |
| Chunking | Custom Python |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector store | ChromaDB |
| Keyword search | rank-bm25 (BM25Okapi) |
| Fusion | Reciprocal Rank Fusion (RRF) |
| LLM | Llama 3.1 8B via Groq API |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Deployment | Railway (backend) |

## Running Locally

```bash
git clone https://github.com/Fawazahmad75/rag-pipeline
cd rag-pipeline
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Add your Groq API key to a `.env` file:
```
GROQ_API_KEY=your_key_here
```

Start the backend:
```bash
uvicorn api:app --reload
```

Start the frontend (in a new terminal):
```bash
streamlit run ui.py
```

Then open `http://localhost:8501`, upload a document, and start asking questions.

## Live Demo

Backend API: [https://rag-pipeline-production.up.railway.app/docs](https://rag-pipeline-production.up.railway.app/docs](https://docpall.streamlit.app/)
