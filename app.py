import os
import time
from src.chunker import extract_text, chunk_text
from src.embedder import embed_and_store, get_collection
from src.retriever import hybrid_search
from src.generator import generate_answer

all_chunks = []

def process_document(file_path):
    source_name = os.path.basename(file_path)
    text = extract_text(file_path)
    chunks = chunk_text(text)
    embed_and_store(chunks, source_name)
    all_chunks.extend(chunks)
    return len(chunks)

def ask(query):
    start = time.time()
    chunks, metadata = hybrid_search(query, all_chunks)
    retrieval_time = round((time.time() - start) * 1000, 1)
    
    start = time.time()
    answer = generate_answer(query, chunks)
    generation_time = round((time.time() - start) * 1000, 1)
    
    return {
        'answer': answer,
        'sources': metadata,
        'retrieval_ms': retrieval_time,
        'generation_ms': generation_time
    }