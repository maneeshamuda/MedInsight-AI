from backend.nlp.clinical_ner import extract_conditions
from backend.nlp.lab_extractor import extract_labs


def extract_entities(text: str) -> dict:
    return {"labs": extract_labs(text), "conditions": extract_conditions(text)}
