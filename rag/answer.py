from dotenv import load_dotenv
from openai import OpenAI
import os
from rag.retrieve import retrieve

load_dotenv()
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY"),
)

MODEL = "openai/gpt-oss-120b"  # free on Groq, good quality
NOT_FOUND = "Not found in the documents."

SYSTEM_PROMPT = f"""You answer questions using ONLY the numbered context passages provided.
Rules:
- Use only information from the passages. Never use outside knowledge.
- After each claim, cite the passage number in plain square brackets like [1] or [2]. Do not use any other citation format.
- If the passages do not contain the answer, reply with exactly: {NOT_FOUND}
- Keep the answer clear and concise."""


def build_context(chunks):
    parts = []
    for i, c in enumerate(chunks, start=1):
        parts.append(f"[{i}] (file: {c['file']}, page: {c['page']})\n{c['text']}")
    return "\n\n".join(parts)


def ask(question, k=4):
    """Return {"answer": str, "sources": [ {file, page, text}, ... ]}"""
    chunks = retrieve(question, k)
    if not chunks:
        return {"answer": "No documents uploaded yet.", "sources": []}

    user_message = f"Context:\n{build_context(chunks)}\n\nQuestion: {question}"

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=600,
        temperature=0,  # no randomness, more consistent answers
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    answer = response.choices[0].message.content.strip()

    if NOT_FOUND.lower() in answer.lower():
        return {"answer": NOT_FOUND, "sources": []}

    sources = [{"file": c["file"], "page": c["page"], "text": c["text"]} for c in chunks]
    return {"answer": answer, "sources": sources}