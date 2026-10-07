import pytest
from backend.prescription.drug_extractor import extract_prescriptions
from backend.prescription.frequency_parser import parse_frequency


def one(line):
    items, _ = extract_prescriptions(line)
    assert len(items) == 1, items
    return items[0]


def test_full_prescription_high_confidence():
    p = one("Tab. Amoxicillin 500 mg 1 tab TDS after food x 7 days")
    assert (p["strength"], p["frequency"], p["timing"], p["duration"], p["form"]) == \
        ("500 mg", "3 times daily", "after meals", "7 days", "tablet")
    assert p["confidence"] >= 0.9 and not p["missing_fields"]


def test_missing_strength_is_never_invented():
    p = one("Tab. Pantoprazole 1-0-0 before food x 14 days")
    assert p["strength"] is None and p["missing_fields"] == ["strength"] and p["confidence"] < 0.9


@pytest.mark.parametrize("txt,norm,times", [
    ("OD", "once daily", 1), ("BD", "twice daily", 2), ("TDS", "3 times daily", 3), ("QID", "4 times daily", 4),
    ("1-0-1", "twice daily", 2), ("1-1-1", "3 times daily", 3), ("q8h", "every 8 hours", 3),
    ("every 6 hours", "every 6 hours", 4), ("2 times a day", "twice daily", 2), ("once daily", "once daily", 1)])
def test_frequency(txt, norm, times):
    f = parse_frequency(txt)
    assert f["normalized"] == norm and f["times_per_day"] == times


def test_sos_is_as_needed():
    f = parse_frequency("SOS")
    assert f["as_needed"] and f["times_per_day"] is None


def test_brand_name_maps_to_generic_and_rxnorm():
    p = one("Tab Dolo 650 mg 1-1-1 x 3 days")
    assert p["generic_key"] == "paracetamol"


def test_allergy_context_is_not_a_prescription():
    items, notes = extract_prescriptions("Allergic to amoxicillin.")
    assert items == [] and notes


def test_syrup_strength_per_volume_not_read_as_quantity():
    p = one("Syp Paracetamol 250 mg/5 ml 5 ml TDS x 3 days")
    assert p["strength"] == "250 mg/5 ml" and p["quantity"] == "5 ml" and p["strength_mg"] is None


def test_multiple_drugs_one_line_and_continuation():
    items, _ = extract_prescriptions("Metformin 500 mg BD Atorvastatin 10 mg OD\nTab Amlodipine 5 mg\n1-0-0 x 30 days")
    names = {i["generic_key"]: i for i in items}
    assert names["metformin"]["frequency"] == "twice daily" and names["atorvastatin"]["frequency"] == "once daily"
    assert names["amlodipine"]["frequency"] == "once daily" and names["amlodipine"]["duration"] == "30 days"
