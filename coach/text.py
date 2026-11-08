"""Text matching shared by food search and exercise lookup."""

import re
import unicodedata


def fold(text: str) -> str:
    """Lower case without accents, so "jalon" matches "jalón" and "brocoli" matches "brócoli"."""
    decomposed = unicodedata.normalize("NFKD", text.strip().lower())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def fold_words(*texts: str) -> list[str]:
    """The folded words of the texts, punctuation dropped: a quoted phrase ("pechuga de pollo,
    cruda") is its words, as names are split for search."""
    return re.findall(r"\w+", fold(" ".join(texts)))


def number(value: float, language: str | None, decimals: int = 2) -> str:
    """A number for a sentence the client reads: rounded, trailing zeros dropped, and a decimal
    comma in Spanish (header lines and JSON fields keep the point)."""
    text = f"{round(value, decimals):.{decimals}f}".rstrip("0").rstrip(".")
    return text.replace(".", ",") if language == "es" else text
