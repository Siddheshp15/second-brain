from ingest.extract import extract_document

for p in extract_document("data/sample.pdf"):
    print(p["page"], "|", " ".join(p["text"].split()[:10]), "...")