from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("documents")

def embed_and_store(chunks, source_name):
    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk).tolist()
        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            ids=[f"{source_name}_{i}"],
            metadatas=[{"source": source_name}]
        )
    return len(chunks)

def get_collection():
    return collection

def get_model():
    return model