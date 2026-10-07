"""Parse dosing frequency: OD/BD/TDS/QID, 1-0-1, q8h, SOS/PRN, bedtime, weekly."""
import re

SLOT_RE = re.compile(r"(?<![\d\-/.])([0-3])-([0-3])-([0-3])(?:-([0-3]))?(?![\d\-/])")
HOURS_RE = re.compile(r"\bq\s*(\d{1,2})\s*h\b|\bevery\s*(\d{1,2})\s*(?:hours?|hrs?|h)\b|\b(\d{1,2})\s*hourly\b", re.I)
PRN_RE = re.compile(r"\b(?:s\.?o\.?s\.?|p\.?r\.?n\.?|as needed|when required|if required|if needed|when needed)(?![A-Za-z])", re.I)
WEEKLY_RE = re.compile(r"\b(?:once\s*(?:a\s*|per\s*)?week(?:ly)?|weekly|1\s*/\s*week)\b", re.I)
BEDTIME_RE = re.compile(r"\b(?:h\.?s\.?|at\s*bed\s*time|bed\s*time|at night)(?![A-Za-z])", re.I)
NUMERIC_RE = re.compile(r"\b(\d)\s*(?:times|x)\s*(?:a\s*|per\s*|/\s*)?(?:day|daily|d)\b", re.I)
WORD_PATTERNS = [
    (re.compile(r"\b(?:q\.?i\.?d\.?|four\s*times(?:\s*(?:a|per))?(?:\s*(?:day|daily))?)(?![A-Za-z])", re.I), 4),
    (re.compile(r"\b(?:t\.?d\.?s\.?|t\.?i\.?d\.?|thrice(?:\s*(?:a|per))?(?:\s*(?:day|daily))?|three\s*times(?:\s*(?:a|per))?(?:\s*(?:day|daily))?)(?![A-Za-z])", re.I), 3),
    (re.compile(r"\b(?:b\.?d\.?|b\.?i\.?d\.?|twice(?:\s*(?:a|per))?(?:\s*(?:day|daily))?|two\s*times(?:\s*(?:a|per))?(?:\s*(?:day|daily))?)(?![A-Za-z])", re.I), 2),
    (re.compile(r"\b(?:o\.?d\.?|q\.?d\.?|once(?:\s*(?:a|per))?\s*(?:day|daily)|once\s*daily|1\s*(?:time|x)\s*(?:a\s*|per\s*|/\s*)?(?:day|daily))(?![A-Za-z])", re.I), 1),
]


def _times_label(n: int) -> str:
    return {1: "once daily", 2: "twice daily"}.get(n, f"{n} times daily")


def parse_frequency(text: str) -> dict | None:
    info = {"kind": None, "n": None, "times_per_day": None, "daily_units": None,
            "units_per_dose": None, "as_needed": False, "normalized": None}
    m = SLOT_RE.search(text)
    if m:
        slots = [int(g) for g in m.groups() if g is not None]
        nz = [s for s in slots if s]
        if nz:
            info.update(kind="slots", n=len(nz), times_per_day=len(nz), daily_units=float(sum(nz)),
                        units_per_dose=float(nz[0]) if len(set(nz)) == 1 else None,
                        normalized=_times_label(len(nz)))
    if not info["kind"]:
        h = HOURS_RE.search(text)
        if h:
            n = int(next(g for g in h.groups() if g))
            if n > 0:
                info.update(kind="hours", n=n, times_per_day=(24 // n if 24 % n == 0 else None),
                            normalized=f"every {n} hours")
    if not info["kind"]:
        for rx, n in WORD_PATTERNS:
            if rx.search(text):
                info.update(kind="n" if n > 2 else ("twice" if n == 2 else "once"), n=n,
                            times_per_day=n, normalized=_times_label(n))
                break
    if not info["kind"]:
        nm = NUMERIC_RE.search(text)
        if nm and int(nm.group(1)) > 0:
            n = int(nm.group(1))
            info.update(kind="n" if n > 2 else ("twice" if n == 2 else "once"), n=n,
                        times_per_day=n, normalized=_times_label(n))
    if not info["kind"] and WEEKLY_RE.search(text):
        info.update(kind="weekly", n=1, normalized="once weekly")
    if not info["kind"] and BEDTIME_RE.search(text):
        info.update(kind="bedtime", n=1, times_per_day=1, normalized="once daily at bedtime")
    if PRN_RE.search(text):
        info["as_needed"] = True
        info["normalized"] = f"{info['normalized']} as needed" if info["normalized"] else "as needed"
        info["kind"] = info["kind"] or "prn"
    return info if info["kind"] else None
