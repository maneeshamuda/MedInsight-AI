| Method | Path | Purpose |
|---|---|---|
| POST | /api/analyze | multipart `file` (PDF/PNG/JPG/TIFF/WEBP/TXT) |
| POST | /api/analyze/text | `{"text": "..."}` |
| POST | /api/prescriptions/parse | prescription-only view |
| GET | /api/languages | en, hi, te, es |
| GET | /api/analyses/{id} · DELETE | only when STORE_RESULTS=true |
| GET | /api/health | status, tesseract availability |

Interactive docs: `/docs`.
