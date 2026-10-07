"""Rule-based lab-value extraction with reference ranges, status and confidence."""
import re
from functools import lru_cache

from backend.knowledge.terminology import lab_lexicon, norm_unit

_UNIT = (
    r"(?:g|gm)/dl|mg/dl|mmol/l|[mu\u00b5\u03bc]iu/m?l|iu/l|u/l|ng/ml|ng/dl|pg/ml|meq/l|mg/l|mm/hr|%|fl|pg"
    r"|(?:cells|million|mill|lakhs?|thou(?:sand)?)?/(?:[u\u00b5\u03bc]l|cumm|mm3|l)|x?10\^\d/l"
)
UNIT_RE = re.compile(rf"\s*({_UNIT})(?![A-Za-z])", re.I)
NUM_RE = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{2,3})+(?:\.\d+)?|\d+(?:\.\d+)?)")
RANGE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)", re.I)
LT_RE = re.compile(r"(?:<=?|\u2264|up\s*to|upto|less than)\s*(\d+(?:\.\d+)?)", re.I)
GT_RE = re.compile(r"(?:>=?|\u2265|more than|greater than)\s*(\d+(?:\.\d+)?)", re.I)
FLAG_RE = re.compile(r"(?<![A-Za-z])(H|L|HIGH|LOW|High|Low|high|low)(?![A-Za-z])")
GAP_RE = re.compile(r"^[\s:\-|.=,_]*(?:\([^)]{0,20}\)\s*[:\-]?\s*)?([<>\u2264\u2265]=?)?\s*$")


@lru_cache(maxsize=1)
def _alias_index():
    pairs = []
    for key, spec in lab_lexicon().items():
        pairs += [(a.lower(), key) for a in spec["aliases"]]
    pairs.sort(key=lambda p: -len(p[0]))
    alt = "|".join(re.escape(a).replace(r"\ ", r"\s+") for a, _ in pairs)
    rx = re.compile(rf"(?<![A-Za-z0-9])(?P<a>{alt})(?![A-Za-z0-9])", re.I)
    return rx, dict(pairs)


def _fmt(x: float) -> str:
    return f"{x:g}"


def _parse_range(s: str):
    m = RANGE_RE.search(s)
    if m:
        lo, hi = float(m.group(1)), float(m.group(2))
        if lo < hi:
            return lo, hi, f"{_fmt(lo)}-{_fmt(hi)}"
    m = LT_RE.search(s)
    if m:
        hi = float(m.group(1))
        return None, hi, f"<{_fmt(hi)}"
    m = GT_RE.search(s)
    if m:
        lo = float(m.group(1))
        return lo, None, f">{_fmt(lo)}"
    return None


def _status(v, lo, hi):
    if lo is None and hi is None:
        return "unknown"
    if lo is not None and v < lo:
        return "below_range"
    if hi is not None and v > hi:
        return "above_range"
    return "within_range"


def extract_labs(text: str) -> list[dict]:
    rx, alias_to_key = _alias_index()
    lex = lab_lexicon()
    out, seen = [], set()
    for line in text.splitlines():
        m = rx.search(line)
        if not m:
            continue
        key = alias_to_key[re.sub(r"\s+", " ", m.group("a").lower())]
        spec = lex[key]
        rest = line[m.end():]
        nm = NUM_RE.search(rest)
        if not nm:
            continue
        gap = GAP_RE.match(rest[: nm.start()])
        if not gap:
            continue  # words between name and number: do not guess
        qualifier = gap.group(1)
        value_text = nm.group(1).replace(",", "")
        value = float(value_text)
        after = rest[nm.end():]
        um = UNIT_RE.match(after)
        unit = um.group(1) if um else None
        after = after[um.end():] if um else after

        rng = _parse_range(after)
        flag_m = FLAG_RE.search(RANGE_RE.sub(" ", after))
        report_flag = None
        if flag_m:
            report_flag = "above_range" if flag_m.group(1).lower() in ("h", "high") else "below_range"

        nu = norm_unit(unit)
        unit_ok = bool(nu) and nu in spec["units"]
        flags: list[str] = []
        lo = hi = None
        ref_text, ref_src = None, None
        if rng:
            lo, hi, ref_text = rng
            ref_src = "report"
        elif spec["default"] and unit_ok:
            lo, hi = spec["default"]
            ref_text, ref_src = f"{_fmt(lo)}-{_fmt(hi)}", "generic_adult"
            flags.append("generic_reference_range")

        if qualifier:
            status = "unknown"
            flags.append("qualified_value")
        else:
            status = _status(value, lo, hi)

        conf = 0.55
        conf += 0.15 if unit else 0.0
        if ref_src == "report":
            conf += 0.25
        elif ref_src == "generic_adult":
            conf += 0.15
        if unit_ok:
            plo, phi = spec["plausible"]
            if plo <= value <= phi:
                conf += 0.05
            else:
                conf *= 0.5
                flags.append("implausible_value")
        if qualifier:
            conf = min(conf, 0.7)
        conf = round(min(conf, 0.99), 2)

        sig = (key, value_text, nu)
        if sig in seen:
            continue
        seen.add(sig)
        out.append({
            "key": key, "name": spec["display"], "value": ("%s%s" % (qualifier or "", value_text)),
            "numeric_value": value, "unit": unit, "reference_range": ref_text,
            "reference_source": ref_src, "status": status, "report_flag": report_flag,
            "loinc": spec.get("loinc"), "confidence": conf, "flags": flags,
            "needs_review": False, "source_text": line[:160],
        })
    return out
