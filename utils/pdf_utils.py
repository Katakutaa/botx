import fitz  # PyMuPDF

def get_pdf_pages(file_path: str) -> int:
    """PDF fayldan bet sonini aniqlaydi"""
    try:
        doc = fitz.open(file_path)
        return len(doc)
    except Exception:
        return -1
