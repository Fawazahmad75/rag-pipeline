from sentence_transformers import SentenceTransformer
import chromadb

_model = None
_client = None
_collection = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path="./chroma_db")
        _collection = _client.get_or_create_collection("documents")
    return _collection

def embed_and_store(chunks, source_name):
    model = get_model()
    collection = get_collection()
    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk).tolist()
        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            ids=[f"{source_name}_{i}"],
            metadatas=[{"source": source_name}]
        )
    return len(chunks)