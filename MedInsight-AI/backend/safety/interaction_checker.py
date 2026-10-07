"""Curated pair table (demo-grade). Production: integrate RxNav/DrugBank/licensed DDI data."""
from backend.knowledge.terminology import interaction_table


def check_interactions(prescriptions: list[dict]) -> list[dict]:
    present = {p["generic_key"]: p["generic_name"] for p in prescriptions}
    alerts = []
    for row in interaction_table():
        a, b = row["drugs"]
        if a in present and b in present:
            alerts.append({"drugs": [present[a], present[b]], "severity": row["severity"], "message": row["message"]})
    order = {"major": 0, "moderate": 1, "minor": 2}
    return sorted(alerts, key=lambda x: order.get(x["severity"], 3))
