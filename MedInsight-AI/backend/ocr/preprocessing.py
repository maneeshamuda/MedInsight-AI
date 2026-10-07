"""Text and image cleanup before extraction."""
import re
import unicodedata

_DASHES = dict.fromkeys(map(ord, "\u2013\u2014\u2212\u2012"), "-")


def clean_text(text: str) -> str:
    """Normalise whitespace/dashes line by line. Never alters digits or words."""
    text = unicodedata.normalize("NFC", text).translate(_DASHES)
    text = text.replace("\u00a0", " ").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.split("\n")]
    return "\n".join(lines).strip()


def preprocess_image(img):
    """Grayscale, upscale small scans, autocontrast. Returns a PIL image."""
    from PIL import Image, ImageOps

    img = ImageOps.exif_transpose(img).convert("L")
    short = min(img.size)
    if short < 1000:
        scale = 1000 / short
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    return ImageOps.autocontrast(img)
