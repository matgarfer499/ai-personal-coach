from datetime import date
from pathlib import Path

import pytest

from coach import knowledge

GOOD = Path(__file__).parent.parent / "fixtures" / "knowledge" / "good"


def test_section_returns_one_rule_up_to_next_rule():
    text = knowledge.section("widgets.md", "Lift widgets slowly", knowledge_dir=GOOD)
    assert text.startswith("### Lift widgets slowly\n")
    assert "**Grade:** moderate" in text
    assert "Store widgets dry" not in text


def test_section_last_rule_of_a_section_stops_at_next_section():
    text = knowledge.section("widgets", "Store widgets dry", knowledge_dir=GOOD)
    assert "**Grade:** strong" in text
    assert "## Widget care" not in text


def test_section_returns_whole_h2_section():
    text = knowledge.section("widgets.md", "Handling widgets", knowledge_dir=GOOD)
    assert text.startswith("## Handling widgets\n")
    assert "### Lift widgets slowly" in text and "### Store widgets dry" in text
    assert "Polish widgets weekly" not in text


def test_section_last_in_file():
    text = knowledge.section("widgets.md", "Polish widgets weekly", knowledge_dir=GOOD)
    assert text.rstrip().endswith("**Sources:** [S002]")


def test_section_not_found_names_file_and_heading():
    with pytest.raises(knowledge.SectionNotFound, match="widgets.md.*No such rule"):
        knowledge.section("widgets.md", "No such rule", knowledge_dir=GOOD)


def test_iter_rules_reports_section_and_line():
    rules = list(knowledge.iter_rules((GOOD / "widgets.md").read_text()))
    assert [(r.heading, r.section, r.line) for r in rules] == [
        ("Lift widgets slowly", "Handling widgets", 11),
        ("Store widgets dry", "Handling widgets", 17),
        ("Polish widgets weekly", "Widget care", 24),
    ]
    assert rules[0].grade == "moderate"
    assert rules[1].source_ids == ["S002", "S001"]


def _kdir(tmp_path, checked):
    (tmp_path / "a.md").write_text(f"# A\n\n> Evidence checked on {checked}.\n")
    (tmp_path / "b.md").write_text("# B\n\n> Evidence checked on 2026-09-01.\n")
    (tmp_path / "sources.md").write_text("# Sources\n")
    return tmp_path


def test_stale_files(tmp_path):
    kdir = _kdir(tmp_path, "2026-01-31")
    # 2026-01-31 + 6 months = 2026-07-31: stale only after that day.
    assert knowledge.stale_files(6, date(2026, 7, 31), knowledge_dir=kdir) == []
    assert knowledge.stale_files(6, date(2026, 8, 1), knowledge_dir=kdir) == [
        ("a.md", date(2026, 1, 31))
    ]


def test_stale_files_month_end_clamps(tmp_path):
    kdir = _kdir(tmp_path, "2026-08-31")
    # 2026-08-31 + 6 months clamps to 2027-02-28.
    assert knowledge.stale_files(6, date(2027, 2, 28), knowledge_dir=kdir) == []
    # b.md (2026-09-01) reaches its 6 months on 2027-03-01, so it is not stale yet.
    assert knowledge.stale_files(6, date(2027, 3, 1), knowledge_dir=kdir) == [
        ("a.md", date(2026, 8, 31))
    ]


def test_stale_files_missing_date_counts_as_stale(tmp_path):
    (tmp_path / "c.md").write_text("# C\n")
    assert knowledge.stale_files(6, date(2026, 1, 1), knowledge_dir=tmp_path) == [("c.md", None)]


def test_real_knowledge_files_have_dates():
    assert knowledge.stale_files(1200, date(2026, 10, 24)) == []


FENCED = """# F

> Evidence checked on 2026-01-01.

## Real section

### Real rule
**Grade:** strong
```
## not a section
### not a rule
```
Still part of the real rule.

## Next
"""


def test_fenced_code_is_not_read_as_headings(tmp_path):
    (tmp_path / "f.md").write_text(FENCED)
    rules = list(knowledge.iter_rules(FENCED))
    assert [r.heading for r in rules] == ["Real rule"]
    assert "### not a rule" in rules[0].body
    text = knowledge.section("f", "Real rule", knowledge_dir=tmp_path)
    assert text.rstrip().endswith("Still part of the real rule.")
    assert knowledge.section("f", "Real section", knowledge_dir=tmp_path).count("##") == 4


def test_invalid_checked_date_is_none_and_stale(tmp_path):
    (tmp_path / "x.md").write_text("# X\n\n> Evidence checked on 2026-13-45.\n")
    assert knowledge.checked_date((tmp_path / "x.md").read_text()) is None
    assert knowledge.stale_files(6, date(2026, 1, 1), knowledge_dir=tmp_path) == [("x.md", None)]
