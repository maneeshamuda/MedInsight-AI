# Safety design

1. **Never Guess** – a field that is not present in the document stays `null`. Required fields
   (medicine strength, frequency) missing => `needs_review`. Nothing is inferred or defaulted.
2. **Deterministic explanation** – patient text is rendered from extracted facts via reviewed
   templates (`backend/translation/languages.py`). No generative model can alter a value or dose.
3. **Confidence** – each item scored from evidence present (unit, report range, plausibility, strength,
   frequency…) and scaled by OCR quality. Below `CONFIDENCE_THRESHOLD` (0.90) => human review.
4. **Rules** – plausibility bounds, max-daily-dose check (uses *minimum* implied dose), report-flag vs
   computed-status contradictions, duplicate/conflicting medicines, allergy-context exclusion.
5. **Interactions** – curated pair table (`data/terminology/interactions.json`). Demo-grade; replace with
   a licensed DDI source before real use.
6. **No diagnosis** – conditions are extracted only when explicitly written (negation, family history and
   hedging handled). Lab values are never turned into diagnoses.
7. **Privacy** – results not stored by default; source files never stored; `DELETE /api/analyses/{id}`.

## Known limits
- Reference ranges fall back to a *generic adult union range* only when the report has none and the unit matches. Flagged `generic_reference_range`.
- Terminology tables are small seed sets. SNOMED CT needs a licence for production.
- Not a medical device. Not validated clinically.
