"""Aggregate every safety signal into one decision. The generative layer never overrides this."""
from backend import config


def decide(ocr_conf: float, findings, conditions, prescriptions, uncertain, contradictions) -> tuple[bool, list[str]]:
    reasons = []
    if ocr_conf < config.MIN_OCR_CONFIDENCE:
        reasons.append(f"Low OCR quality ({ocr_conf:.0%}); text may have been misread.")
    if not (findings or conditions or prescriptions):
        reasons.append("No medical entities could be extracted.")
    n_rx = sum(1 for p in prescriptions if p["needs_review"])
    if n_rx:
        reasons.append(f"{n_rx} medicine entr{'y' if n_rx == 1 else 'ies'} below confidence threshold or missing required fields (strength/frequency).")
    n_lab = sum(1 for f in findings if f["needs_review"])
    if n_lab:
        reasons.append(f"{n_lab} lab result(s) need verification.")
    n_c = sum(1 for c in conditions if c["needs_review"])
    if n_c:
        reasons.append(f"{n_c} condition mention(s) are hedged or uncertain.")
    if contradictions:
        reasons.append(f"{len(contradictions)} internal contradiction(s) detected.")
    return bool(reasons), reasons
