from backend.translation.translator import render


def build_summary(findings, prescriptions, lang: str) -> str:
    abnormal = sum(1 for f in findings if f["status"] in ("above_range", "below_range") and not f["needs_review"])
    return render("summary", lang, labs=len(findings), meds=len(prescriptions), abnormal=abnormal)
