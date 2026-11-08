import json
from datetime import date
from pathlib import Path

import check_knowledge as ck

FIXTURES = Path(__file__).parent.parent / "fixtures" / "knowledge"
GOOD = FIXTURES / "good"
BAD = FIXTURES / "bad"


def test_rule_files_skip_sources_and_index(tmp_path):
    for name in ("a.md", "sources.md", "index.md"):
        (tmp_path / name).write_text("# x\n", encoding="utf-8")
    assert [p.name for p in ck.rule_files(tmp_path)] == ["a.md"]


def test_good_fixture_passes_every_offline_check():
    assert ck.check_ids(GOOD) == []
    for path in ck.rule_files(GOOD):
        assert ck.check_grades(path) == []
        assert ck.check_dashes(path) == []
        assert ck.check_checked_date(path) == []


def test_check_ids_reports_unknown_and_uncited():
    errors = ck.check_ids(BAD)
    assert any("S999" in e and "not in sources.md" in e for e in errors)
    assert any("S002" in e and "never cited" in e for e in errors)
    assert len(errors) == 2


def test_check_grades_reports_duplicate_missing_and_invalid():
    errors = ck.check_grades(BAD / "gadgets.md")
    assert any("Two grades" in e and "2 Grade lines" in e for e in errors)
    assert any("No grade" in e and "0 Grade lines" in e for e in errors)
    assert any("Wrong grade value" in e and "'high'" in e for e in errors)
    assert len(errors) == 3


def test_check_dashes_reports_line_numbers():
    errors = ck.check_dashes(BAD / "gadgets.md")
    assert len(errors) == 2
    assert errors[0].startswith(f"{BAD / 'gadgets.md'}:8:")
    assert "U+2013" in errors[0]
    assert "U+2014" in errors[1]


def test_check_checked_date():
    errors = ck.check_checked_date(BAD / "gadgets.md")
    assert errors and "Evidence checked on" in errors[0]


def test_checked_date_parses():
    assert ck.checked_date((GOOD / "widgets.md").read_text(encoding="utf-8")) == date(2026, 1, 15)
    assert ck.checked_date("no date here") is None


def test_index_fresh_passes_on_fixture_and_missing_index_is_an_error(tmp_path):
    assert ck.check_index_fresh(GOOD) == []
    (tmp_path / "sources.md").write_text("# Sources\n", encoding="utf-8")
    errors = ck.check_index_fresh(tmp_path)
    assert len(errors) == 1 and "missing" in errors[0]


def test_check_checked_date_reports_invalid_date_without_crashing(tmp_path):
    path = tmp_path / "x.md"
    path.write_text("# X\n\n> Evidence checked on 2026-02-30.\n", encoding="utf-8")
    errors = ck.check_checked_date(path)
    assert len(errors) == 1 and "invalid date" in errors[0]


def test_check_checked_date_ignores_a_date_outside_the_header(tmp_path):
    path = tmp_path / "x.md"
    path.write_text(
        "# X\n\n> header\n\n## A\n\nEvidence checked on 2026-01-01.\n", encoding="utf-8"
    )
    assert "no 'Evidence checked on" in ck.check_checked_date(path)[0]


def test_check_duplicate_headings(tmp_path):
    path = tmp_path / "x.md"
    path.write_text(
        "# X\n\n## A\n\n### Same\n**Grade:** strong\n\n## B\n\n### Same\n**Grade:** strong\n"
        "\n```\n### Same\n```\n",
        encoding="utf-8",
    )
    errors = ck.check_duplicate_headings(path)
    assert errors == [f"{path}:10: heading 'Same' repeats line 5"]
    assert ck.check_duplicate_headings(GOOD / "widgets.md") == []


def test_counts():
    counts = ck.counts(GOOD)
    assert counts == {"sources": 2, "rules": 3, "strong": 1, "moderate": 1, "emerging": 1}


def test_main_offline_exit_codes(capsys):
    assert ck.main(["--knowledge-dir", str(GOOD)]) == 0
    out = capsys.readouterr().out
    assert "2 sources" in out and "3 rules" in out
    assert ck.main(["--knowledge-dir", str(BAD)]) == 1


