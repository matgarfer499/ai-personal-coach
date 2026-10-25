"""Branch, check and commit mechanics for the /research skill.

A research run happens on its own branch, `research/<YYYY-MM-DD>-<slug>`, in a separate git
worktree, so the main checkout is never switched. The branch starts from the default branch when
that branch has the knowledge checks, else from the current branch (a default branch that
predates scripts/check_knowledge.py). `finish` commits only after the checks pass, pushes only
a `research/` branch, and never merges.

Usage (from the repo root):
  uv run python scripts/research.py start "TOPIC" --worktree-root DIR [--today YYYY-MM-DD]
  uv run python scripts/research.py next-id [--knowledge-dir DIR/knowledge]
  uv run python scripts/research.py check --worktree DIR [--ids S820,S821]
  uv run python scripts/research.py finish --worktree DIR --message MSG [--ids ...] [--no-push]
  uv run python scripts/research.py discard --worktree DIR
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

from build_knowledge_index import readme_with_counts

from coach.text import fold

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BRANCH = "main"
CHECKS_SCRIPT = "scripts/check_knowledge.py"
BRANCH_PREFIX = "research/"
SLUG_MAX = 40  # convention: keeps branch names readable
LOG_DIR = "docs/research-log"
# The only paths a research run may change (the skill's "Writes"); coach/ and docs/safety.md never.
# Directories match by prefix, files exactly. README.md may change only in its counts line, which
# the index build rewrites.
ALLOWED_DIRS = ("knowledge/", f"{LOG_DIR}/")
ALLOWED_FILES = {"docs/dropped-claims.md"}
README = "README.md"
LOG_SECTIONS = [
    "Topic",
    "What was searched",
    "New rules",
    "Changed rules",
    "Retired rules",
    "Dropped claims",
    "Check output",
]
PLACEHOLDER = "(to fill)"
BASE_KEY = "researchBase"
SOURCE_ID_RE = re.compile(r"^### S(\d+)$", re.M)


class ChecksFailed(Exception):
    pass


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout.strip()


def slugify(topic: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", fold(topic)).strip("-")
    return slug[:SLUG_MAX].rstrip("-") or "topic"


def branch_name(today: date, topic: str) -> str:
    return f"{BRANCH_PREFIX}{today.isoformat()}-{slugify(topic)}"


def choose_base(repo: Path, default: str = DEFAULT_BRANCH) -> str:
    try:
        git(repo, "cat-file", "-e", f"{default}:{CHECKS_SCRIPT}")
    except RuntimeError:
        return "HEAD"
    return default


def log_template(topic: str, today: date) -> str:
    sections = "\n\n".join(f"## {s}\n\n{PLACEHOLDER}" for s in LOG_SECTIONS[1:])
    header = f"# Research log: {topic}\n\nDate: {today.isoformat()}\n\n## Topic\n\n{topic}"
    return f"{header}\n\n{sections}\n"


def log_path(branch: str) -> Path:
    return Path(LOG_DIR) / f"{branch.removeprefix(BRANCH_PREFIX)}.md"


def start(repo: Path, topic: str, today: date, worktree_root: Path) -> dict:
    if Path(worktree_root).resolve().is_relative_to(Path(repo).resolve()):
        raise ValueError("the worktree root must be outside the repo, or the checkout gets dirty")
    branch = branch_name(today, topic)
    base = choose_base(repo)
    worktree = Path(worktree_root) / branch.removeprefix(BRANCH_PREFIX)
    base_commit = git(repo, "rev-parse", base)
    git(repo, "worktree", "add", "-q", "-b", branch, str(worktree), base_commit)
    # finish checks everything the branch changed since here, not just the last commit.
    git(repo, "config", f"branch.{branch}.{BASE_KEY}", base_commit)
    log = log_path(branch)
    log_file = worktree / log
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text(log_template(topic, today), encoding="utf-8")
    return {"branch": branch, "base": base, "worktree": str(worktree), "log": str(log)}


def next_id(knowledge_dir: Path) -> str:
    text = (Path(knowledge_dir) / "sources.md").read_text(encoding="utf-8")
    return f"S{max(int(n) for n in SOURCE_ID_RE.findall(text)) + 1:03d}"


def _run_script(worktree: Path, *args: str) -> subprocess.CompletedProcess:
    paths = os.pathsep.join([str(worktree), str(worktree / "scripts")])
    env = os.environ | {"PYTHONPATH": paths, "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run(
        [sys.executable, *args], cwd=worktree, env=env, capture_output=True, text=True
    )


def branch_base(worktree: Path) -> str:
    """The commit `start` branched from, recorded in the repo's git config."""
    branch = git(worktree, "branch", "--show-current")
    try:
        return git(worktree, "config", "--get", f"branch.{branch}.{BASE_KEY}")
    except RuntimeError:
        raise ValueError(
            f"no recorded base for {branch}; set it with "
            f"git config branch.{branch}.{BASE_KEY} <commit it started from>"
        ) from None


