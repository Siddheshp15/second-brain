from ingest.extract import extract_document
from ingest.chunk import chunk_document
from rag.embed import add_chunks, get_collection, embed_texts

# 1. Ingest the sample file
pages = extract_document("data/sample.pdf")
chunks = chunk_document(pages)
stored = add_chunks(chunks)
print("Chunks stored:", stored)

# 2. Check what's in the database
collection = get_collection()
print("Total in database:", collection.count())

# 3. Try a search
question = "How is the job priority score calculated?"
results = collection.query(
    query_embeddings=embed_texts([question]),
    n_results=3,
)

print("\nQuestion:", question)
for i in range(3):
    meta = results["metadatas"][0][i]
    dist = results["distances"][0][i]
    text = results["documents"][0][i]
    print(f"\n#{i+1} | {meta['file']} | page {meta['page']} | distance {dist:.3f}")
    print(text[:200], "...")