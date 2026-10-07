"""End-to-end orchestration: ingest -> NLP -> prescription -> normalise -> safety -> explain -> translate."""
from backend import config
from backend.explanation.patient_explanation import build_patient_text
from backend.explanation.summarizer import build_summary
from backend.knowledge import normalize
from backend.nlp.entity_extractor import extract_entities
from backend.nlp.medical_classifier import classify_document, detect_language
from backend.ocr.ingest import ingest
from backend.ocr.preprocessing import clean_text
from backend.prescription.drug_extractor import extract_prescriptions
from backend.safety.confidence import apply_ocr_factor
from backend.safety.contradiction import find_contradictions
from backend.safety.human_review import decide
from backend.safety.interaction_checker import check_interactions
from backend.safety.validation import validate
from backend.translation.translator import available, labels
from backend.wellness import build_wellness


def analyze_text(text: str, ocr_confidence: float = 1.0, source: str = "text", notes: list[str] | None = None) -> dict:
    text = clean_text(text)
    ents = extract_entities(text)
    findings, conditions = ents["labs"], ents["conditions"]
    prescriptions, rx_notes = extract_prescriptions(text)

    apply_ocr_factor(findings + conditions + prescriptions, ocr_confidence)
    normalize(findings, conditions, prescriptions)

    v = validate(findings, conditions, prescriptions)
    contradictions = find_contradictions(findings, prescriptions)
    interactions = check_interactions(prescriptions)
    review, reasons = decide(ocr_confidence, findings, conditions, prescriptions, v["uncertain_fields"], contradictions)

    items = findings + conditions + prescriptions
    doc_conf = round(sum(i["confidence"] for i in items) / len(items), 2) if items else 0.0

    translations = {}
    for lang in available():
        translations[lang] = {
            "summary": build_summary(findings, prescriptions, lang),
            "patient_friendly": build_patient_text(findings, conditions, prescriptions, interactions, review, lang),
            "labels": labels(lang),
        }
    return {
        "document": {"type": classify_document(len(findings), len(prescriptions), text), "language": detect_language(text),
                     "source": source, "confidence": doc_conf, "ocr_confidence": round(ocr_confidence, 2), "notes": notes or []},
        "clinical_findings": findings,
        "conditions": conditions,
        "prescriptions": prescriptions,
        "safety": {"requires_human_review": review, "review_reasons": reasons, "interaction_alerts": interactions,
                   "dose_alerts": v["dose_alerts"], "contradictions": contradictions,
                   "uncertain_fields": v["uncertain_fields"], "notes": rx_notes},
        "explanation": {k: translations["en"][k] for k in ("summary", "patient_friendly")},
        "translations": translations,
        "wellness": build_wellness(findings, conditions, prescriptions),
    }


def analyze_bytes(data: bytes) -> dict:
    ing = ingest(data)
    return analyze_text(ing.text, ing.ocr_confidence, ing.source, ing.notes)
