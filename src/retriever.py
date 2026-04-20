from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
from src.embedder import get_collection, get_model

# Load cross-encoder once at module level (lazy would slow down first query)
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def vector_search(query, n_results=10):
    model = get_model()
    collection = get_collection()
    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results['documents'][0], results['metadatas'][0]

def bm25_search(query, all_chunks, n_results=10):
    if not all_chunks:
        return []
    tokenized_chunks = [chunk.split() for chunk in all_chunks]
    bm25 = BM25Okapi(tokenized_chunks)
    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:n_results]
    return [all_chunks[i] for i in top_indices]


def rerank(query, chunks, top_n=5):
    if not chunks:
        return chunks
    pairs = [[query, chunk] for chunk in chunks]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
    return [chunk for chunk, score in ranked[:top_n]]

def hybrid_search(query, all_chunks, n_results=5):
    if not all_chunks:
        # Fall back to pure vector search if no chunks in memory
        vector_results, metadata = vector_search(query, n_results=n_results)
        return vector_results, metadata
    
    vector_results, metadata = vector_search(query, n_results=10)
    bm25_results = bm25_search(query, all_chunks, n_results=10)
    
    scores = {}
    for rank, chunk in enumerate(vector_results):
        scores[chunk] = scores.get(chunk, 0) + 1 / (rank + 1)
    for rank, chunk in enumerate(bm25_results):
        scores[chunk] = scores.get(chunk, 0) + 1 / (rank + 1)
    
    top_10 = sorted(scores.keys(), key=lambda c: scores[c], reverse=True)[:10]
    top_5 = rerank(query, top_10, top_n=n_results)

    chunk_to_meta = dict(zip(vector_results, metadata))
    seen_sources = set()
    top_5_metadata = []
    for chunk in top_5:
        meta = chunk_to_meta.get(chunk, {})
        source = meta.get("source", "unknown")
        if source not in seen_sources:
            seen_sources.add(source)
            top_5_metadata.append(meta)

    return top_5, top_5_metadata