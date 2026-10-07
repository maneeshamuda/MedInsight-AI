from backend.knowledge.terminology import drug_lexicon


def lookup_drug(generic_key: str) -> dict | None:
    d = drug_lexicon().get(generic_key)
    if not d or not d.get("rxnorm"):
        return None
    return {"code_system": "RxNorm (ingredient)", "code": d["rxnorm"]}
