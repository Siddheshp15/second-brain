import os
import re
import fitz  # PyMuPDF


def clean_text(text):
    """Tidy up messy text from PDFs."""
    text = text.replace("\x00", " ")        # remove null characters
    text = re.sub(r"-\n(\w)", r"\1", text)  # join words split across lines: "inter-\nnational" -> "international"
    text = re.sub(r"\s+", " ", text)        # collapse all whitespace/newlines into single spaces
    return text.strip()


def extract_pdf(path):
    """Return a list of pages: [{"file", "page", "text"}, ...]"""
    filename = os.path.basename(path)
    pages = []
    doc = fitz.open(path)
    for i, page in enumerate(doc):
        text = clean_text(page.get_text())
        if text:  # skip empty pages
            pages.append({"file": filename, "page": i + 1, "text": text})
    doc.close()
    return pages


def extract_txt(path):
    """A TXT file has no pages, so we treat it as page 1."""
    filename = os.path.basename(path)
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = clean_text(f.read())
    return [{"file": filename, "page": 1, "text": text}] if text else []


def extract_document(path):
    """Pick the right extractor based on file type."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return extract_pdf(path)
    if ext == ".txt":
        return extract_txt(path)
    raise ValueError(f"Unsupported file type: {ext}")