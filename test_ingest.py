from ingest.extract import extract_document
from ingest.chunk import chunk_document

pages = extract_document("data/sample.pdf")
print("Pages with text:", len(pages))

chunks = chunk_document(pages)
print("Total chunks:", len(chunks))

print("\n--- First chunk ---")
print("ID:", chunks[0]["id"])
print("Page:", chunks[0]["page"])
print("Words:", len(chunks[0]["text"].split()))
print(chunks[0]["text"][:300], "...")