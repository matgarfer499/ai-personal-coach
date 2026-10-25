"""Mechanical checks for the knowledge base.

Offline (default): source IDs resolve and are all cited, one valid grade per rule, no en or em
dashes, an "Evidence checked on" date in every rule file, a fresh `index.md` and README counts
that match it.

Online (`--online --ids S801,S802`): for sources with a PubMed URL, check that PubMed's record is
the cited paper (DOI match, or a title match when either side has no DOI), and warn about decimals
in the `Supports:` note that are not in the abstract.

Usage: uv run python scripts/check_knowledge.py [--knowledge-dir DIR] [--online --ids S1,S2]
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import time
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from build_knowledge_index import (
    SOURCE_HEADING_RE,
    build_index,
    counts,
    readme_path,
    readme_with_counts,
)

from coach.knowledge import (
    CHECKED_RE,
    CITE_RE,
    GRADES,
    KNOWLEDGE_DIR,
    blank_fences,
    checked_date,
    header,
    iter_rules,
    parse_heading,
    read,
    rule_files,
)

PUBMED_RE = re.compile(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)")
DOI_RE = re.compile(r"DOI: \[(10\.[^\]]+)\]")
DECIMAL_RE = re.compile(r"(?<![\d.])\d+\.\d+(?!\.?\d)")
DASHES = {"–": "U+2013 en dash", "—": "U+2014 em dash"}

# convention: title-match tolerances (tooling, not coaching). The citation must reproduce, in
# one unbroken run, half of the PubMed title or 80 characters for very long titles, and never less
# than 20 characters, after study-design boilerplate is removed from both sides.
LONG_TITLE_RUN = 80
MIN_TITLE_RUN = 20
BOILERPLATE = re.compile(
    r"anupdated|asystematicreview|andmetaanalysis|metaanalysis|ofrandomi[sz]edcontrolledtrials"
    r"|arandomi[sz]edcontrolledtrial|anumbrellareview|anarrativereview|positionstand"
)

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def check_ids(knowledge_dir: Path) -> list[str]:
    knowledge_dir = Path(knowledge_dir)
    defined = set(SOURCE_HEADING_RE.findall(read(knowledge_dir / "sources.md")))
    cited: dict[str, str] = {}
    for path in rule_files(knowledge_dir):
        for sid in CITE_RE.findall(read(path)):
            cited.setdefault(sid, path.name)
    errors = [f"{cited[s]}: [{s}] is not in sources.md" for s in sorted(set(cited) - defined)]
    errors += [f"sources.md: {s} is never cited" for s in sorted(defined - set(cited))]
    return errors


def check_grades(path: Path) -> list[str]:
    errors = []
    for rule in iter_rules(read(path)):
        grades = rule.grades
        where = f"{path}:{rule.line}: rule '{rule.heading}'"
        if len(grades) != 1:
            errors.append(f"{where} has {len(grades)} Grade lines (expected 1)")
        elif grades[0] not in GRADES:
            errors.append(f"{where} has grade '{grades[0]}' (expected one of {', '.join(GRADES)})")
    return errors


def check_dashes(path: Path) -> list[str]:
    errors = []
    for lineno, line in enumerate(read(path).splitlines(), start=1):
        for char, name in DASHES.items():
            if char in line:
                errors.append(f"{path}:{lineno}: {name}")
    return errors


def check_checked_date(path: Path) -> list[str]:
    text = read(path)
    if checked_date(text) is not None:
        return []
    if match := CHECKED_RE.search(header(text)):
        return [f"{path}: invalid date in 'Evidence checked on {match.group(1)}'"]
    return [f"{path}: no 'Evidence checked on YYYY-MM-DD' in the header"]


def check_duplicate_headings(path: Path) -> list[str]:
    """`section(file, heading)` returns the first match, so every heading must be unique."""
    seen: dict[str, int] = {}
    errors = []
    for lineno, mark in enumerate(blank_fences(read(path).splitlines()), start=1):
        if (found := parse_heading(mark)) is None:
            continue
        heading = found[1]
        if heading in seen:
            errors.append(f"{path}:{lineno}: heading '{heading}' repeats line {seen[heading]}")
        else:
            seen[heading] = lineno
    return errors


def check_index_fresh(knowledge_dir: Path) -> list[str]:
    index = Path(knowledge_dir) / "index.md"
    rebuild = "run uv run python scripts/build_knowledge_index.py"
    if not index.exists():
        return [f"{index} is missing: {rebuild}"]
    if read(index) != build_index(knowledge_dir):
        return [f"{index} is stale: {rebuild}"]
    return []


def check_readme_counts(knowledge_dir: Path) -> list[str]:
    """README.md states the rule and source counts; a research merge must not leave them stale."""
    readme = readme_path(knowledge_dir)
    if not readme.exists():
        return []
    text = read(readme)
    updated = readme_with_counts(text, knowledge_dir)
    if updated is None:
        return [f"{readme} has no counts line (N rule files (...), N graded rules, N sources)"]
    if updated != text:
        totals = counts(knowledge_dir)
        return [
            f"{readme} counts are stale (now {totals['rules']} graded rules, "
            f"{totals['sources']} sources): run uv run python scripts/build_knowledge_index.py"
        ]
    return []


@dataclass
class Source:
    sid: str
    citation: str
    pmid: str | None
    doi: str | None
    supports: str


def parse_sources(path: Path) -> dict[str, Source]:
    text = read(path)
    matches = list(SOURCE_HEADING_RE.finditer(text))
    sources = {}
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        lines = [line.strip() for line in text[match.end() : end].strip().splitlines()]
        url_line = next((line for line in lines if line.startswith("URL:")), "")
        pmid = PUBMED_RE.search(url_line)
        doi = DOI_RE.search("\n".join(lines))
        supports = next((line for line in lines if line.startswith("Supports:")), "")
        sources[match.group(1)] = Source(
            sid=match.group(1),
            citation=lines[0] if lines else "",
            pmid=pmid.group(1) if pmid else None,
            doi=doi.group(1).lower() if doi else None,
            supports=supports.removeprefix("Supports:").strip(),
        )
    return sources


def _normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def titles_match(pubmed_title: str, citation: str) -> bool:
    """Fallback identity test when a DOI is missing on either side.

    Citations abbreviate organisations ("ACSM", "EASD") and drop trailing clauses, so an exact
    substring test gives false alarms. Instead the citation must share one long unbroken run of
    normalised text with the title, after removing study-design boilerplate that unrelated
    reviews share ("a systematic review and meta-analysis").
    """
    title = BOILERPLATE.sub("", _normalise(pubmed_title))
    cite = BOILERPLATE.sub("", _normalise(citation))
    if not title:
        return False
    match = difflib.SequenceMatcher(None, title, cite, autojunk=False).find_longest_match()
    return match.size >= max(MIN_TITLE_RUN, min(len(title) / 2, LONG_TITLE_RUN))


def pubmed_doi(record: dict) -> str | None:
    for article_id in record.get("articleids", []):
        if article_id.get("idtype") == "doi" and article_id.get("value"):
            return article_id["value"].lower()
    return None


def fetch_url(url: str) -> str:
    """Fetch a URL politely (NCBI allows 3 requests per second without an API key)."""
    time.sleep(0.4)
    request = urllib.request.Request(url, headers={"User-Agent": "ai-personal-coach-checks"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def check_online(
    knowledge_dir: Path, ids: list[str], fetch: Callable[[str], str] = fetch_url
) -> tuple[list[str], list[str]]:
    sources = parse_sources(Path(knowledge_dir) / "sources.md")
    errors, warnings = [], []
    for sid in ids:
        source = sources.get(sid)
        if source is None:
            errors.append(f"{sid}: not in sources.md")
            continue
        if source.pmid is None:
            warnings.append(f"{sid}: no PubMed URL, title not checked online")
            continue
        query = f"db=pubmed&id={source.pmid}"
        summary = json.loads(fetch(f"{EUTILS}/esummary.fcgi?{query}&retmode=json"))
        record = summary.get("result", {}).get(source.pmid, {})
        title, doi = record.get("title", ""), pubmed_doi(record)
        if source.doi and doi:
            if source.doi != doi:
                errors.append(f"{sid}: PubMed {source.pmid} has DOI {doi}, sources.md {source.doi}")
        elif not titles_match(title, source.citation):
            errors.append(f"{sid}: PubMed title {title!r} does not match the citation")
        abstract = fetch(f"{EUTILS}/efetch.fcgi?{query}&rettype=abstract&retmode=text")
        in_abstract = set(DECIMAL_RE.findall(abstract))
        for number in DECIMAL_RE.findall(source.supports):
            if number not in in_abstract:
                warnings.append(f"{sid}: {number} from the Supports note is not in the abstract")
    return errors, warnings


def main(argv: list[str] | None = None, fetch: Callable[[str], str] = fetch_url) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--knowledge-dir", type=Path, default=KNOWLEDGE_DIR)
    parser.add_argument("--online", action="store_true", help="check PubMed titles and decimals")
    parser.add_argument("--ids", default="", help="comma-separated source IDs for --online")
    args = parser.parse_args(argv)
    kdir = args.knowledge_dir

    errors = check_ids(kdir)
    for path in rule_files(kdir):
        errors += check_grades(path) + check_checked_date(path) + check_duplicate_headings(path)
    for path in sorted(kdir.glob("*.md")):
        errors += check_dashes(path)
    errors += check_index_fresh(kdir)
    errors += check_readme_counts(kdir)
    warnings: list[str] = []
    if args.online:
        ids = [i.strip() for i in args.ids.split(",") if i.strip()]
        if not ids:
            parser.error("--online needs --ids")
        online_errors, warnings = check_online(kdir, ids, fetch=fetch)
        errors += online_errors

    for line in errors:
        print(f"ERROR {line}")
    for line in warnings:
        print(f"WARN  {line}")
    totals = counts(kdir)
    print(
        f"{totals['sources']} sources, {totals['rules']} rules ({totals['strong']} strong, "
        f"{totals['moderate']} moderate, {totals['emerging']} emerging); "
        f"{len(errors)} errors, {len(warnings)} warnings"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
