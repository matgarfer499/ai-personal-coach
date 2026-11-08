"""`coach doctor`: first-run checks, so a new user sees what is missing and the command that fixes
it (README "First 10 minutes"). Tooling only: no coaching numbers here."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

# convention: tooling, not coaching: the Python pyproject.toml declares (`requires-python`).
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


SETUP_FIX = "start `claude` in this folder and type /setup at its prompt"


def _profile(data_dir: Path) -> tuple[bool, str, str]:
    from coach.cli import PROFILE_REQUIRED, _missing  # the same list `coach profile show` uses
    from coach.profile import load_profile

    path = data_dir / "profile.yaml"
    if not path.exists():
        return False, "no profile yet", SETUP_FIX
    try:
        profile = load_profile(path)
    except (ValueError, OSError) as err:
        # /setup reads the profile first, so it fails on this file too
        return False, str(err), f"fix the line named above in {path}, or move the file away"
    missing = [f for f in PROFILE_REQUIRED if _missing(profile, f)]
    return not missing, "missing: " + ", ".join(missing) if missing else "complete", SETUP_FIX


def text(report: dict) -> str:
    """The report as a list a person reads; `coach doctor --json` gives the JSON."""
    lines = [
        f"{'ok  ' if c['ok'] else 'FIX '} {c['check']}: {' '.join(c['detail'].split())}"
        + ("" if c["ok"] else f"\n      -> {c['fix']}")
        for c in report["checks"]
    ]
    profile = next(c for c in report["checks"] if c["check"] == "profile")
    others = [c["check"] for c in report["checks"] if not c["ok"] and c is not profile]
    if report["ok"]:
        lines.append("All good.")
    if others:
        lines.append(f"Fix these first: {', '.join(others)}.")
    if not profile["ok"] and profile["fix"] == SETUP_FIX:
        lines.append("A missing or incomplete profile is expected before /setup finishes.")
    return "\n".join(lines) + "\n"


def run(data_dir: Path) -> dict:
    data_dir = Path(data_dir)
    python = sys.version_info[:2]
    data_ok, data_detail = _data_dir(data_dir)
    profile_ok, profile_detail, profile_fix = _profile(data_dir)
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
            profile_fix,
        ),
    ]
    return {"ok": all(c["ok"] for c in checks), "checks": checks}
