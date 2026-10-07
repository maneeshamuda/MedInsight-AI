from pydantic import BaseModel


class DocumentInfo(BaseModel):
    type: str
    language: str
    source: str
    confidence: float
    ocr_confidence: float
    notes: list[str] = []


class Finding(BaseModel):
    name: str
    value: str
    unit: str | None = None
    reference_range: str | None = None
    reference_source: str | None = None
    status: str
    report_flag: str | None = None
    loinc: str | None = None
    confidence: float
    flags: list[str] = []
    needs_review: bool = False
    source_text: str | None = None


class Condition(BaseModel):
    name: str
    icd10: str | None = None
    snomed_ct: str | None = None
    confidence: float
    hedged: bool = False
    needs_review: bool = False
    source_text: str | None = None
