"""Explicitly-stated conditions only (no diagnosis inference from lab values)."""
import re
from functools import lru_cache

from backend.knowledge.terminology import condition_lexicon

NEGATION = re.compile(
    r"\b(no|not|denies|denied|without|negative for|ruled out|rule out excluded|absence of|free of|no evidence of|no history of|nil)\b", re.I)
NOT_PATIENT = re.compile(r"\b(family history|father|mother|sibling|brother|sister)\b", re.I)
HEDGE = re.compile(r"\b(suggest(?:s|ive|ing)?|possible|probable|likely|suspected?|\?|r/o|rule out|query|\?\?|may be|consistent with)\b", re.I)


@lru_cache(maxsize=1)
def _index():
    pairs = []
    for key, spec in condition_lexicon().items():
        pairs += [(a.lower(), key) for a in spec["aliases"]]
    pairs.sort(key=lambda p: -len(p[0]))
    alt = "|".join(re.escape(a).replace(r"\ ", r"\s+") for a, _ in pairs)
    return re.compile(rf"(?<![A-Za-z0-9])(?P<a>{alt})(?![A-Za-z0-9])", re.I), dict(pairs)


def extract_conditions(text: str) -> list[dict]:
    rx, alias_to_key = _index()
    lex = condition_lexicon()
    found: dict[str, dict] = {}
    for line in text.splitlines():
        for sentence in re.split(r"(?<=[.;])\s+", line):
            consumed_to = -1
            for m in rx.finditer(sentence):
                if m.start() < consumed_to:
                    continue
                consumed_to = m.end()
                key = alias_to_key[re.sub(r"\s+", " ", m.group("a").lower())]
                before = sentence[max(0, m.start() - 45): m.start()]
                if NEGATION.search(before) or NOT_PATIENT.search(before):
                    continue
                hedged = bool(HEDGE.search(sentence))
                conf = 0.6 if hedged else 0.9
                prev = found.get(key)
                if prev and prev["confidence"] >= conf:
                    continue
                found[key] = {
                    "key": key, "name": lex[key]["display"], "confidence": conf,
                    "hedged": hedged, "needs_review": False, "source_text": sentence[:160],
                }
    # "diabetes" generic is redundant when a specific type was matched
    if "type2_diabetes" in found:
        found.pop("diabetes_unspecified", None)
    return list(found.values())
