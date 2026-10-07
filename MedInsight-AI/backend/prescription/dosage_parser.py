"""Strength, form, quantity, timing, duration parsers."""
import re

STRENGTH_RE = re.compile(
    r"(?<![\d.])(\d+(?:\.\d+)?)\s*(mg|mcg|\u00b5g|\u03bcg|ug|gm|g|iu|units?|%)"
    r"(?:\s*/\s*(\d+(?:\.\d+)?)?\s*(ml|g|tab|cap))?(?![A-Za-z])", re.I)
FORM_RE = re.compile(r"\b(tab(?:let)?s?|cap(?:sule)?s?|syr(?:up)?|syp|susp(?:ension)?|inj(?:ection)?|drops?|cream|ointment|gel|inhaler|spray)\b", re.I)
QTY_RE = re.compile(
    r"(?<![\d.])(\d+(?:\.\d+)?|one|two|three|half|1/2)\s*(tab(?:let)?s?|cap(?:sule)?s?|ml|tsp|teaspoon(?:ful)?s?|drops?|puffs?|sachets?)\b", re.I)
DURATION_RE = re.compile(r"(?:(?:for|x|\u00d7|\*)\s*)?(?<![\d.])(\d{1,3})\s*(days?|d|weeks?|wks?|wk|months?|mos?)\b", re.I)
TIMING_PATTERNS = [
    ("after_meals", "after meals", re.compile(r"\b(?:after\s*(?:food|meals?|eating|dinner|lunch|breakfast)|p\.?c\.?|post[- ]?meals?)(?![A-Za-z])", re.I)),
    ("before_meals", "before meals", re.compile(r"\b(?:before\s*(?:food|meals?|eating|dinner|lunch|breakfast)|a\.?c\.?|pre[- ]?meals?)(?![A-Za-z])", re.I)),
    ("with_food", "with food", re.compile(r"\bwith\s*(?:food|meals?)\b", re.I)),
    ("empty_stomach", "on an empty stomach", re.compile(r"\bempty\s*stomach\b", re.I)),
    ("bedtime", "at bedtime", re.compile(r"\b(?:at\s*bed\s*time|bed\s*time|h\.?s\.?)(?![A-Za-z])", re.I)),
]
_FORM_NORM = {"tab": "tablet", "cap": "capsule", "syr": "syrup", "syp": "syrup", "susp": "suspension",
              "inj": "injection", "drop": "drops"}
_NUMWORD = {"one": 1.0, "two": 2.0, "three": 3.0, "half": 0.5, "1/2": 0.5}


def parse_strength(text: str):
    """Return (display, strength_mg_or_None, span) or None."""
    m = STRENGTH_RE.search(text)
    if not m:
        return None
    num, unit = float(m.group(1)), m.group(2).lower()
    unit = {"\u00b5g": "mcg", "\u03bcg": "mcg", "ug": "mcg", "gm": "g", "unit": "units"}.get(unit, unit)
    display = f"{num:g} {unit}"
    per = m.group(4)
    if per:
        display += f"/{(m.group(3) + ' ') if m.group(3) else ''}{per.lower()}"
    mg = None
    if not per:
        mg = {"mg": num, "mcg": num / 1000, "g": num * 1000}.get(unit)
    return display, mg, m.span()


def parse_form(text: str) -> str | None:
    m = FORM_RE.search(text)
    if not m:
        return None
    w = m.group(1).lower()
    for k, v in _FORM_NORM.items():
        if w.startswith(k):
            return v
    return w


def parse_quantity(text: str):
    """Return (display, units_per_dose_or_None)."""
    m = QTY_RE.search(text)
    if not m:
        return None
    raw, unit = m.group(1).lower(), m.group(2).lower()
    n = _NUMWORD.get(raw) or float(raw)
    norm_unit = ("tablet" if unit.startswith("tab") else "capsule" if unit.startswith("cap") else
                 "tsp" if unit.startswith(("tsp", "teaspoon")) else unit.rstrip("s") if unit != "ml" else "ml")
    disp_unit = norm_unit + ("s" if n > 1 and norm_unit in ("tablet", "capsule") else "")
    units = n if norm_unit in ("tablet", "capsule") else None
    return f"{n:g} {disp_unit}", units


def parse_timing(text: str):
    for code, label, rx in TIMING_PATTERNS:
        if rx.search(text):
            return code, label
    return None


def parse_duration(text: str):
    best = None
    for m in DURATION_RE.finditer(text):
        has_prefix = bool(re.match(r"(?:for|x|\u00d7|\*)", m.group(0), re.I))
        if best is None or (has_prefix and not best[0]):
            best = (has_prefix, m)
    if not best:
        return None
    m = best[1]
    n, u = int(m.group(1)), m.group(2).lower()
    unit = "day" if u.startswith("d") else "week" if u.startswith(("w",)) else "month"
    if n == 0:
        return None
    return f"{n} {unit}{'' if n == 1 else 's'}", n, unit
