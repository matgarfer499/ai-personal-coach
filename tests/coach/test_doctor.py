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