def new_source_ids(worktree: Path) -> list[str]:
    """Source IDs in the worktree's sources.md that the branch's base does not have."""
    now = (Path(worktree) / "knowledge" / "sources.md").read_text(encoding="utf-8")
    before = git(worktree, "show", f"{branch_base(worktree)}:knowledge/sources.md")
    return sorted(
        f"S{n}" for n in set(SOURCE_ID_RE.findall(now)) - set(SOURCE_ID_RE.findall(before))
    )


def _names(worktree: Path, *args: str) -> set[str]:
    return set(git(worktree, *args).splitlines())


def changed_paths(worktree: Path, since: str) -> list[str]:
    """Every path that differs from `since`: committed, staged, unstaged or untracked. Renames
    count as both their old and new path."""
    return sorted(
        _names(worktree, "diff", "--name-only", "--no-renames", since)
        | _names(worktree, "diff", "--name-only", "--no-renames", "--cached", since)
        | _names(worktree, "ls-files", "--others", "--exclude-standard")
    )


def run_checks(worktree: Path, ids: list[str], online: bool = True) -> tuple[bool, str]:
    """Rebuild the index, run the knowledge checks (online for new source IDs), then the repo's
    own checks, ruff and pytest, as before any commit."""
    kdir = str(Path(worktree) / "knowledge")
    build = _run_script(worktree, "scripts/build_knowledge_index.py", "--knowledge-dir", kdir)
    if build.returncode != 0:
        return False, build.stdout + build.stderr
    command = [CHECKS_SCRIPT, "--knowledge-dir", kdir]
    if ids and online:
        command += ["--online", "--ids", ",".join(ids)]
    steps = [_run_script(worktree, *command)]
    if (Path(worktree) / "pyproject.toml").exists():
        steps += [
            _run_script(worktree, "-m", "ruff", "check", "."),
            _run_script(worktree, "-m", "pytest", "-q", "-p", "no:cacheprovider"),
        ]
    output = "\n".join((s.stdout + s.stderr).strip() for s in steps)
    return all(s.returncode == 0 for s in steps), output


def _outside_scope(worktree: Path) -> list[str]:
    base = branch_base(worktree)
    paths = changed_paths(worktree, base)
    allowed = [p for p in paths if p in ALLOWED_FILES or p.startswith(ALLOWED_DIRS)]
    if README in paths and _only_counts_changed(worktree, base):
        allowed.append(README)
    return [p for p in paths if p not in allowed]


def _only_counts_changed(worktree: Path, base: str) -> bool:
    """README.md differs from the branch base only by an up-to-date counts line."""
    try:
        before = git(worktree, "show", f"{base}:{README}")
    except RuntimeError:
        return False  # a research run never creates the README
    now = (Path(worktree) / README).read_text(encoding="utf-8")
    expected = readme_with_counts(before + "\n", Path(worktree) / "knowledge")
    return expected is not None and expected.rstrip("\n") == now.rstrip("\n")


