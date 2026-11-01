"""The profile's `region` value: a regions/<code>/ folder name, or "none" for no region."""

import re

NO_REGION = "none"  # a country with no regions/<code>/ folder: the base food table only
_CODE = re.compile(r"^[a-z0-9_-]+$")  # a folder name, never a path


def real_region(code: str | None) -> str | None:
    """The folder code in lower case, or None for no region (None, "" or "none" in any case).
    Raises ValueError for anything that is not a plain folder name (it would reach the disk)."""
    code = (code or "").strip().lower()
    if code in ("", NO_REGION):
        return None
    if not _CODE.match(code):
        raise ValueError(f"{code!r} is not a region code (letters, digits, - and _ only)")
    return code
