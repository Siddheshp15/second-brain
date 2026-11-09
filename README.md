# 🧠 Second Brain: Document Q&A with RAG

Upload PDFs or TXT files and ask questions in plain English. Answers come
only from your documents, with file and page citations. If the answer isn't
in the documents, the app says so instead of guessing.

![Cited answer](screenshots/answer.png)
![Sources panel](screenshots/sources.png)
![Not found handling](screenshots/not_found.png)

## How it works

Upload -> extract text (PyMuPDF) -> clean -> chunk (500 words, 50 overlap)
-> embed (all-MiniLM-L6-v2) -> store in ChromaDB (metadata: file, page)

Question -> embed -> retrieve top 4 chunks -> LLM answers using ONLY those
chunks -> answer + citations

- **Grounded answering:** the prompt restricts the model to the retrieved
  passages and requires the exact reply "Not found in the documents." when the
  answer is missing.
- **Citations:** every chunk keeps its file name and page number, shown under
  each answer.

## Tech stack

Python, PyMuPDF, sentence-transformers, ChromaDB, FastAPI, Streamlit,
Groq API (open-weight LLM, free tier)

## Results

Evaluated on 30 hand-checked questions (24 answerable, 6 unanswerable) about
one research paper (a 7-page paper on GPU cluster scheduling).

| Chunk size (words) | Chunks | Hit rate @4 | MRR   |
|--------------------|--------|-------------|-------|
| 300                | 20     | 79.2%       | 0.642 |
| **500**            | 14     | **91.7%**   | 0.736 |
| 800                | 8      | 62.5%       | 0.493 |

- **"Not found" accuracy:** 6/6 unanswerable questions correctly refused
- **Answer correctness:** 87.5% (21/24, checked manually). All 3 errors were
  wrongful refusals, not made-up answers.
- **Average latency:** about 8.9 s per question (free API tier, includes
  rate-limit retries)

Hit rate @4 = how often the page containing the answer is among the 4
retrieved chunks. MRR = how high the correct page ranks on average.

## Run locally

1. Install libraries: