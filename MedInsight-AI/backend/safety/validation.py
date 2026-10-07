"""Deterministic rule checks. Mutates items with needs_review and returns alerts."""
from backend.knowledge.terminology import drug_lexicon
from backend.safety.confidence import meets_threshold


def check_dose(p: dict) -> dict | None:
    """Flag when the *minimum* implied daily dose already exceeds the typical adult max."""
    spec = drug_lexicon()[p["generic_key"]]
    max_mg, s_mg, fd = spec.get("max_daily_mg"), p.get("strength_mg"), p.get("frequency_detail")
    if not (max_mg and s_mg and fd) or fd.get("as_needed"):
        return None
    if fd.get("daily_units"):
        units = fd["daily_units"]
    elif fd.get("times_per_day"):
        units = fd["times_per_day"] * (p.get("units_per_dose") or 1)  # >=1 unit per dose
    else:
        return None
    daily = s_mg * units
    if daily > max_mg:
        return {"medicine": p["medicine_name"], "type": "dose_above_typical_max",
                "message": f"Prescribed amount is at least {daily:g} mg/day; typical adult maximum is {max_mg:g} mg/day. Verify with the prescriber."}
    return None


def validate(findings, conditions, prescriptions) -> dict:
    uncertain, dose_alerts = [], []
    for i, f in enumerate(findings):
        reasons = []
        if not meets_threshold(f["confidence"]):
            reasons.append("")
        if "implausible_value" in f["flags"]:
            reasons.append(".value")
        if "qualified_value" in f["flags"]:
            reasons.append(".value")
        if reasons:
            f["needs_review"] = True
            uncertain += [f"clinical_findings[{i}]{r}" for r in dict.fromkeys(reasons)]
    for i, c in enumerate(conditions):
        if c["hedged"] or not meets_threshold(c["confidence"]):
            c["needs_review"] = True
            uncertain.append(f"conditions[{i}]")
    for i, p in enumerate(prescriptions):
        for m in p["missing_fields"]:
            uncertain.append(f"prescriptions[{i}].{m}")
        if p["missing_fields"] or not meets_threshold(p["confidence"]):
            p["needs_review"] = True
            if not p["missing_fields"]:
                uncertain.append(f"prescriptions[{i}]")
        alert = check_dose(p)
        if alert:
            p["needs_review"] = True
            dose_alerts.append(alert)
            uncertain.append(f"prescriptions[{i}].dose")
    return {"uncertain_fields": uncertain, "dose_alerts": dose_alerts}
