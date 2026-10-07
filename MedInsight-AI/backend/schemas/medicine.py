from pydantic import BaseModel


class Prescription(BaseModel):
    medicine_name: str
    generic_name: str
    rxnorm_id: str | None = None
    code_system: str | None = None
    strength: str | None = None
    form: str | None = None
    quantity: str | None = None
    frequency: str | None = None
    timing: str | None = None
    duration: str | None = None
    confidence: float
    missing_fields: list[str] = []
    warnings: list[str] = []
    needs_review: bool = False
    source_text: str | None = None