def test_parse_sources():
    sources = ck.parse_sources(GOOD / "sources.md")
    assert set(sources) == {"S001", "S002"}
    assert sources["S001"].pmid == "11111111"
    assert sources["S002"].pmid is None
    assert sources["S001"].doi == "10.1/x"
    assert sources["S002"].doi is None
    assert "Slow lifting doubles widget life" in sources["S001"].citation
    assert sources["S001"].supports.startswith("40 participants")


def _stub_fetch(title, abstract, doi=None):
    calls = []

    def fetch(url):
        calls.append(url)
        if "esummary" in url:
            record = {"title": title, "articleids": [{"idtype": "pubmed", "value": "11111111"}]}
            if doi:
                record["articleids"].append({"idtype": "doi", "value": doi})
            return json.dumps({"result": {"uids": ["11111111"], "11111111": record}})
        if "efetch" in url:
            return abstract
        raise AssertionError(url)

    return fetch, calls


def test_online_title_match_and_decimal_warnings():
    fetch, calls = _stub_fetch(
        "Slow lifting doubles widget life: a randomised trial.",
        "Forty adults lifted widgets. Widget life ratio was 2.0.",
    )
    errors, warnings = ck.check_online(GOOD, ["S001"], fetch=fetch)
    assert errors == []
    # 0.45 is in the Supports note but not in the abstract: a warning, not an error.
    assert len(warnings) == 1 and "0.45" in warnings[0]
    assert any("11111111" in c for c in calls)


def test_online_title_mismatch_is_an_error():
    fetch, _ = _stub_fetch("Something else entirely", "")
    errors, _ = ck.check_online(GOOD, ["S001"], fetch=fetch)
    assert len(errors) == 1 and "S001" in errors[0] and "title" in errors[0]


def test_online_doi_match_wins_over_a_reworded_title():
    fetch, _ = _stub_fetch("A completely reworded title", "", doi="10.1/X")
    errors, _ = ck.check_online(GOOD, ["S001"], fetch=fetch)
    assert errors == []


def test_online_doi_mismatch_is_an_error_even_if_title_matches():
    fetch, _ = _stub_fetch("Slow lifting doubles widget life: a randomised trial", "", doi="10.9/y")
    errors, _ = ck.check_online(GOOD, ["S001"], fetch=fetch)
    assert len(errors) == 1 and "10.9/y" in errors[0] and "10.1/x" in errors[0]


def test_online_skips_sources_without_pmid_and_flags_unknown_ids():
    fetch, calls = _stub_fetch("unused", "")
    errors, warnings = ck.check_online(GOOD, ["S002", "S404"], fetch=fetch)
    assert calls == []
    assert any("S404" in e for e in errors)
    assert any("S002" in w and "no PubMed" in w for w in warnings)


def test_main_online_uses_injected_fetch(capsys):
    fetch, calls = _stub_fetch("Slow lifting doubles widget life: a randomised trial", "2.0 0.45")
    rc = ck.main(["--knowledge-dir", str(GOOD), "--online", "--ids", "S001"], fetch=fetch)
    assert rc == 0
    assert len(calls) == 2
    fetch, _ = _stub_fetch("Unrelated paper about sleep and caffeine intake in adults", "")
    rc = ck.main(["--knowledge-dir", str(GOOD), "--online", "--ids", "S001"], fetch=fetch)
    assert rc == 1


def test_titles_match_tolerates_abbreviations_but_not_other_papers():
    pubmed = (
        "American College of Sports Medicine position stand. Quantity and quality of exercise "
        "for developing and maintaining cardiorespiratory, musculoskeletal, and neuromotor "
        "fitness in apparently healthy adults: guidance for prescribing exercise."
    )
    citation = (
        "Garber CE et al., 2011. ACSM position stand: Quantity and quality of exercise for "
        "developing and maintaining cardiorespiratory, musculoskeletal, and neuromotor fitness "
        "in apparently healthy adults. Med Sci Sports Exerc"
    )
    assert ck.titles_match(pubmed, citation)
    # S108: the citation abbreviates "Randomized Controlled Trials" to "RCTs".
    assert ck.titles_match(
        "Effects of Resistance Training on Lower-Extremity Muscle Power in Middle-Aged and Older "
        "Adults: A Systematic Review and Meta-Analysis of Randomized Controlled Trials.",
        "Straight CR et al., 2016, Effects of Resistance Training on Lower-Extremity Muscle Power "
        "in Middle-Aged and Older Adults: A Systematic Review and Meta-Analysis of RCTs, Sports",
    )
    assert not ck.titles_match("Sleep and recovery in athletes.", citation)
    assert not ck.titles_match("", citation)


