import shutil

from fastapi import APIRouter

from backend import config

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "version": config.APP_VERSION,
            "tesseract_available": bool(config.TESSERACT_CMD or shutil.which("tesseract")),
            "confidence_threshold": config.CONFIDENCE_THRESHOLD, "store_results": config.STORE_RESULTS}
