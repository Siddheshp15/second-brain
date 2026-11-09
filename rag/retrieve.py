from rag.embed import get_collection, embed_texts


def retrieve(question, k=4):
    """Find the k chunks most similar to the question."""
    collection = get_collection()
    total = collection.count()
    if total == 0:
        return []

    results = collection.query(
        query_embeddings=embed_texts([question]),
        n_results=min(k, total),
    )

    chunks = []
    for i in range(len(results["ids"][0])):
        chunks.append({
            "id": results["ids"][0][i],
            "file": results["metadatas"][0][i]["file"],
            "page": results["metadatas"][0][i]["page"],
            "text": results["documents"][0][i],
            "distance": results["distances"][0][i],
        })
    return chunks