def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into chunks of ~chunk_size words, overlapping by `overlap` words."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start = end - overlap  # step back so chunks overlap
    return chunks


def chunk_document(pages, chunk_size=500, overlap=50):
    """Turn pages into chunks, keeping file name and page number on each one."""
    result = []
    for p in pages:
        for j, chunk in enumerate(chunk_text(p["text"], chunk_size, overlap)):
            result.append({
                "id": f"{p['file']}_p{p['page']}_c{j}",  # unique ID, needed for the database later
                "file": p["file"],
                "page": p["page"],
                "text": chunk,
            })
    return result