import chromadb
from sentence_transformers import SentenceTransformer

DB_PATH = "data/chroma"
COLLECTION_NAME = "documents"

_model = None  # loaded once, reused after that


def get_model():
    """Load the embedding model the first time it's needed."""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def get_collection():
    """Open (or create) the ChromaDB collection saved on disk."""
    client = chromadb.PersistentClient(path=DB_PATH)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # compare chunks by cosine similarity
    )


def embed_texts(texts):
    """Turn a list of texts into a list of embeddings."""
    return get_model().encode(texts, show_progress_bar=False).tolist()


def add_chunks(chunks):
    """Embed chunks and store them in ChromaDB. Returns how many were stored."""
    if not chunks:
        return 0
    collection = get_collection()
    texts = [c["text"] for c in chunks]
    collection.upsert(  # upsert = add, or update if the ID already exists (no duplicates)
        ids=[c["id"] for c in chunks],
        documents=texts,
        embeddings=embed_texts(texts),
        metadatas=[{"file": c["file"], "page": c["page"]} for c in chunks],
    )
    return len(chunks)