"""Tesseract OCR with per-word confidence (psm 6 keeps table rows on one line)."""
from backend import config
from backend.ocr.preprocessing import preprocess_image


class OCRUnavailable(RuntimeError):
    pass


def ocr_image(img) -> tuple[str, float]:
    """Return (text, mean_word_confidence in 0..1)."""
    try:
        import pytesseract
    except ImportError as e:  # pragma: no cover
        raise OCRUnavailable("pytesseract is not installed") from e
    if config.TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD
    img = preprocess_image(img)
    try:
        d = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config="--psm 6")
    except pytesseract.TesseractNotFoundError as e:
        raise OCRUnavailable("Tesseract binary not found. Install it or set TESSERACT_CMD.") from e
    lines: dict = {}
    confs: list[float] = []
    for i, word in enumerate(d["text"]):
        if not word.strip():
            continue
        c = float(d["conf"][i])
        if c < 0:
            continue
        key = (d["block_num"][i], d["par_num"][i], d["line_num"][i])
        lines.setdefault(key, []).append(word)
        confs.append(c)
    text = "\n".join(" ".join(w) for _, w in sorted(lines.items()))
    return text, (sum(confs) / len(confs) / 100.0 if confs else 0.0)
