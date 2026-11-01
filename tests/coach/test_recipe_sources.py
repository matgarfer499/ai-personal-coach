"""The curated recipe sources /menu reads: recipe-sources.yaml at the root and in each region.

They hold links and one line on why each source is good, never recipe text."""

import re
from datetime import date
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parent.parent.parent
FILES = [ROOT / "recipe-sources.yaml", *sorted(ROOT.glob("regions/*/recipe-sources.yaml"))]
FIELDS = {"id", "name", "url", "kind", "language", "cuisines", "tags", "why", "checked_on"}
KINDS = {"site", "youtube"}
TAGS = {"healthy", "quick", "budget", "batch", "beginner"}
SLUG = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
WHY_MAX = 120


def problems(entry) -> list[str]:
    """What is wrong with one entry; empty when it is fine."""
    if not isinstance(entry, dict):
        return [f"not a mapping: {entry!r}"]
    found = []
    if {"steps", "ingredients", "recipe"} & set(entry):
        found.append("recipe text: only a link and why it is good")
    if set(entry) != FIELDS:
        found.append(f"keys must be exactly {sorted(FIELDS)}, not {sorted(entry)}")
    text = {k: entry.get(k) for k in ("id", "name", "url", "kind", "language", "why")}
    if not all(isinstance(v, str) and v.strip() for v in text.values()):
        return found + ["id, name, url, kind, language and why must be text"]
    if not SLUG.fullmatch(text["id"]):
        found.append(f"id is not a kebab slug: {text['id']!r}")
    if not text["url"].startswith("https://"):
        found.append(f"url is not https: {text['url']!r}")
    if text["kind"] not in KINDS:
        found.append(f"kind must be one of {sorted(KINDS)}: {text['kind']!r}")
    if not re.fullmatch(r"[a-z]{2}", text["language"]):
        found.append(f"language is not a two-letter code: {text['language']!r}")
    if len(text["why"]) > WHY_MAX:
        found.append(f"why is over {WHY_MAX} characters: {len(text['why'])}")
    cuisines, tags = entry.get("cuisines"), entry.get("tags")
    if (
        not isinstance(cuisines, list)
        or not cuisines
        or not all(isinstance(c, str) and SLUG.fullmatch(c) for c in cuisines)
    ):
        found.append(f"cuisines must be lower-case words: {cuisines!r}")
    if not isinstance(tags, list) or not set(tags) <= TAGS:
        found.append(f"tags must be some of {sorted(TAGS)}: {tags!r}")
    if not isinstance(entry.get("checked_on"), date):
        found.append(f"checked_on must be YYYY-MM-DD, unquoted: {entry.get('checked_on')!r}")
    return found


def load(path: Path) -> list:
    entries = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(entries, list) and entries, f"{path.name}: a list of sources"
    return entries


def test_the_root_and_spain_files_exist():
    assert FILES[0].exists() and ROOT / "regions" / "es" / "recipe-sources.yaml" in FILES


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_every_source_is_well_formed(path):
    for entry in load(path):
        assert not problems(entry), entry.get("id") if isinstance(entry, dict) else entry


def test_ids_and_urls_are_unique_across_files():
    entries = [entry for path in FILES for entry in load(path)]
    for key in ("id", "url"):
        values = [entry[key] for entry in entries]
        assert len(values) == len(set(values)), [v for v in values if values.count(v) > 1]


GOOD = {
    "id": "example-kitchen",
    "name": "Example Kitchen",
    "url": "https://example.org/",
    "kind": "site",
    "language": "en",
    "cuisines": ["latin-american"],
    "tags": [],
    "why": "Tested home recipes",
    "checked_on": date(2026, 11, 1),
}


@pytest.mark.parametrize(
    "change",
    [
        {"steps": ["Chop", "Fry"]},
        {"ingredients": ["rice"]},
        {"recipe": "Fry the rice"},
        {"id": "Example Kitchen"},
        {"url": "http://example.org/"},
        {"kind": "blog"},
        {"language": "eng"},
        {"cuisines": ["Spanish"]},
        {"tags": ["tasty"]},
        {"why": "x" * (WHY_MAX + 1)},
        {"checked_on": "2026-11-01"},
    ],
)
def test_the_check_catches_a_bad_entry(change):
    assert not problems(GOOD)
    assert problems(GOOD | change)
