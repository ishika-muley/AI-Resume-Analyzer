"""Extract plain text from PDF / DOCX files."""
import pdfplumber, docx

class ParseError(Exception):
    pass

def extract_text(path: str, ext: str) -> str:
    try:
        if ext == "pdf":
            with pdfplumber.open(path) as pdf:
                text = "\n".join((p.extract_text() or "") for p in pdf.pages)
        elif ext == "docx":
            d = docx.Document(path)
            parts = [p.text for p in d.paragraphs]
            for t in d.tables:
                for row in t.rows:
                    parts.append(" | ".join(c.text for c in row.cells))
            text = "\n".join(parts)
        else:
            raise ParseError("Unsupported file type.")
    except ParseError:
        raise
    except Exception as e:
        raise ParseError(f"Could not read the file; it may be corrupted or password-protected ({type(e).__name__}).")
    text = text.strip()
    if len(text) < 30:
        raise ParseError("No readable text found. Scanned/image-only resumes are not supported.")
    return text


def extract_links(path: str, ext: str) -> list:
    """Return http(s) hyperlink URLs embedded in the file (clickable text has no URL in the extracted text)."""
    links = set()
    try:
        if ext == "pdf":
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    for h in page.hyperlinks:
                        if h.get("uri"): links.add(h["uri"])
        else:
            for r in docx.Document(path).part.rels.values():
                if r.reltype.endswith("/hyperlink"): links.add(r.target_ref)
    except Exception:
        pass
    return sorted(l for l in links if l.startswith("http"))
