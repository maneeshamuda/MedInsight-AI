from pydantic import BaseModel

from backend.schemas.medicine import Prescription
from backend.schemas.report import Condition, DocumentInfo, Finding


class Safety(BaseModel):
    requires_human_review: bool
    review_reasons: list[str] = []
    interaction_alerts: list[dict] = []
    dose_alerts: list[dict] = []
    contradictions: list[dict] = []
    uncertain_fields: list[str] = []
    notes: list[str] = []


class Explanation(BaseModel):
    summary: str
    patient_friendly: str


class AnalysisResponse(BaseModel):
    analysis_id: str | None = None
    document: DocumentInfo
    clinical_findings: list[Finding]
    conditions: list[Condition]
    prescriptions: list[Prescription]
    safety: Safety
    explanation: Explanation
    translations: dict[str, dict]
    wellness: dict = {}
    disclaimer: str = "Informational extraction only. Not a diagnosis or medical advice."


class TextRequest(BaseModel):
    text: str
