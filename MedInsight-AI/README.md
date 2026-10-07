# 🏥 MedInsight AI
Extract, structure, validate and explain medical reports & prescriptions — **without guessing**.

## Run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
sudo apt install tesseract-ocr          # only needed for images / scanned PDFs
uvicorn backend.main:app --reload       # http://localhost:8000  (API docs: /docs)
pytest -q
```
Docker: `docker compose up --build`

## What works now
- PDF (text layer + OCR fallback), images (Tesseract with confidence), plain text
- 22 lab tests (value, unit, reference range, status, LOINC) · conditions with negation/hedging handling (ICD-10, SNOMED CT seed)
- Prescriptions: drug (generic + Indian brands), strength, form, quantity, frequency (OD/BD/TDS/1-0-1/q8h/SOS), timing, duration, RxNorm
- Safety: confidence scoring, dose-max check, interaction check, contradictions, human-review flag
- Explanations in English, Hindi, Telugu, Spanish from verified facts only
- Website at `/` (drop or pick PDFs and photos, several at once, or take a photo on a phone; paste-text fallback; reference-range gauges; language switch; JSON download, print)

## Roadmap (from your architecture)
1. Swap/augment `nlp/lab_extractor.py` with a clinical Transformer NER; keep rules as validators.
2. Expand `data/terminology/*.json` (or load RxNorm/ICD-10 releases; SNOMED needs a licence).
3. Replace the interaction seed table with a licensed DDI source.
4. Auth, encryption at rest, audit logs, Postgres (`STORE_RESULTS=true` uses SQLite today).
5. React frontend (API is ready; `public/index.html` is a zero-build placeholder).

See `docs/safety.md`. Not a medical device; not clinically validated.
