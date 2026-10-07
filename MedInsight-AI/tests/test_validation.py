from backend.pipeline import analyze_text
from backend.safety.validation import check_dose
from backend.prescription.drug_extractor import extract_prescriptions


def test_clean_prescription_needs_no_review():
    r = analyze_text(open("data/sample_reports/sample_clean_prescription.txt").read())
    assert not r["safety"]["requires_human_review"] and len(r["prescriptions"]) == 3


def test_missing_strength_triggers_review():
    r = analyze_text("Rx\nTab. Pantoprazole 1-0-0 before food x 14 days")
    assert r["safety"]["requires_human_review"] and "prescriptions[0].strength" in r["safety"]["uncertain_fields"]
    assert "not clearly" in r["explanation"]["patient_friendly"] or "unclear" in r["explanation"]["patient_friendly"]


def test_major_interaction_detected():
    r = analyze_text("Tab Warfarin 5 mg OD x 30 days\nTab Ibuprofen 400 mg BD x 5 days")
    a = r["safety"]["interaction_alerts"]
    assert a and a[0]["severity"] == "major"


def test_dose_above_max_flagged():
    p, _ = extract_prescriptions("Tab Paracetamol 1000 mg QID x 5 days  Tab Paracetamol 1000 mg 5 times a day")
    assert any(check_dose(x) for x in p)  # 5 g/day > 4 g/day


def test_report_flag_mismatch_is_a_contradiction():
    r = analyze_text("Hemoglobin 14.0 g/dL 12.0 - 15.5 L")
    assert r["safety"]["contradictions"] and r["safety"]["requires_human_review"]


def test_conflicting_duplicate_medicine():
    r = analyze_text("Tab Metformin 500 mg BD x 30 days\nTab Metformin 1000 mg OD x 30 days")
    assert any(c["type"] == "duplicate_or_conflicting_medicine" for c in r["safety"]["contradictions"])


def test_empty_extraction_requires_review():
    r = analyze_text("Patient seen today, doing well.")
    assert r["safety"]["requires_human_review"]


def test_low_ocr_confidence_requires_review_and_scales_scores():
    hi = analyze_text("Tab Metformin 500 mg BD x 30 days")
    lo = analyze_text("Tab Metformin 500 mg BD x 30 days", ocr_confidence=0.6)
    assert lo["prescriptions"][0]["confidence"] < hi["prescriptions"][0]["confidence"]
    assert lo["safety"]["requires_human_review"]


def test_translations_preserve_facts():
    r = analyze_text("Tab Amoxicillin 500 mg TDS after food x 7 days")
    for lang in ("hi", "te", "es"):
        t = r["translations"][lang]["patient_friendly"]
        assert "500 mg" in t and "Amoxicillin" in t and "7" in t
