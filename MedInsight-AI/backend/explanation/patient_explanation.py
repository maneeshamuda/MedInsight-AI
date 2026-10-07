"""Deterministic patient explanation built ONLY from extracted/validated facts.

No generative model is involved, so it cannot invent or alter a dose, a value or a diagnosis.
"""
from backend.translation.translator import render


def _freq(p: dict, lang: str) -> str | None:
    fd = p.get("frequency_detail")
    if not fd:
        return None
    kind, n = fd["kind"], fd.get("n")
    base = {"once": lambda: render("freq_once", lang), "twice": lambda: render("freq_twice", lang),
            "n": lambda: render("freq_n", lang, n=n), "slots": lambda: (render("freq_once", lang) if n == 1 else render("freq_twice", lang) if n == 2 else render("freq_n", lang, n=n)),
            "hours": lambda: render("freq_hours", lang, n=n), "bedtime": lambda: render("freq_bedtime", lang),
            "weekly": lambda: render("freq_weekly", lang), "prn": lambda: render("freq_prn", lang)}[kind]()
    if fd["as_needed"] and kind != "prn":
        base += render("prn_suffix", lang)
    return base


def _duration(p: dict, lang: str) -> str | None:
    d = p.get("duration_detail")
    if not d:
        return None
    unit = render(f"unit_{d['unit']}" + ("" if d["n"] == 1 else "s"), lang)
    return render("dur", lang, n=d["n"], unit=unit)


def _med_sentence(p: dict, lang: str) -> list[str]:
    name, purpose = p["medicine_name"], render(f"purpose_{p['purpose_code']}", lang)
    parts = [p.get("strength"), p.get("quantity") or p.get("form"), _freq(p, lang),
             render(f"timing_{p['timing_code']}", lang) if p.get("timing_code") else None, _duration(p, lang)]
    parts = [x for x in parts if x]
    out = [render("med_line", lang, name=name, purpose=purpose, details=", ".join(parts)) if parts
           else render("med_no_details", lang, name=name, purpose=purpose)]
    if p["missing_fields"]:
        fields = ", ".join(render(f"field_{f}", lang) for f in p["missing_fields"])
        out.append(render("med_missing", lang, fields=fields))
    elif p["needs_review"]:
        out.append(render("med_verify", lang))
    return out


def build_patient_text(findings, conditions, prescriptions, interactions, requires_review: bool, lang: str) -> str:
    lines = []
    sure = [c["name"] for c in conditions if not c["needs_review"]]
    unsure = [c["name"] for c in conditions if c["needs_review"]]
    if sure:
        lines.append(render("conditions", lang, list=", ".join(sure)))
    if unsure:
        lines.append(render("condition_unconfirmed", lang, list=", ".join(unsure)))
    for f in findings:
        if f["needs_review"]:
            lines.append(render("lab_uncertain", lang, name=f["name"]))
            continue
        unit_part = f" {f['unit']}" if f.get("unit") else ""
        rng = ""
        if f.get("reference_range"):
            rng = render("range_generic" if f["reference_source"] == "generic_adult" else "range_part", lang, range=f["reference_range"])
        key = f"lab_line_{f['status']}"
        lines.append(render(key, lang, name=f["name"], value=f["value"], unit_part=unit_part, range_part=rng))
    for p in prescriptions:
        lines += _med_sentence(p, lang)
    for a in interactions:
        lines.append(render("interaction", lang, a=a["drugs"][0], b=a["drugs"][1], severity=render(f"sev_{a['severity']}", lang)))
    if requires_review:
        lines.append(render("needs_review", lang))
    lines.append(render("disclaimer", lang))
    return "\n".join(lines)
