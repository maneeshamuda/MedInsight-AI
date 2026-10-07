from fastapi import APIRouter, HTTPException

from backend import config, pipeline
from backend.schemas.response import TextRequest

router = APIRouter()


@router.post("/prescriptions/parse")
def parse_prescription(req: TextRequest):
    """Prescription-only view: medicines + interaction/dose/review decisions."""
    if not req.text.strip() or len(req.text) > config.MAX_TEXT_CHARS:
        raise HTTPException(400, "Provide text between 1 and %d characters." % config.MAX_TEXT_CHARS)
    r = pipeline.analyze_text(req.text)
    return {"prescriptions": r["prescriptions"], "safety": r["safety"]}