def test_titles_match_long_title_with_dropped_tail():
    pubmed = (
        "Glucose management for exercise using continuous glucose monitoring (CGM) systems in "
        "type 1 diabetes: position statement of the European Association for the Study of "
        "Diabetes (EASD) and of the International Society for Pediatric and Adolescent Diabetes "
        "(ISPAD) endorsed by JDRF and supported by the American Diabetes Association (ADA)."
    )
    citation = (
        "Moser O et al. Glucose management for exercise using continuous glucose monitoring "
        "(CGM) systems in type 1 diabetes: position statement of the EASD and ISPAD. 2020"
    )
    assert ck.titles_match(pubmed, citation)


def test_titles_match_rejects_shared_boilerplate_and_short_titles():
    citation = "Smith A, 2020, Caffeine and sleep quality: a systematic review and meta-analysis"
    assert not ck.titles_match(
        "Creatine supplementation: a systematic review and meta-analysis.", citation
    )
    # Real near-collision in sources.md (S604 vs S605's citation).
    assert not ck.titles_match(
        "Resistance Training Induces Improvements in Range of Motion: A Systematic Review and "
        "Meta-Analysis.",
        "Afonso J et al., 2021, Strength Training versus Stretching for Improving Range of "
        "Motion: A Systematic Review and Meta-Analysis, Healthcare (Basel)",
    )
    assert not ck.titles_match("Erratum.", "X, 2020. Erratum to: widgets. J Widgets")


def test_a_reference_to_a_missing_heading_fails():
    errors = ck.check_references(BAD)
    assert len(errors) == 1
    assert "No such rule" in errors[0] and "gadgets.md" in errors[0]
    assert ck.check_references(GOOD) == []


def test_a_supports_quote_over_500_characters_fails():
    errors = ck.check_quote_length(FIXTURES / "long_quote")
    assert len(errors) == 1
    assert "S001" in errors[0] and "500" in errors[0]
    assert ck.check_quote_length(GOOD) == []


def test_a_reference_may_name_a_section_heading(tmp_path):
    (tmp_path / "a.md").write_text(
        '## Bone health\n\n### A rule\n(see "Bone health") and see "Nothing here".\n',
        encoding="utf-8",
    )
    errors = ck.check_references(tmp_path)
    assert len(errors) == 1 and "Nothing here" in errors[0]


def test_supports_quote_length_boundary_is_500_characters(tmp_path):
    def errors_for(total: int) -> list[str]:
        line = "Supports: " + "x" * (total - len("Supports: "))
        (tmp_path / "sources.md").write_text(
            f"## List\n\n### S001\nDoe J, 2020. T. J\nURL: <https://example.org/a>\n{line}\n",
            encoding="utf-8",
        )
        return ck.check_quote_length(tmp_path)

    assert errors_for(500) == []
    assert len(errors_for(501)) == 1


def test_a_reference_target_must_be_a_level_2_or_3_heading(tmp_path):
    (tmp_path / "a.md").write_text(
        "# Top\n\n## Section\n\n### Rule\n\n#### Deep\n\n"
        '(see "Rule") (see "Section") (see "Top") (see "Deep")\n',
        encoding="utf-8",
    )
    errors = ck.check_references(tmp_path)
    assert len(errors) == 2
    assert any('"Top"' in e for e in errors) and any('"Deep"' in e for e in errors)


def _target(error: str) -> str:
    return error.split(": see ", 1)[1].removesuffix(" names no heading").strip('"')


def test_unquoted_and_capitalised_references_are_checked():
    errors = ck.check_references(FIXTURES / "unquoted_see")
    targets = sorted(_target(e) for e in errors)
    assert targets == ["Gone", "Missing Heading", "Nowhere", "Real"]


def test_reference_gaps_are_caught():
    errors = ck.check_references(FIXTURES / "see_gaps")
    targets = sorted(_target(e) for e in errors)
    assert targets == [
        "Activity multipliers (XYZ)",
        "Capitalised Nowhere Target",
        "Missing after comma",
        "Missing after semicolon",
        "real",
        "real heading",
    ]


