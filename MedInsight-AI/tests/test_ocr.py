import pytest
from backend.ocr.ingest import ingest
from backend.ocr.preprocessing import clean_text


def test_clean_text_normalises_dashes_and_spaces():
    assert clean_text("Hb   10.2 \u2013  12\u201416 \u00a0g/dL") == "Hb 10.2 - 12-16 g/dL"


def test_ingest_plain_text():
    r = ingest(b"Hemoglobin 10.2 g/dL")
    assert r.source == "text" and r.ocr_confidence == 1.0


def test_ingest_rejects_binary_garbage():
    with pytest.raises(ValueError):
        ingest(b"\xff\xfe\x00\x01garbage\x80\x81")


def test_digital_pdf_text_layer(tmp_path):
    reportlab = pytest.importorskip("reportlab")
    from reportlab.pdfgen import canvas
    p = tmp_path / "r.pdf"
    c = canvas.Canvas(str(p))
    c.drawString(72, 750, "Hemoglobin 10.2 g/dL 12.0 - 15.5 L and some padding text here")
    c.save()
    r = ingest(p.read_bytes())
    assert r.source == "pdf" and "Hemoglobin" in r.text and r.ocr_confidence == 1.0
