"""Text matching shared by food search and exercise lookup."""

import unicodedata


def fold(text: str) -> str:
    """Lower case without accents, so "jalon" matches "jalón" and "brocoli" matches "brócoli"."""
    decomposed = unicodedata.normalize("NFKD", text.strip().lower())
    return "".join(c for c in decomposed if not unicodedata.combining(c))
