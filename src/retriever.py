from rank_bm25 import BM25Okapi
from src.embedder import get_collection, get_model

def vector_search(query, n_results=5):
    model = get_model()
    collection = get_collection()
    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results['documents'][0], results['metadatas'][0]

def bm25_search(query, all_chunks, n_results=5):
    tokenized_chunks = [chunk.split() for chunk in all_chunks]
    bm25 = BM25Okapi(tokenized_chunks)
    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:n_results]
    return [all_chunks[i] for i in top_indices]

def hybrid_search(query, all_chunks, n_results=5):
    vector_results, metadata = vector_search(query, n_results)
    bm25_results = bm25_search(query, all_chunks, n_results)
    
    scores = {}
    for rank, chunk in enumerate(vector_results):
        scores[chunk] = scores.get(chunk, 0) + 1 / (rank + 1)
    for rank, chunk in enumerate(bm25_results):
        scores[chunk] = scores.get(chunk, 0) + 1 / (rank + 1)
    
    ranked = sorted(scores.keys(), key=lambda c: scores[c], reverse=True)
    return ranked[:n_results], metadata