"""The profile's `region` value: a regions/<code>/ folder name, or "none" for no region."""

NO_REGION = "none"  # a country with no regions/<code>/ folder: the base food table only


def real_region(code: str | None) -> str | None:
    """The folder code in lower case, or None for no region (None, "" or "none" in any case)."""
    code = (code or "").strip().lower()
    return None if code in ("", NO_REGION) else code
