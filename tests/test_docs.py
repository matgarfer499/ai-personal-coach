"""The safety and conventions docs stay in step with the code."""

import dataclasses
import re
from pathlib import Path

from coach import safety

ROOT = Path(__file__).parent.parent
SAFETY_DOC = (ROOT / "docs" / "safety.md").read_text(encoding="utf-8")


def _heading(rule):
    return re.match(r'\S+\.md: "([^"]+)"', rule).group(1)


def test_safety_doc_names_every_flag():
    for field in dataclasses.fields(safety.SafetyFlags):
        if field.name not in ("screened", "reasons"):
            assert f"`{field.name}`" in SAFETY_DOC, field.name


def test_safety_doc_names_every_rule_the_flags_cite():
    rules = [
        v
        for k, v in vars(safety).items()
        if k.isupper() and isinstance(v, str) and re.match(r'\S+\.md: "', v)
    ]
    assert len(rules) >= 9
    for rule in rules:
        assert _heading(rule) in SAFETY_DOC, rule


def test_safety_doc_has_the_required_sections():
    for section in ("What the coach is not", "The deferral line", "Screening", "Red flags"):
        assert f"## {section}" in SAFETY_DOC, section


CONVENTIONS_DOC = (ROOT / "docs" / "conventions.md").read_text(encoding="utf-8")
ASSIGNED = re.compile(r"^\s*([A-Za-z_][\w, ]*?)\s*(?::[^=]+)?=")
LABEL = re.compile(r"#.*\bconvention\s*[:(]")


def convention_constants():
    """Names assigned right after a `# convention:` comment block, or on a line carrying one."""
    found = set()
    for path in sorted((ROOT / "coach").glob("**/*.py")) + sorted((ROOT / "scripts").glob("*.py")):
        lines = path.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            if not LABEL.search(line):
                continue
            j = i
            if line.lstrip().startswith("#"):
                while j < len(lines) and lines[j].lstrip().startswith("#"):
                    j += 1
            match = ASSIGNED.match(lines[j]) if j < len(lines) else None
            if match:
                found |= {(path.name, n.strip()) for n in match.group(1).split(",")}
    return found


def test_every_convention_constant_is_in_conventions_doc():
    constants = convention_constants()
    assert len(constants) >= 15
    missing = [f"{f}: {name}" for f, name in sorted(constants) if name not in CONVENTIONS_DOC]
    assert not missing, missing
