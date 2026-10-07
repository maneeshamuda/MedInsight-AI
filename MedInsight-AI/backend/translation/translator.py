from backend.translation.languages import SUPPORTED, T


def render(key: str, lang: str, **kw) -> str:
    tpl = T.get(lang, T["en"]).get(key) or T["en"][key]
    return tpl.format(**kw) if kw else tpl


def labels(lang: str) -> dict:
    return T.get(lang, T["en"])["labels"]


def available() -> dict:
    return SUPPORTED
