"""PDF text extraction. Digital PDFs use the embedded text layer; scans fall back to OCR."""
import io

from backend.ocr.image_ocr import OCRUnavailable, ocr_image


def extract_pdf(data: bytes) -> tuple[str, float, list[str]]:
    """Return (text, confidence 0..1, notes)."""
    from pypdf import PdfReader

    notes: list[str] = []
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            raise ValueError("Encrypted PDFs are not supported.")
        text = "\n".join((p.extract_text() or "") for p in reader.pages)
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Could not read PDF: {e}") from e

    if len(text.strip()) >= 30:
        return text, 1.0, notes

    notes.append("No text layer found; document treated as a scan and OCR was used.")
    try:
        import pypdfium2 as pdfium
    except ImportError as e:
        raise OCRUnavailable("Scanned PDF needs pypdfium2 + Tesseract for OCR.") from e
    pdf = pdfium.PdfDocument(data)
    texts, confs = [], []
    for page in pdf:
        t, c = ocr_image(page.render(scale=2.5).to_pil())
        texts.append(t)
        confs.append(c)
    return "\n".join(texts), (sum(confs) / len(confs) if confs else 0.0), notes
