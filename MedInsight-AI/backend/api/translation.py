from fastapi import APIRouter

from backend.translation.translator import available

router = APIRouter()


@router.get("/languages")
def languages():
    return available()
