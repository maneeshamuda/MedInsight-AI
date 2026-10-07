"""Loads editable terminology tables from data/terminology/*.json."""
import json
from functools import lru_cache

from backend.config import TERMINOLOGY_DIR


@lru_cache(maxsize=None)
def _load(name: str):
    with open(TERMINOLOGY_DIR / f"{name}.json", encoding="utf-8") as f:
        return json.load(f)


def lab_lexicon() -> dict:
    return _load("labs")


def drug_lexicon() -> dict:
    return _load("drugs")


def condition_lexicon() -> dict:
    return _load("conditions")


def interaction_table() -> list:
    return _load("interactions")


def norm_unit(unit: str | None) -> str:
    """Canonical lowercase unit so 'gm/dL', 'g/dl', '/cumm', 'µIU/mL' compare equal."""
    if not unit:
        return ""
    u = unit.lower().replace("\u00b5", "u").replace("\u03bc", "u").replace(" ", "")
    if u.startswith("gm/"):
        u = "g/" + u[3:]
    return u.replace("cumm", "ul").replace("mm3", "ul").replace("cells", "")
