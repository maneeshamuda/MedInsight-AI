"""Curated food / exercise / habit guidance from conditions, medicines and out-of-range labs.

Deterministic lookup only (no generative model). General wellness information, not a diet plan.
"""
import json
from functools import lru_cache

from backend import config
from backend.knowledge.terminology import condition_lexicon, drug_lexicon, lab_lexicon

NOTE = ("General wellness information only. It is not a diet or exercise prescription. "
        "Confirm with your doctor or a dietitian, especially with kidney, heart or liver disease, pregnancy, or other conditions.")


@lru_cache(maxsize=1)
def _guide() -> dict:
    with open(config.DATA_DIR / "wellness" / "guidance.json", encoding="utf-8") as f:
        return json.load(f)


def _rev(lex: dict) -> dict:
    return {v["display"].lower(): k for k, v in lex.items()}


def _add(bucket: dict, kind: str, items: list[str], why: str):
    for t in items:
        bucket[kind].setdefault(t, [])
        if why not in bucket[kind][t]:
            bucket[kind][t].append(why)


def build_wellness(findings: list[dict], conditions: list[dict], prescriptions: list[dict]) -> dict:
    g = _guide()
    cmap, dmap, lmap = _rev(condition_lexicon()), _rev(drug_lexicon()), _rev(lab_lexicon())
    acc = {"eat": {}, "limit": {}, "exercise": {}, "habits": {}}
    medicine_tips, matched = [], []

    for c in conditions:
        if c.get("hedged"):
            continue
        key = cmap.get(c["name"].lower())
        if key in g["conditions"]:
            matched.append(c["name"])
            for kind, items in g["conditions"][key].items():
                _add(acc, kind, items, c["name"])
    for f in findings:
        key = lmap.get(f["name"].lower())
        spec = g["labs"].get(f"{key}:{f['status']}")
        if spec and not f.get("needs_review"):
            for kind, items in spec.items():
                _add(acc, kind, items, f"{f['name']} {f['status'].replace('_', ' ')}")
    for p in prescriptions:
        key = dmap.get((p.get("generic_name") or p["medicine_name"]).lower())
        if key in g["drugs"]:
            medicine_tips.append({"medicine": p["medicine_name"], "tips": g["drugs"][key]})

    if not any(acc.values()) and not medicine_tips:
        return {"available": False, "note": NOTE}
    if not acc["eat"] and not acc["exercise"]:
        for kind, items in g["general"].items():
            _add(acc, kind, items, "General health")
    sections = {k: [{"text": t, "because": w} for t, w in v.items()] for k, v in acc.items()}
    return {"available": True, "based_on": matched, **sections, "medicine_tips": medicine_tips, "note": NOTE}
