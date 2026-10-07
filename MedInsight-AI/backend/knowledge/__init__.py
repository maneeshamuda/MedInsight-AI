"""Knowledge normalisation: attach standard codes to extracted entities."""
from backend.knowledge import icd10, rxnorm, snomed


def normalize(findings: list[dict], conditions: list[dict], prescriptions: list[dict]) -> None:
    for c in conditions:
        c["icd10"] = icd10.lookup(c["key"])
        c["snomed_ct"] = snomed.lookup(c["key"])
    for p in prescriptions:
        r = rxnorm.lookup_drug(p["generic_key"])
        p["rxnorm_id"] = r["code"] if r else None
        p["code_system"] = r["code_system"] if r else None
    # findings already carry LOINC from the lab lexicon
