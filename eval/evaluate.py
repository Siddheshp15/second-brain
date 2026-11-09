import json
import time
import chromadb

from ingest.extract import extract_document
from ingest.chunk import chunk_document
from rag.embed import embed_texts
from rag.answer import ask, NOT_FOUND

DOC = "data/sample.pdf"
K = 4

with open("eval/questions.json", encoding="utf-8") as f:
    questions = json.load(f)

answerable = [q for q in questions if q["answerable"]]
unanswerable = [q for q in questions if not q["answerable"]]


def build_collection(chunk_size, overlap):
    """Temporary in-memory collection, so your real database isn't touched."""
    client = chromadb.EphemeralClient()
    col = client.get_or_create_collection(
        f"eval_{chunk_size}", metadata={"hnsw:space": "cosine"}
    )
    chunks = chunk_document(extract_document(DOC), chunk_size, overlap)
    texts = [c["text"] for c in chunks]
    col.add(
        ids=[c["id"] for c in chunks],
        documents=texts,
        embeddings=embed_texts(texts),
        metadatas=[{"file": c["file"], "page": c["page"]} for c in chunks],
    )
    return col, len(chunks)


def retrieval_metrics(col):
    hits, rr = 0, 0.0
    for q in answerable:
        res = col.query(
            query_embeddings=embed_texts([q["question"]]),
            n_results=min(K, col.count()),
        )
        pages = [m["page"] for m in res["metadatas"][0]]
        if q["page"] in pages:
            hits += 1
            rr += 1 / (pages.index(q["page"]) + 1)
    n = len(answerable)
    return hits / n, rr / n


# ---------- Part 1: chunk size experiment (retrieval only, no LLM calls) ----------
print(f"\nChunk size experiment ({len(answerable)} answerable questions, k={K})")
print(f"{'chunk size':<12}{'chunks':<9}{'hit@4':<10}{'MRR':<8}")
for size in (300, 500, 800):
    col, n_chunks = build_collection(size, size // 10)
    hit, mrr = retrieval_metrics(col)
    print(f"{size:<12}{n_chunks:<9}{hit*100:<10.1f}{mrr:<8.3f}")

# ---------- Part 2: full pipeline (uses the LLM, free tier is rate-limited) ----------
print("\nFull pipeline run (this takes a few minutes because of free-tier limits)...")


def ask_with_retry(q, tries=4):
    for attempt in range(tries):
        try:
            return ask(q)
        except Exception as e:
            if "429" in str(e) and attempt < tries - 1:
                time.sleep(25)  # rate limited: wait, then retry
            else:
                raise


results, latencies = [], []
refused_ok, refused_wrong = 0, 0

for q in questions:
    start = time.time()
    out = ask_with_retry(q["question"])
    latencies.append(time.time() - start)
    refused = out["answer"].strip() == NOT_FOUND

    if not q["answerable"] and refused:
        refused_ok += 1
    if q["answerable"] and refused:
        refused_wrong += 1

    results.append({
        "question": q["question"],
        "expected": q["answer"],
        "answerable": q["answerable"],
        "got": out["answer"],
        "refused": refused,
        "correct": None,  # you fill this in by hand: true / false
    })
    time.sleep(8)  # stay under the free-tier token limits

with open("eval/results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n'Not found' accuracy: {refused_ok}/{len(unanswerable)} unanswerable questions refused")
print(f"Wrongly refused answerable questions: {refused_wrong}/{len(answerable)}")
print(f"Average latency per question: {sum(latencies)/len(latencies):.1f} s")
print("Answers saved to eval/results.json. Now check them by hand.")