import os
import time
import json
from datetime import datetime
from src.chunker import extract_text, chunk_text
from src.embedder import embed_and_store, get_collection
from src.graph import build_graph

all_chunks = []
ingested_sources = {}
METRICS_FILE = "metrics.json"
SOURCES_FILE = "sources.json"

def load_sources():
    if os.path.exists(SOURCES_FILE):
        with open(SOURCES_FILE) as f:
            return json.load(f)
    return {}

def save_sources():
    with open(SOURCES_FILE, "w") as f:
        json.dump(ingested_sources, f, indent=2)

def load_metrics():
    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE) as f:
            return json.load(f)
    return []

def append_metric(metric: dict):
    metrics = load_metrics()
    metrics.append(metric)
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)

# Load sources on startup
ingested_sources = load_sources()

def process_document(source: str):
    if source.startswith("http://") or source.startswith("https://"):
        source_name = source
    else:
        source_name = os.path.basename(source)

    text = extract_text(source)
    chunks = chunk_text(text)
    embed_and_store(chunks, source_name)
    all_chunks.extend(chunks)

    ingested_sources[source_name] = {
        "chunks": len(chunks),
        "ingested_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    save_sources()

    return len(chunks)

def ask(query: str):
    start_total = time.time()
    graph = build_graph(all_chunks)
    result = graph.invoke({
        "query": query,
        "query_type": "",
        "chunks": [],
        "metadata": [],
        "answer": "",
        "declined": False,
        "cited": False,
        "prompt_version": "",
        "retrieval_ms": 0.0,
        "generation_ms": 0.0,
        "trace_url": ""
    })
    total_ms = round((time.time() - start_total) * 1000, 1)

    # Save metric
    append_metric({
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "query_type": result.get("query_type", ""),
        "retrieval_ms": result.get("retrieval_ms", 0),
        "generation_ms": result.get("generation_ms", 0),
        "total_ms": total_ms,
        "cited": result.get("cited", False),
        "declined": result.get("declined", False),
        "prompt_version": result.get("prompt_version", "")
    })

    result["sources"] = result.pop("metadata", [])
    result["total_ms"] = total_ms
    return result