import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from ingest.extract import extract_document
from ingest.chunk import chunk_document
from rag.embed import add_chunks, get_collection
from rag.answer import ask

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Second Brain")


class Question(BaseModel):
    question: str
    k: int = 4  # how many chunks to retrieve


@app.get("/")
def home():
    return {"status": "Second Brain API is running"}


@app.post("/upload")
def upload(file: UploadFile = File(...)):
    # Only allow PDF and TXT
    filename = os.path.basename(file.filename)  # strips any folder path, for safety
    ext = os.path.splitext(filename)[1].lower()
    if ext not in (".pdf", ".txt"):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported.")

    # Save the file to disk
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(file.file.read())

    # Extract -> chunk -> embed -> store
    pages = extract_document(path)
    if not pages:
        os.remove(path)
        raise HTTPException(
            status_code=400,
            detail="No readable text found. The file may be scanned or empty.",
        )
    chunks = chunk_document(pages)
    stored = add_chunks(chunks)

    return {"file": filename, "pages": len(pages), "chunks": stored}


@app.post("/ask")
def ask_question(q: Question):
    if not q.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        return ask(q.question, q.k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not get an answer: {e}")


@app.get("/documents")
def documents():
    data = get_collection().get(include=["metadatas"])
    summary = {}
    for meta in data["metadatas"]:
        name = meta["file"]
        summary.setdefault(name, {"file": name, "chunks": 0, "pages": set()})
        summary[name]["chunks"] += 1
        summary[name]["pages"].add(meta["page"])

    return [
        {"file": d["file"], "chunks": d["chunks"], "pages": len(d["pages"])}
        for d in summary.values()
    ]