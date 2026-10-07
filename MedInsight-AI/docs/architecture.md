# Architecture

ingest (ocr/) -> clinical NLP (nlp/) + prescription parser (prescription/) -> knowledge codes (knowledge/)
-> safety (safety/: confidence, validation, contradictions, interactions, human_review)
-> explanation (explanation/) -> templates per language (translation/) -> dashboard (public/)

`backend/pipeline.py` is the single orchestrator. Every stage is a pure function over dicts, so each can be
unit-tested and swapped (e.g. replace `lab_extractor` with a Transformer NER) without touching the rest.
