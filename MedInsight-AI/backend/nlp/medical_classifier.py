"""Document-type and script detection (heuristic; swap for a trained classifier later)."""
import re


def classify_document(n_labs: int, n_meds: int, text: str) -> str:
    if n_labs and n_meds:
        return "mixed"
    if n_labs:
        return "lab_report"
    if n_meds:
        return "prescription"
    if re.search(r"\b(rx|tablet|capsule|laborator|specimen|reference range)\b", text, re.I):
        return "medical_document_unparsed"
    return "unknown"


def detect_language(text: str) -> str:
    deva = len(re.findall(r"[\u0900-\u097f]", text))
    tel = len(re.findall(r"[\u0c00-\u0c7f]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    if tel > latin and tel >= deva:
        return "te"
    if deva > latin:
        return "hi"
    return "en"
