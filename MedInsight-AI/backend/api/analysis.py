from fastapi import APIRouter, HTTPException

from backend import config
from backend.database import repository
from backend.schemas.response import AnalysisResponse

router = APIRouter()


@router.get("/analyses/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(analysis_id: str):
    if not config.STORE_RESULTS:
        raise HTTPException(404, "Result storage is disabled.")
    r = repository.get(analysis_id)
    if not r:
        raise HTTPException(404, "Not found.")
    r["analysis_id"] = analysis_id
    return r


@router.delete("/analyses/{analysis_id}")
def delete_analysis(analysis_id: str):
    if not config.STORE_RESULTS or not repository.delete(analysis_id):
        raise HTTPException(404, "Not found.")
    return {"deleted": True}
