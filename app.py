import os
import time
from src.chunker import extract_text, chunk_text
from src.embedder import embed_and_store, get_collection
from src.graph import build_graph
from dotenv import load_dotenv
load_dotenv()

os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "false")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "docpal-finance")

all_chunks = []
ingested_sources = {}

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

    return len(chunks)

def ask(query: str):
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
    # Rename metadata to sources for API consistency
    result["sources"] = result.pop("metadata", [])
    return result