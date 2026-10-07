"""Central configuration. Override via environment variables / .env."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
TERMINOLOGY_DIR = DATA_DIR / "terminology"
FRONTEND_DIR = ROOT / "public"

# "Never Guess": items below this confidence go to human review.
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.90"))
MIN_OCR_CONFIDENCE = float(os.getenv("MIN_OCR_CONFIDENCE", "0.70"))
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))
MAX_TEXT_CHARS = int(os.getenv("MAX_TEXT_CHARS", "200000"))

# Health data: results are NOT persisted unless explicitly enabled.
STORE_RESULTS = os.getenv("STORE_RESULTS", "false").lower() == "true"
DB_PATH = os.getenv("DB_PATH", str(ROOT / "medinsight.db"))

TESSERACT_CMD = os.getenv("TESSERACT_CMD")  # optional path to tesseract binary
APP_VERSION = "0.1.0"
