"""`coach doctor`: first-run checks, so a new user sees what is missing and the command that fixes
it (README "First 10 minutes"). Tooling only: no coaching numbers here."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

# The Python the project declares in pyproject.toml (`requires-python`).
PYTHON_MIN = (3, 12)


def _check(name: str, ok: bool, detail: str, fix: str = "") -> dict:
    return {"check": name, "ok": ok, "detail": detail, "fix": "" if ok else fix}


def _pdf_extra() -> bool:
    try:
        import reportlab  # noqa: F401
    except ImportError:
        return False
    return True


def _data_dir(data_dir: Path) -> tuple[bool, str]:
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        probe = data_dir / ".doctor-write-test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except OSError as err:
        return False, str(err)
    return True, str(data_dir.resolve())


def _profile(data_dir: Path) -> tuple[bool, str]:
    from coach.cli import PROFILE_REQUIRED, _missing  # the same list `coach profile show` uses
    from coach.profile import load_profile

    path = data_dir / "profile.yaml"
    if not path.exists():
        return False, "no profile yet"
    try:
        profile = load_profile(path)
    except ValueError as err:
        return False, str(err)
    missing = [f for f in PROFILE_REQUIRED if _missing(profile, f)]
    return not missing, "missing: " + ", ".join(missing) if missing else "complete"


def run(data_dir: Path) -> dict:
    data_dir = Path(data_dir)
    python = sys.version_info[:2]
    data_ok, data_detail = _data_dir(data_dir)
    profile_ok, profile_detail = _profile(data_dir) if data_ok else (False, "no data folder")
    checks = [
        _check(
            "python",
            python >= PYTHON_MIN,
            f"{python[0]}.{python[1]}",
            "install Python 3.12 or newer, or let uv fetch it: uv python install 3.12",
        ),
        _check(
            "pdf_extra",
            _pdf_extra(),
            "reportlab (printable plan and menus)",
            "uv sync --extra pdf",
        ),
        _check(
            "data_dir",
            data_ok,
            data_detail,
            "make the folder writable, or set COACH_DATA_DIR to one that is (README, Settings)",
        ),
        _check(
            "uv",
            shutil.which("uv") is not None,
            "uv on PATH",
            "install uv: https://docs.astral.sh/uv/getting-started/installation/",
        ),
        _check(
            "claude",
            shutil.which("claude") is not None,
            "Claude Code on PATH",
            "install Claude Code and log in (README, First 10 minutes)",
        ),
        _check(
            "profile",
            profile_ok,
            profile_detail,
            "start `claude` in this folder and type /setup at its prompt",
        ),
    ]
    return {"ok": all(c["ok"] for c in checks), "checks": checks}
