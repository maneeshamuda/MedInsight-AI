from fastapi.testclient import TestClient
from backend.main import app

c = TestClient(app)
SAMPLE = open("data/sample_reports/sample_mixed_report.txt").read()


def test_health():
    assert c.get("/api/health").json()["status"] == "ok"


def test_languages():
    assert set(c.get("/api/languages").json()) == {"en", "hi", "te", "es"}


def test_analyze_text_schema():
    r = c.post("/api/analyze/text", json={"text": SAMPLE})
    assert r.status_code == 200
    j = r.json()
    assert j["document"]["type"] == "mixed" and j["safety"]["requires_human_review"]
    assert j["translations"]["hi"]["labels"]["title"]


def test_analyze_upload_txt():
    r = c.post("/api/analyze", files={"file": ("r.txt", SAMPLE.encode(), "text/plain")})
    assert r.status_code == 200 and len(r.json()["prescriptions"]) == 5


def test_rejects_empty_and_binary():
    assert c.post("/api/analyze/text", json={"text": "  "}).status_code == 400
    assert c.post("/api/analyze", files={"file": ("x.bin", b"\xff\xfe\x00\x81\x82", "application/octet-stream")}).status_code == 415


def test_prescription_endpoint():
    r = c.post("/api/prescriptions/parse", json={"text": "Tab Metformin 500 mg BD x 30 days"})
    assert r.status_code == 200 and r.json()["prescriptions"][0]["rxnorm_id"] == "6809"


def test_frontend_served():
    assert "MedInsight" in c.get("/").text


def test_wellness_guidance():
    from backend import pipeline
    w = pipeline.analyze_text("Diagnosis: hypertension\nTab Amlodipine 5 mg OD")["wellness"]
    assert w["available"] and w["eat"] and w["medicine_tips"][0]["medicine"] == "Amlodipine"
