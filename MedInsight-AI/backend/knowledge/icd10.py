from backend.knowledge.terminology import condition_lexicon


def lookup(condition_key: str) -> str | None:
    return (condition_lexicon().get(condition_key) or {}).get("icd10")
