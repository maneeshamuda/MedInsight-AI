from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend import config
from backend.api import analysis, health, prescription, translation, upload

app = FastAPI(title="MedInsight AI", version=config.APP_VERSION,
              description="Extract, validate and explain medical reports and prescriptions. Never guesses.")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://localhost:3000"],
                   allow_methods=["*"], allow_headers=["*"])
for r in (health, upload, analysis, prescription, translation):
    app.include_router(r.router, prefix="/api")
# On Vercel the static site in public/ is served by the platform itself.
if config.FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=config.FRONTEND_DIR, html=True), name="frontend")
