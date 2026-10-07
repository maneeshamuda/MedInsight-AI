from backend import config


def apply_ocr_factor(items: list[dict], ocr_conf: float) -> None:
    """Scale item confidence by OCR quality (1.0 for digital text)."""
    if ocr_conf >= 1.0:
        return
    for it in items:
        it["confidence"] = round(it["confidence"] * max(ocr_conf, 0.0), 2)


def meets_threshold(conf: float, threshold: float | None = None) -> bool:
    return round(conf, 2) >= (config.CONFIDENCE_THRESHOLD if threshold is None else threshold)
