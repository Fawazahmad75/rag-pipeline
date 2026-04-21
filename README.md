# DocPal Finance 🏦

A production-grade RAG (Retrieval-Augmented Generation) assistant for financial advisors, built on the Canadian Securities Course (CSC) material. Fully observable, evaluated, and CI-gated.

## Live Demo
- **Frontend:** https://docpal.streamlit.app
- **Backend API:** https://rag-pipeline-production-ccb0.up.railway.app/docs

## Architecture

```
User Query
    ↓
LangGraph Router (Llama 3.1 8B)
    ↓
factual → Hybrid Search (BM25 + Vector + RRF) → top 5 chunks
comparison → Hybrid Search → top 7 chunks
out_of_scope → polite decline (no LLM call)
    ↓
Cross-Encoder Reranker (ms-marco-MiniLM-L-6-v2)
    ↓
LangChain + Groq (Llama 3.1 8B) → Answer
    ↓
LangSmith Trace
```

## Key Features

- **Hybrid Search** — BM25 + Vector embeddings combined with Reciprocal Rank Fusion (RRF)
- **Cross-Encoder Reranker** — ms-marco-MiniLM-L-6-v2 reranks top 10 to top 5/7 for higher precision
- **LangGraph Router** — classifies queries as factual, comparison, or out_of_scope before retrieval
- **Prompt Versioning** — all prompts stored in prompts.yaml with version tracking
- **Citation Enforcement** — LLM explicitly declines when context does not support the answer
- **LangSmith Observability** — every chain call traced with inputs, outputs, latency, and tokens
- **RAGAS Evaluation** — 50 verified Q&A pairs, faithfulness scoring, CI gate at 0.75
- **GitHub Actions CI** — eval runs on every push, build fails if faithfulness drops
- **Persistent Metrics** — per-query metrics saved to metrics.json, P50/P95 latency on dashboard
- **URL Ingestion** — ingest any web page alongside PDFs and TXT files

## Evaluation Results

| Metric | Score |
|---|---|
| Faithfulness | 0.96 |
| Out of scope accuracy | 100% |
| Citation coverage | 76% |
| Golden dataset | 50 Q&A pairs |
| CI pipeline | Passing |

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Llama 3.1 8B via Groq |
| Embeddings | all-MiniLM-L6-v2 (384 dims) |
| Reranker | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| Vector DB | ChromaDB |
| Orchestration | LangGraph |
| LLM Framework | LangChain |
| Observability | LangSmith |
| Backend | FastAPI on Railway |
| Frontend | Streamlit Cloud |

## Project Structure

```
rag-pipeline/
├── src/
│   ├── chunker.py        # PDF/TXT/URL extraction + chunking (500 words, 100 overlap)
│   ├── embedder.py       # Lazy-loaded embeddings + ChromaDB
│   ├── retriever.py      # Hybrid search (BM25 + Vector + RRF) + cross-encoder reranker
│   ├── generator.py      # LangChain chains + prompt versioning + LangSmith tracing
│   └── graph.py          # LangGraph state machine router
├── evaluation/
│   ├── ground_truth.json # 50 verified Q&A pairs from CSC chapters
│   ├── ingest_docs.py    # Batch PDF ingestion script
│   ├── run_eval.py       # Eval script with CI exit codes
│   └── results.json      # Latest eval results
├── .github/
│   └── workflows/
│       └── eval.yml      # GitHub Actions CI pipeline
├── prompts.yaml          # Versioned prompt config
├── metrics.json          # Per-request metrics log
├── api.py                # FastAPI backend
├── app.py                # Core pipeline logic
└── ui.py                 # Streamlit dashboard
```

## Interview Talking Points

**Why cross-encoder reranker?**
Bi-encoder embeddings are fast but approximate. The cross-encoder evaluates the query and each chunk together as a pair, which is far more accurate. I added it after hybrid search to rerank the top 10 results down to 5 or 7.

**Why P50/P95 instead of average latency?**
Averages hide worst-case performance. P95 tells me what the slowest 5% of users experience. In production you optimize for P95, not average.

**Why CI evaluation gating?**
A prompt change can break your RAG just as badly as a code change. By running eval on every push and failing the build if faithfulness drops below 0.75, I treat AI quality the same way I treat test coverage.

**Why prompt versioning?**
If I change a prompt and quality degrades, I need to know exactly which version caused it. Versioning prompts in a config file makes them trackable and auditable.

**Why hybrid search with RRF?**
Pure vector search misses exact keyword matches. Pure BM25 misses semantic meaning. I caught that naive combination always prioritized vector results, so I implemented RRF to give both signals fair weight.

**Why LangGraph?**
Not all queries are equal. Factual queries need 5 chunks, comparison queries need 7, and out-of-scope queries should not hit the LLM at all. LangGraph lets me define this as a proper state machine with conditional routing.