"""Document ingestion: detect type by magic bytes, return text + OCR confidence."""
import io
from dataclasses import dataclass, field

from backend.ocr.image_ocr import ocr_image
from backend.ocr.pdf_parser import extract_pdf
from backend.ocr.preprocessing import clean_text

_IMG_MAGIC = (b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff", b"BM", b"II*\x00", b"MM\x00*")


@dataclass
class Ingested:
    text: str
    ocr_confidence: float
    source: str
    notes: list[str] = field(default_factory=list)


def _is_image(data: bytes) -> bool:
    return data.startswith(_IMG_MAGIC) or (data[:4] == b"RIFF" and data[8:12] == b"WEBP")


def ingest(data: bytes) -> Ingested:
    if data.startswith(b"%PDF-"):
        text, conf, notes = extract_pdf(data)
        return Ingested(clean_text(text), conf, "pdf", notes)
    if _is_image(data):
        from PIL import Image

        try:
            img = Image.open(io.BytesIO(data))
            img.load()
        except Exception as e:
            raise ValueError(f"Could not read image: {e}") from e
        text, conf = ocr_image(img)
        return Ingested(clean_text(text), conf, "image", [])
    try:
        return Ingested(clean_text(data.decode("utf-8")), 1.0, "text", [])
    except UnicodeDecodeError as e:
        raise ValueError("Unsupported file type. Upload a PDF, image (PNG/JPG/TIFF/WEBP) or UTF-8 text.") from e