def test_valid_and_prose_references_pass():
    # Covers quoted `See also "X"`, parenthesised headings, and prose that is not a reference.
    assert ck.check_references(FIXTURES / "see_ok") == []


def test_reference_scan_details_are_exact(tmp_path):
    (tmp_path / "a.md").write_text(
        "## Section\n\n### Real heading\n\n### Activity multipliers (PAL)\n\n"
        "Prose (see Table 2) (see S012) (see Real heading for details) (see Below).\n"
        'We foresee "x" and (see Activity multipliers (PAL)) and see "Activity multipliers (PAL)"\n'
        '```\n(see Fenced Fake Reference) see "fenced"\n```\n'
        "A wrapped (see Real\nheading) reference is checked and passes.\n"
        '(see Gone Missing) twice (see Gone Missing) and see "Quoted gone".\n',
        encoding="utf-8",
    )
    (tmp_path / "b.md").write_text("### Other\n\n(see real heading for more)\n", encoding="utf-8")
    errors = ck.check_references(tmp_path)
    assert errors == [
        f'{tmp_path / "a.md"}:14: see "Quoted gone" names no heading',
        f"{tmp_path / 'a.md'}:14: see Gone Missing names no heading",
        f"{tmp_path / 'a.md'}:14: see Gone Missing names no heading",
        f"{tmp_path / 'b.md'}:3: see real heading for more names no heading",
    ]


def test_wrapped_references_and_heading_boundaries(tmp_path):
    (tmp_path / "a.md").write_text(
        "### Protein\n\n### Protein intake\n\n### Protein targets\n\n### Alpha\n\n"
        "Fine (see Protein\n  targets) and (see Protein intake targets) and (see Alpha for more)\n"
        "(see Protein intakes) (see above) (see ABOVE)\n"
        "(see Protein\n  tragets) and (see Protein for athletes).\n\n"
        "(see Table 2) (see Figure 3) (see Below)\n",
        encoding="utf-8",
    )
    errors = ck.check_references(tmp_path)
    assert [(e.split(":")[-2], _target(e)) for e in errors] == [
        ("11", "Protein intakes"),
        ("12", "Protein tragets"),
        ("13", "Protein for athletes"),
    ]


# Beta p5-elena-I7: a strong rule's numbers must appear in a cited Supports line.
def test_rule_numbers_on_the_good_fixture():
    assert ck.check_rule_numbers(GOOD) == []


def _copy_good(tmp_path, old, new):
    for path in GOOD.glob("*.md"):
        (tmp_path / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    rules = tmp_path / "widgets.md"
    rules.write_text(rules.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
    return tmp_path


def test_rule_numbers_flags_a_number_no_source_states(tmp_path):
    kdir = _copy_good(tmp_path, "below 60% humidity.", "below 70% humidity.")
    assert ck.check_rule_numbers(kdir) == [
        'widgets.md: "Store widgets dry" (strong): 70 is in no cited Supports line'
    ]


def test_rule_numbers_skips_a_labelled_convention(tmp_path):
    kdir = _copy_good(tmp_path, "below 60% humidity.", "below 70% humidity (a convention).")
    assert ck.check_rule_numbers(kdir) == []


def test_main_claims_flag_prints_the_report(capsys, tmp_path):
    kdir = _copy_good(tmp_path, "below 60% humidity.", "below 70% humidity.")
    ck.main(["--knowledge-dir", str(kdir), "--claims"])
    assert "70 is in no cited Supports line" in capsys.readouterr().out


def test_numbers_keep_unit_suffixed_decimals_and_thousands():
    assert ck._numbers("1.6g/kg, 12.5kg, 1,500 kcal") == {"1.6", "12.5", "1500"}


def test_rule_numbers_reports_a_number_once_per_rule(tmp_path):
    kdir = _copy_good(tmp_path, "below 60% humidity.", "below 70% humidity. Never 70% or more.")
    assert len(ck.check_rule_numbers(kdir)) == 1


def test_rule_numbers_does_not_skip_conventional(tmp_path):
    kdir = _copy_good(tmp_path, "below 60% humidity.", "below 70% humidity, conventional.")
    assert len(ck.check_rule_numbers(kdir)) == 1
