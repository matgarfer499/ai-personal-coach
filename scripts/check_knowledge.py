"""Mechanical checks for the knowledge base.

Offline (default): source IDs resolve and are all cited, every `see "X"` names a heading,
`Supports:` lines are at most 500 characters, one valid grade per rule, no en or em
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

# convention: longest `Supports:` line in sources.md, matching the research skill's step 4 (only
# the sentences that carry the claim's numbers, at most about 500 characters).
MAX_SUPPORTS_CHARS = 500
# a heading may itself contain quotes, so the closing quote is the one followed by punctuation
SEE_RE = re.compile(r'\b[Ss]ee(?: also)? "(.+?)"(?=[\s,;.:)]|$)')
# `(see Some Heading)`: unquoted, so only a capitalised target counts ("(see next rule)" is prose)
# An unquoted reference opens a parenthetical or follows `;` or `,` inside one.
SEE_UNQUOTED_RE = re.compile(r"(?:\(|[;,] )[Ss]ee(?: also)? (?=([^\"\s].*))")
# Prose after `see` that is not a heading: "Table 2", "Cai 2023", "D080", "S123".
PROSE_SEE_RE = re.compile(
    r"(?:(?:Table|Figure|Appendix|Box)\b.*|.*\b(?:19|20)\d\d[a-z]?|[DS]\d+|(?:above|below))$", re.I
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


def _clause(rest: str) -> str | None:
    """Text up to the `)` that closes the reference, a `;`, or a sentence end; parens balance.

    None when the line ends first: the reference wraps onto the next line and is not checked.
    """
    depth = 0
    for i, ch in enumerate(rest):
        if ch == "(":
            depth += 1
        elif (
            ch == ")" and depth == 0 or ch == ";" or ch in ".," and rest[i + 1 : i + 2] in ("", " ")
        ):
            return rest[:i].strip()
        elif ch == ")":
            depth -= 1
    return None


def _unquoted_target(rest: str, headings: set[str]) -> str | None:
    """The dangling target in the text after an unquoted `see`, or None if it is fine or prose."""
    for heading in sorted(headings, key=len, reverse=True):  # headings may contain parentheses
        if rest.startswith(heading) and not rest[len(heading) :][:1].isalnum():
            return None
    target = _clause(rest)
    if not target or PROSE_SEE_RE.match(target):
        return None
    words = target.lower().split()
    near = any(
        words[:n] == h.lower().split()[:n]
        for h in headings
        if (n := min(3, len(words), len(h.split()))) and (n > 1 or len(target) >= 4)
    )
    return target if near or (target[0].isupper() and len(words) > 1) else None


def check_references(knowledge_dir: Path) -> list[str]:
    """Every `see "X"` or `(see X)` must name a `## X` or `### X` heading in some rule file.

    Quoted targets (`see "X"`, `See also "X"`) must match a heading exactly. Unquoted targets
    (after `(see`, or `; see` / `, see`) are matched against the heading list: the longest heading
    that prefixes the text passes, which also covers headings with parentheses. Otherwise the text
    up to `)`, `;` or a sentence end is reported when a heading shares its first three words (or
    fewer, if either has fewer) with it case-insensitively (a near miss, including wrong case or a
    bare first word), or when it is a capitalised multi-word phrase. Prose such as `(see next
    rule)`, `(see above)`, `(see Below)`, `(see Table 2)`, `(see Cai 2023)`, `(see D080)`,
    `(see S012)` passes, as does a heading followed by prose (`(see Real heading for details)`).
    Fenced code blocks are skipped. The message shows the target as written (quoted only if it
    was quoted).

    Still not seen: a lowercase unquoted target that is not near a heading, a reference without
    `see` (for example "refer to X"), a reference outside parentheses and not after `;`/`,`, a
    reference wrapped across two lines, a heading in the wrong file (any rule file satisfies it),
    and references in `sources.md`, `index.md` or `README.md`.
    """
    texts = {path: read(path) for path in rule_files(knowledge_dir)}
    headings = {
        found[1]
        for text in texts.values()
        for mark in blank_fences(text.splitlines())
        if (found := parse_heading(mark)) and found[0] in (2, 3)
    }
    errors = []
    for path, text in texts.items():
        for lineno, line in enumerate(blank_fences(text.splitlines()), start=1):
            targets = [f'"{t}"' for t in SEE_RE.findall(line) if t not in headings]
            targets += [
                t
                for rest in SEE_UNQUOTED_RE.findall(line)
                if (t := _unquoted_target(rest, headings))
            ]
            errors += [f"{path}:{lineno}: see {t} names no heading" for t in targets]
    return errors


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


def check_quote_length(knowledge_dir: Path) -> list[str]:
    sources = parse_sources(Path(knowledge_dir) / "sources.md")
    return [
        f"sources.md: {sid} Supports line is {n} characters (max {MAX_SUPPORTS_CHARS})"
        for sid, source in sources.items()
        if (n := len(f"Supports: {source.supports}")) > MAX_SUPPORTS_CHARS
    ]


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
    errors += check_references(kdir) + check_quote_length(kdir)
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
