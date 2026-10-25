import shutil
from pathlib import Path

import build_knowledge_index as bki
import check_knowledge as ck

GOOD = Path(__file__).parent.parent / "fixtures" / "knowledge" / "good"


def test_build_index_lists_every_rule_with_section_grade_sources_and_line():
    text = bki.build_index(GOOD)
    assert "## widgets.md" in text
    assert "Evidence checked on 2026-01-15, 3 rules" in text
    assert "| 11 | Handling widgets | Lift widgets slowly | moderate | S001 |" in text
    assert "| 17 | Handling widgets | Store widgets dry | strong | S002, S001 |" in text
    assert "| 24 | Widget care | Polish widgets weekly | emerging | S002 |" in text
    assert "sources.md" not in text.split("\n## ", 1)[1]


def test_build_index_does_not_depend_on_file_creation_order_or_location(tmp_path):
    names = ["widgets.md", "sources.md"]
    (tmp_path / "zeta.md").write_text("# Z\n\n> Evidence checked on 2026-01-01.\n")
    for name in reversed(names):
        (tmp_path / name).write_text((GOOD / name).read_text())
    (tmp_path / "alpha.md").write_text("# A\n\n> Evidence checked on 2026-01-01.\n")
    text = bki.build_index(tmp_path)
    assert text.index("## alpha.md") < text.index("## widgets.md") < text.index("## zeta.md")
    assert str(tmp_path) not in text
    widgets = text.split("## widgets.md", 1)[1].split("## zeta.md")[0].rstrip()
    assert widgets in bki.build_index(GOOD)


def test_build_index_escapes_pipes(tmp_path):
    (tmp_path / "x.md").write_text(
        "# X\n\n> Evidence checked on 2026-01-01.\n\n## A | B\n\n### C | D\n**Grade:** strong\n"
    )
    assert "| 7 | A \\| B | C \\| D | strong |  |" in bki.build_index(tmp_path)


def test_main_writes_index_and_check_detects_staleness(tmp_path):
    kdir = tmp_path / "k"
    shutil.copytree(GOOD, kdir)
    assert bki.main(["--knowledge-dir", str(kdir)]) == 0
    assert ck.check_index_fresh(kdir) == []
    rules = kdir / "widgets.md"
    rules.write_text(rules.read_text().replace("Polish widgets weekly", "Polish widgets often"))
    errors = ck.check_index_fresh(kdir)
    assert errors and "stale" in errors[0]


README_LINE = (
    "| `knowledge/` | 1 rule files (widgets and more), 99 graded rules, 98 sources; "
    "`index.md` lists every rule |\n"
)


def copy_with_readme(tmp_path, readme):
    kdir = tmp_path / "k"
    shutil.copytree(GOOD, kdir)
    (tmp_path / "README.md").write_text(readme)
    return kdir


def test_counts_cover_rules_and_sources():
    assert bki.counts(GOOD) == {
        "sources": 2,
        "rules": 3,
        "strong": 1,
        "moderate": 1,
        "emerging": 1,
    }


def test_main_rewrites_the_counts_line_in_the_readme_beside_the_knowledge_dir(tmp_path):
    kdir = copy_with_readme(tmp_path, f"# Title\n\n{README_LINE}\nUntouched text.\n")
    assert bki.main(["--knowledge-dir", str(kdir)]) == 0
    text = (tmp_path / "README.md").read_text()
    assert "1 rule files (widgets and more), 3 graded rules, 2 sources;" in text
    assert text.startswith("# Title\n\n| `knowledge/` |") and text.endswith("Untouched text.\n")


def test_check_flags_stale_readme_counts_until_the_index_is_rebuilt(tmp_path):
    kdir = copy_with_readme(tmp_path, README_LINE)
    bki.main(["--knowledge-dir", str(kdir)])
    assert ck.check_readme_counts(kdir) == []
    rules = kdir / "widgets.md"  # a research merge adds a rule: the README is now behind
    rules.write_text(rules.read_text() + "\n### One more rule\n**Grade:** strong\n\nText [S001].\n")
    errors = ck.check_readme_counts(kdir)
    assert len(errors) == 1 and "4 graded rules" in errors[0]
    assert "build_knowledge_index" in errors[0]
    bki.main(["--knowledge-dir", str(kdir)])
    assert ck.check_readme_counts(kdir) == []


def test_readme_without_a_counts_line_is_an_error_not_a_silent_skip(tmp_path, capsys):
    kdir = copy_with_readme(tmp_path, "# Title\n\nNo numbers here.\n")
    assert "counts line" in ck.check_readme_counts(kdir)[0]
    assert bki.main(["--knowledge-dir", str(kdir)]) == 1
    assert "counts line" in capsys.readouterr().err


def test_no_readme_beside_the_knowledge_dir_means_nothing_to_check(tmp_path):
    kdir = tmp_path / "k"
    shutil.copytree(GOOD, kdir)
    assert ck.check_readme_counts(kdir) == []
    assert bki.main(["--knowledge-dir", str(kdir)]) == 0


def test_check_main_fails_on_stale_readme_counts(tmp_path, capsys):
    kdir = copy_with_readme(tmp_path, README_LINE)
    (kdir / "index.md").write_text(bki.build_index(kdir))  # index fresh, README stale
    assert ck.main(["--knowledge-dir", str(kdir)]) == 1
    assert "README.md" in capsys.readouterr().out


def test_the_repos_own_readme_counts_are_current():
    assert ck.check_readme_counts(ck.KNOWLEDGE_DIR) == []
