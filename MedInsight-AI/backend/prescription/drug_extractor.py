"""Prescription parsing: drug identity + strength/form/quantity/frequency/timing/duration."""
import re
from functools import lru_cache

from backend.knowledge.terminology import drug_lexicon
from backend.prescription import dosage_parser as dp
from backend.prescription.frequency_parser import parse_frequency
from backend.prescription.prescription_schema import WEIGHTS

NON_RX_CONTEXT = re.compile(r"allerg|intoleran|hypersensitiv|\bavoid\b|contraindicat|discontinu|stopped|do not (?:take|give)", re.I)


@lru_cache(maxsize=1)
def _index():
    pairs = []
    for key, spec in drug_lexicon().items():
        pairs += [(a.lower(), key) for a in spec["aliases"]]
    pairs.sort(key=lambda p: -len(p[0]))
    alt = "|".join(re.escape(a) for a, _ in pairs)
    return re.compile(rf"(?<![A-Za-z0-9])(?P<a>{alt})(?![A-Za-z0-9])", re.I), dict(pairs)


def _segments(lines: list[str]):
    """Yield (drug_key, written_name, prefix, segment_text) for every drug mention."""
    rx, a2k = _index()
    hits = []
    for i, ln in enumerate(lines):
        hits += [(i, m) for m in rx.finditer(ln)]
    line_hit_idx = {i for i, _ in hits}
    for n, (i, m) in enumerate(hits):
        nxt_same = next((m2.start() for i2, m2 in hits[n + 1:] if i2 == i), None)
        seg = lines[i][m.start(): nxt_same]
        if nxt_same is None:  # continuation lines (max 2) until blank / next drug line
            for j in range(i + 1, min(i + 3, len(lines))):
                if not lines[j].strip() or j in line_hit_idx:
                    break
                seg += " " + lines[j]
        prefix = lines[i][max(0, m.start() - 12): m.start()]
        yield a2k[m.group("a").lower()], m.group("a"), prefix, seg, lines[i]


def extract_prescriptions(text: str) -> tuple[list[dict], list[str]]:
    lex = drug_lexicon()
    items, notes, seen = [], [], set()
    for key, written, prefix, seg, full_line in _segments(text.splitlines()):
        spec = lex[key]
        if NON_RX_CONTEXT.search(full_line):
            notes.append(f"'{written}' appears in an allergy/avoid/stop context and was not treated as a prescription.")
            continue
        # strength first, then blank it out so '5 ml' of '250 mg/5 ml' is not read as quantity
        body = seg[len(written):]
        st = dp.parse_strength(body)
        body_wo = body
        if st:
            a, b = st[2]
            body_wo = body[:a] + " " * (b - a) + body[b:]
        freq = parse_frequency(body_wo)
        qty = dp.parse_quantity(body_wo)
        form = dp.parse_form(prefix + " " + body_wo)
        timing = dp.parse_timing(body_wo)
        dur = dp.parse_duration(body_wo)

        missing = [f for f, v in (("strength", st), ("frequency", freq)) if not v]
        warnings = []
        if not dur:
            warnings.append("duration not specified")
        if not (form or qty):
            warnings.append("form/quantity not specified")
        if not timing:
            warnings.append("timing relative to meals not specified")

        conf = WEIGHTS["drug"]
        conf += WEIGHTS["strength"] if st else 0
        conf += WEIGHTS["frequency"] if freq else 0
        conf += WEIGHTS["duration"] if dur else 0
        conf += WEIGHTS["form_or_quantity"] if (form or qty) else 0
        conf += WEIGHTS["timing"] if timing else 0

        name = written if written.lower() == spec["display"].lower() else f"{written.title()} ({spec['display']})"
        item = {
            "medicine_name": name, "generic_key": key, "generic_name": spec["display"],
            "purpose_code": spec["purpose"], "strength": st[0] if st else None,
            "strength_mg": st[1] if st else None, "form": form,
            "quantity": qty[0] if qty else None, "units_per_dose": qty[1] if qty else None,
            "frequency": freq["normalized"] if freq else None, "frequency_detail": freq,
            "timing": timing[1] if timing else None, "timing_code": timing[0] if timing else None,
            "duration": dur[0] if dur else None,
            "duration_detail": {"n": dur[1], "unit": dur[2]} if dur else None,
            "confidence": round(min(conf, 0.99), 2), "missing_fields": missing,
            "warnings": warnings, "needs_review": False, "source_text": full_line[:160],
        }
        sig = (key, item["strength"], item["frequency"], item["duration"])
        if sig in seen:
            continue
        seen.add(sig)
        items.append(item)
    return items, notes
