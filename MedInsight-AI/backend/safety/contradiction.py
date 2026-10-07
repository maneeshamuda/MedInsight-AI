"""Internal-consistency checks across extracted facts."""
from collections import defaultdict


def find_contradictions(findings: list[dict], prescriptions: list[dict]) -> list[dict]:
    out = []
    by_lab = defaultdict(list)
    for i, f in enumerate(findings):
        by_lab[f["key"]].append(i)
        flag, st = f.get("report_flag"), f["status"]
        if flag and st in ("within_range", "above_range", "below_range") and flag != st:
            f["needs_review"] = True
            out.append({"type": "report_flag_mismatch", "fields": [f"clinical_findings[{i}]"],
                        "message": f"{f['name']}: the report marks it {flag.replace('_', ' ')} but the value compares as {st.replace('_', ' ')} against the reference range."})
    for key, idxs in by_lab.items():
        vals = {(findings[i]["value"], findings[i]["unit"]) for i in idxs}
        if len(vals) > 1:
            for i in idxs:
                findings[i]["needs_review"] = True
            out.append({"type": "multiple_values", "fields": [f"clinical_findings[{i}]" for i in idxs],
                        "message": f"{findings[idxs[0]]['name']} appears with different values in the document."})
    by_drug = defaultdict(list)
    for i, p in enumerate(prescriptions):
        by_drug[p["generic_key"]].append(i)
    for key, idxs in by_drug.items():
        if len(idxs) > 1:
            for i in idxs:
                prescriptions[i]["needs_review"] = True
            out.append({"type": "duplicate_or_conflicting_medicine", "fields": [f"prescriptions[{i}]" for i in idxs],
                        "message": f"{prescriptions[idxs[0]]['generic_name']} is listed more than once with different details."})
    return out