def finish(
    worktree: Path,
    message: str,
    push: bool,
    ids: list[str] | None = None,
    online: bool = True,
) -> dict:
    """Commit the run after every check passes. `online=False` is for tests only (no network)."""
    branch = git(worktree, "branch", "--show-current")
    if not branch.startswith(BRANCH_PREFIX):
        raise ValueError(f"finish only commits on a research/ branch, not {branch!r}")
    outside = _outside_scope(worktree)
    if outside:
        raise ValueError(f"a research run may not change {', '.join(outside)}")
    log = log_path(branch)
    log_file = Path(worktree) / log
    if not log_file.exists() or PLACEHOLDER in log_file.read_text(encoding="utf-8"):
        raise ValueError(f"research log missing or not filled in: {log}")
    ids = sorted(set(ids or []) | set(new_source_ids(worktree)))
    ok, output = run_checks(worktree, ids, online=online)
    if not ok:
        raise ChecksFailed(output)
    outside = _outside_scope(worktree)  # the checks must not have written anywhere else
    if outside:
        raise ValueError(f"the checks changed {', '.join(outside)}")
    to_commit = changed_paths(worktree, "HEAD")
    if not to_commit:  # an empty pathspec would make `git add -A --` stage the whole tree
        raise ValueError("nothing to commit")
    git(worktree, "add", "-A", "--", *to_commit)
    git(worktree, "commit", "-q", "-m", message)
    if push:
        git(worktree, "push", "-q", "-u", "origin", branch)
    return {
        "branch": branch,
        "commit": git(worktree, "rev-parse", "HEAD"),
        "pushed": push,
        "checks": output.strip(),
    }


def discard(repo: Path, worktree: Path) -> None:
    """Remove a local run (worktree and local branch). Never touches the remote."""
    branch = git(worktree, "branch", "--show-current")
    if not branch.startswith(BRANCH_PREFIX):
        raise ValueError(f"discard only removes research/ branches, not {branch!r}")
    git(repo, "worktree", "remove", "--force", str(worktree))
    git(repo, "branch", "-D", branch)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    start_cmd = sub.add_parser("start")
    start_cmd.add_argument("topic")
    start_cmd.add_argument("--worktree-root", type=Path, required=True)
    start_cmd.add_argument("--today", type=date.fromisoformat, default=None)
    next_cmd = sub.add_parser("next-id")
    next_cmd.add_argument("--knowledge-dir", type=Path, default=ROOT / "knowledge")
    check_cmd = sub.add_parser("check")
    check_cmd.add_argument("--worktree", type=Path, required=True)
    check_cmd.add_argument("--ids", default="")
    finish_cmd = sub.add_parser("finish")
    finish_cmd.add_argument("--worktree", type=Path, required=True)
    finish_cmd.add_argument("--message", required=True)
    finish_cmd.add_argument("--ids", default="")
    finish_cmd.add_argument("--no-push", action="store_true")
    discard_cmd = sub.add_parser("discard")
    discard_cmd.add_argument("--worktree", type=Path, required=True)
    args = parser.parse_args(argv)
    ids = [i.strip() for i in getattr(args, "ids", "").split(",") if i.strip()]

    try:
        if args.command == "start":
            result = start(ROOT, args.topic, args.today or date.today(), args.worktree_root)
        elif args.command == "next-id":
            result = {"next_id": next_id(args.knowledge_dir)}
        elif args.command == "check":
            ok, output = run_checks(args.worktree, ids)
            result = {"ok": ok, "output": output.strip()}
        elif args.command == "finish":
            result = finish(args.worktree, args.message, push=not args.no_push, ids=ids)
        else:
            discard(ROOT, args.worktree)
            result = {"discarded": str(args.worktree)}
    except (ChecksFailed, RuntimeError, ValueError) as err:
        print(json.dumps({"error": type(err).__name__, "message": str(err)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())
