"""Mechanical checks on the coach skills (.claude/skills/*/SKILL.md)."""

import re
import shlex
from pathlib import Path

import pytest
import yaml

from coach import knowledge
from coach.cli import build_parser

ROOT = Path(__file__).parent.parent.parent
SKILLS = ROOT / ".claude" / "skills"
COACH_SKILLS = ["setup", "checkin", "import", "plan", "review", "menu"]
SECTIONS = ["## When to use", "## Reads", "## Steps", "## Writes", "## Output", "## Safety"]
WRITTEN = sorted(p.parent.name for p in SKILLS.glob("*/SKILL.md"))


def frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert match, "missing YAML frontmatter"
    return yaml.safe_load(match.group(1))


def is_placeholder(word):
    return word.isupper()  # `coach X`, `FILE "HEADING"` in the ground rules


def commands(text):
    """Every concrete `coach ...` invocation inside backticks or code blocks."""
    found = re.findall(r"`coach ([^`]+)`", text)
    for block in re.findall(r"```[a-z]*\n(.*?)```", text, re.S):
        found += [
            line.strip()[len("coach ") :]
            for line in block.splitlines()
            if line.strip().startswith("coach ")
        ]
    return [c for c in found if not is_placeholder(c.split()[0])]


def subcommands():
    parser = build_parser()
    action = next(a for a in parser._actions if a.dest == "command")
    return set(action.choices)


def test_every_coach_skill_exists():
    assert set(COACH_SKILLS) <= set(WRITTEN)


@pytest.mark.parametrize("name", WRITTEN)
def test_skill_file(name):
    text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
    meta = frontmatter(text)
    assert meta["name"] == name
    assert meta["description"].startswith("Use when")
    assert len(yaml.safe_dump(meta)) <= 1024
    for section in SECTIONS:
        assert section in text, f"{name}: missing {section}"
    assert "docs/safety.md" in text, f"{name}: must point to the deferral line"
    assert "–" not in text and "—" not in text, f"{name}: en or em dash"


@pytest.mark.parametrize("name", WRITTEN)
def test_cited_commands_exist(name):
    text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
    known = subcommands()
    for command in commands(text):
        assert command.split()[0] in known, f"{name}: unknown command `coach {command}`"


@pytest.mark.parametrize("name", WRITTEN)
def test_cited_knowledge_sections_resolve(name):
    text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
    for command in commands(text):
        words = shlex.split(command)
        if words[:2] == ["knowledge", "section"]:
            assert len(words) == 4, f"{name}: `coach {command}` needs FILE and HEADING"
            if is_placeholder(words[2]):
                continue
            knowledge.section(words[2], words[3])  # raises SectionNotFound on a renamed rule


def ground_rules(text):
    return text[text.index("## Ground rules") : text.index("## When to use")]


def test_ground_rules_are_identical_in_every_skill():
    blocks = {
        name: ground_rules((SKILLS / name / "SKILL.md").read_text(encoding="utf-8"))
        for name in COACH_SKILLS
    }
    assert len(set(blocks.values())) == 1, sorted(blocks)


@pytest.mark.parametrize("name", COACH_SKILLS)
def test_ground_rules_defer_to_the_configured_data_dir(name):
    """`COACH_DATA_DIR` must work: no skill may pin `--data-dir data/` over it."""
    rules = ground_rules((SKILLS / name / "SKILL.md").read_text(encoding="utf-8"))
    assert "uv run python -m coach X --json" in rules
    assert "--data-dir DATA X" not in rules
    assert "`data_dir`" in rules and "coach profile show" in rules
    assert "COACH_DATA_DIR" in rules


@pytest.mark.parametrize("name", WRITTEN)
def test_skills_never_pin_the_data_dir(name):
    text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
    assert "--data-dir data" not in text


def test_research_forbids_personal_data_instead_of_banning_coaching_use():
    text = (SKILLS / "research" / "SKILL.md").read_text(encoding="utf-8")
    assert "Not while coaching" not in text
    assert "never put personal or\n  client data" in text
    assert "branch" in text and "commit message" in text
