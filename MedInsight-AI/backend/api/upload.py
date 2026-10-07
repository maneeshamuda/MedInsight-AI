from fastapi import APIRouter, File, HTTPException, UploadFile

from backend import config, pipeline
from backend.database import repository
from backend.ocr.image_ocr import OCRUnavailable
from backend.schemas.response import AnalysisResponse, TextRequest

router = APIRouter()


def _finish(result: dict) -> dict:
    if config.STORE_RESULTS:
        result["analysis_id"] = repository.save(result)
    return result


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_file(file: UploadFile = File(...)):
    data = await file.read(config.MAX_UPLOAD_MB * 1024 * 1024 + 1)
    if len(data) > config.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {config.MAX_UPLOAD_MB} MB limit.")
    if not data:
        raise HTTPException(400, "Empty file.")
    try:
        return _finish(pipeline.analyze_bytes(data))
    except OCRUnavailable as e:
        raise HTTPException(503, str(e))
    except ValueError as e:
        raise HTTPException(415, str(e))


@router.post("/analyze/text", response_model=AnalysisResponse)
def analyze_text(req: TextRequest):
    if not req.text.strip():
        raise HTTPException(400, "Text is empty.")
    if len(req.text) > config.MAX_TEXT_CHARS:
        raise HTTPException(413, "Text too long.")
    return _finish(pipeline.analyze_text(req.text))
