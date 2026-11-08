"""`coach doctor`: the first-run checks, each with the command that fixes it."""

import builtins
import json

from coach import doctor
from coach.cli import main


def _by_name(report):
    return {c["check"]: c for c in report["checks"]}


def test_doctor_reports_every_check_with_a_fix(tmp_path):
    report = doctor.run(tmp_path)
    names = set(_by_name(report))
    assert {"python", "pdf_extra", "data_dir", "uv", "claude", "profile"} <= names
    assert all(c["ok"] or c["fix"] for c in report["checks"])


def test_missing_pdf_extra_says_how_to_install_it(tmp_path, monkeypatch):
    real_import = builtins.__import__

    def no_reportlab(name, *args, **kwargs):
        if name.startswith("reportlab"):
            raise ImportError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_reportlab)
    check = _by_name(doctor.run(tmp_path))["pdf_extra"]
    assert check["ok"] is False and "uv sync --extra pdf" in check["fix"]


def test_missing_claude_and_profile_are_reported(tmp_path, monkeypatch):
    monkeypatch.setattr(doctor.shutil, "which", lambda name: None)
    checks = _by_name(doctor.run(tmp_path))
    assert checks["claude"]["ok"] is False and checks["uv"]["ok"] is False
    assert checks["profile"]["ok"] is False and "/setup" in checks["profile"]["fix"]


def test_doctor_runs_from_the_cli_without_a_profile(capsys, tmp_path):
    code = main(["--data-dir", str(tmp_path), "doctor", "--json"])
    out = json.loads(capsys.readouterr().out)
    assert code == 0 and "checks" in out


def test_unusable_data_dir_is_reported_with_a_fix(tmp_path):
    not_a_folder = tmp_path / "data"
    not_a_folder.write_text("", encoding="utf-8")
    checks = _by_name(doctor.run(not_a_folder))
    assert checks["data_dir"]["ok"] is False and "COACH_DATA_DIR" in checks["data_dir"]["fix"]
    assert checks["profile"]["detail"] == "no profile yet"


def test_unreadable_profile_is_a_failed_check_not_an_error(capsys, tmp_path):
    (tmp_path / "profile.yaml").mkdir()
    code = main(["--data-dir", str(tmp_path), "doctor", "--json"])
    profile = _by_name(json.loads(capsys.readouterr().out))["profile"]
    assert code == 0 and profile["ok"] is False and "profile.yaml" in profile["fix"]


def test_broken_profile_fix_names_the_file_not_setup(tmp_path):
    (tmp_path / "profile.yaml").write_text("sex: [", encoding="utf-8")
    profile = _by_name(doctor.run(tmp_path))["profile"]
    assert profile["ok"] is False and "profile.yaml" in profile["fix"]


# Beta 3 p7-nuevo-N1: a readable list by default, JSON with --json, and ok:false explained.
def test_doctor_prints_a_readable_list_by_default(tmp_path, capsys):
    from coach.cli import main

    assert main(["--data-dir", str(tmp_path), "doctor"]) == 0
    out = capsys.readouterr().out
    assert not out.lstrip().startswith("{")
    assert "profile" in out and "/setup" in out
    assert "expected before /setup" in out


def test_doctor_json_stays_json(tmp_path, capsys):
    import json

    from coach.cli import main

    assert main(["--data-dir", str(tmp_path), "doctor", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["ok"] is False


def test_doctor_text_keeps_a_broken_profile_on_one_line_and_never_calls_it_expected(tmp_path):
    (tmp_path / "profile.yaml").write_text("sex: [\n", encoding="utf-8")
    out = doctor.text(doctor.run(tmp_path))
    line = next(x for x in out.splitlines() if "profile:" in x)
    assert "FIX" in line and "expected before /setup" not in out
