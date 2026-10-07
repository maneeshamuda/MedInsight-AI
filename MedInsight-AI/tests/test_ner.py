from backend.nlp.clinical_ner import extract_conditions
from backend.nlp.lab_extractor import extract_labs


def lab(line):
    r = extract_labs(line)
    assert len(r) == 1, r
    return r[0]


def test_low_hemoglobin_with_report_range():
    f = lab("Hemoglobin 10.2 g/dL 12.0 - 15.5 L")
    assert f["status"] == "below_range" and f["report_flag"] == "below_range" and f["confidence"] >= 0.9


def test_generic_range_used_only_when_unit_matches():
    assert lab("Hemoglobin 10.2 g/dL")["reference_source"] == "generic_adult"
    f = lab("Hemoglobin 10.2")
    assert f["status"] == "unknown" and f["reference_range"] is None and f["confidence"] < 0.9


def test_upper_bound_range_and_cholesterol_variants():
    assert lab("Total Cholesterol 182 mg/dL < 200")["status"] == "within_range"
    assert lab("LDL Cholesterol 160 mg/dL 0 - 100")["name"].startswith("LDL")
    assert lab("Non-HDL Cholesterol 150 mg/dL")["name"].startswith("Non-HDL")


def test_implausible_value_lowers_confidence():
    f = lab("Hemoglobin 102 g/dL 12 - 16")
    assert "implausible_value" in f["flags"] and f["confidence"] < 0.9


def test_no_guessing_when_words_between_name_and_number():
    assert extract_labs("Hemoglobin test was ordered on 12 March") == []


def test_commas_in_value():
    assert lab("Platelet Count 2,40,000 /cumm 150000 - 450000")["numeric_value"] == 240000


def test_condition_negation_and_hedging():
    c = {x["key"]: x for x in extract_conditions(
        "Known case of hypertension. No evidence of diabetes mellitus. Findings suggest anemia. Family history of asthma.")}
    assert set(c) == {"hypertension", "anemia"}
    assert not c["hypertension"]["hedged"] and c["anemia"]["hedged"]
