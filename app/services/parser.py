import fitz  
import docx
import tempfile

def extract_text(filename: str, content_bytes: bytes) -> dict:
    """
    Extracts text and metrics from a PDF or DOCX file.
    
    Returns:
        {
            "text": Full document text,
            "num_pages": Number of pages (or 1 for DOCX),
            "useful_ratio": Ratio of non-empty lines/paragraphs (0 to 1)
        }
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=filename[-4:]) as tmp:
        tmp.write(content_bytes)
        tmp_path = tmp.name

    if filename.endswith(".pdf"):
        return _parse_pdf(tmp_path)
    elif filename.endswith(".docx"):
        return _parse_docx(tmp_path)

    raise ValueError("Unsupported file type. Only PDF and DOCX are supported.")

def _parse_pdf(path: str) -> dict:
    doc = fitz.open(path)
    full_text = []
    useful_lines = 0

    for page in doc:
        page_text = page.get_text()
        full_text.append(page_text)
        useful_lines += sum(1 for line in page_text.splitlines() if line.strip())

    full_text_str = "\n".join(full_text)
    total_lines = len(full_text_str.splitlines()) if full_text_str else 1
    useful_ratio = useful_lines / total_lines

    return {
        "text": full_text_str,
        "num_pages": len(doc),
        "useful_ratio": round(useful_ratio, 2)
    }

def _parse_docx(path: str) -> dict:
    doc = docx.Document(path)
    all_paragraphs = doc.paragraphs
    non_empty_paragraphs = [p.text for p in all_paragraphs if p.text.strip()]

    full_text_str = "\n".join(non_empty_paragraphs)
    total_paragraphs = len(all_paragraphs) if all_paragraphs else 1
    useful_ratio = len(non_empty_paragraphs) / total_paragraphs

    return {
        "text": full_text_str,
        "num_pages": 1,
        "useful_ratio": round(useful_ratio, 2)
    }
