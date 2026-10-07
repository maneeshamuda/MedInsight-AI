from backend.knowledge.terminology import condition_lexicon


def lookup(condition_key: str) -> str | None:
    # Seed table only. SNOMED CT is licensed: use a licensed release/UMLS in production.
    return (condition_lexicon().get(condition_key) or {}).get("snomed")
