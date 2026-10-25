"""Read the knowledge base: rule parsing, section extraction and staleness.

Skills load `knowledge/index.md`, then only the sections they need through `section()`.
"""

from __future__ import annotations

import calendar
import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"
NOT_RULE_FILES = {"sources.md", "index.md"}
GRADES = ("strong", "moderate", "emerging")

CHECKED_RE = re.compile(r"Evidence checked on (\d{4}-\d{2}-\d{2})")
# convention: the "Evidence checked on" note sits in the opening blockquote (tooling, not coaching)
HEADER_LINES = 5
CITE_RE = re.compile(r"\[(S\d+)\]")
GRADE_RE = re.compile(r"^\*\*Grade:\*\*\s*(.*?)\s*$")


class SectionNotFound(LookupError):
    pass


@dataclass
class Rule:
    heading: str
    section: str
    line: int
    body: list[str] = field(default_factory=list)

    @property
    def grades(self) -> list[str]:
        return [m.group(1) for line in self.body if (m := GRADE_RE.match(line))]

    @property
    def grade(self) -> str | None:
        grades = self.grades
        return grades[0] if len(grades) == 1 else None

    @property
    def source_ids(self) -> list[str]:
        return list(dict.fromkeys(CITE_RE.findall("\n".join(self.body))))


def rule_files(knowledge_dir: Path = KNOWLEDGE_DIR) -> list[Path]:
    return sorted(p for p in Path(knowledge_dir).glob("*.md") if p.name not in NOT_RULE_FILES)


def read(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def header(text: str) -> str:
    return "\n".join(text.splitlines()[:HEADER_LINES])


def checked_date(text: str) -> date | None:
    """The "Evidence checked on" date in a knowledge file's header; None if absent or invalid."""
    match = CHECKED_RE.search(header(text))
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None


def blank_fences(lines: list[str]) -> list[str]:
    """Copy of `lines` with fenced code blanked, so `#` lines inside fences are not headings."""
    marks, in_fence = [], False
    for line in lines:
        fence = line.lstrip().startswith("```")
        in_fence ^= fence
        marks.append("" if fence or in_fence else line)
    return marks


def parse_heading(mark: str) -> tuple[int, str] | None:
    """`(level, text)` for a `## ` (level 2) or `### ` (level 3) heading line, else None."""
    for level, prefix in ((2, "## "), (3, "### ")):
        if mark.startswith(prefix):
            return level, mark[len(prefix) :].strip()
    return None


def iter_rules(text: str) -> Iterator[Rule]:
    """Yield every `### ` rule with its enclosing `## ` section and 1-based line number."""
    section, rule = "", None
    lines = text.splitlines()
    for lineno, (line, mark) in enumerate(zip(lines, blank_fences(lines), strict=True), start=1):
        heading = parse_heading(mark)
        if heading is None:
            if rule is not None:
                rule.body.append(line)
            continue
        if rule is not None:
            yield rule
        level, title = heading
        if level == 2:
            section, rule = title, None
        else:
            rule = Rule(heading=title, section=section, line=lineno)
    if rule is not None:
        yield rule


def section(file: str, heading: str, knowledge_dir: Path = KNOWLEDGE_DIR) -> str:
    """Return one `## ` section or one `### ` rule, heading line included.

    A `## ` section runs to the next `## `; a `### ` rule runs to the next `### ` or `## `.
    """
    path = Path(knowledge_dir) / (file if file.endswith(".md") else f"{file}.md")
    lines = read(path).splitlines()
    headings = [parse_heading(mark) for mark in blank_fences(lines)]
    wanted = heading.strip()
    for start, found in enumerate(headings):
        if found is None or found[1] != wanted:
            continue
        level = found[0]
        end = next(
            (i for i in range(start + 1, len(lines)) if headings[i] and headings[i][0] <= level),
            len(lines),
        )
        return "\n".join(lines[start:end]).rstrip() + "\n"
    raise SectionNotFound(f"{path.name}: no '## ' or '### ' heading {wanted!r}")


def _add_months(day: date, months: int) -> date:
    month_index = day.month - 1 + months
    year, month = day.year + month_index // 12, month_index % 12 + 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def stale_files(
    months: int, today: date, knowledge_dir: Path = KNOWLEDGE_DIR
) -> list[tuple[str, date | None]]:
    """Rule files whose "Evidence checked on" date is more than `months` months before `today`.

    A file with no valid date has never been checked, so it counts as stale with date None
    (the plan's signature says `date`; callers must handle None).
    """
    stale = []
    for path in rule_files(knowledge_dir):
        checked = checked_date(read(path))
        if checked is None or today > _add_months(checked, months):
            stale.append((path.name, checked))
    return stale
