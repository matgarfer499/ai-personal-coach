"""Text I/O must name its encoding: on Windows the default is cp1252, not UTF-8."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT_CALLS = {"open", "read_text", "write_text"}


def _is_binary(call: ast.Call) -> bool:
    """Mode: `mode=`, else args[1] for open(), args[0] for .open()."""
    mode = next((k.value for k in call.keywords if k.arg == "mode"), None)
    if mode is None and isinstance(call.func, ast.Name) and len(call.args) > 1:
        mode = call.args[1]
    elif (
        mode is None
        and isinstance(call.func, ast.Attribute)
        and call.func.attr == "open"
        and call.args
    ):
        mode = call.args[0]
    return isinstance(mode, ast.Constant) and isinstance(mode.value, str) and "b" in mode.value


def _calls_without_encoding(tree: ast.AST) -> list[tuple[int, str]]:
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
        if name in TEXT_CALLS and not _is_binary(node):
            if not any(k.arg == "encoding" for k in node.keywords):
                out.append((node.lineno, name))
    return out


def _offenders() -> list[str]:
    found = []
    for folder in ("coach", "scripts", "tests"):
        for path in sorted((ROOT / folder).rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            found += [f"{path.relative_to(ROOT)}:{n} {c}" for n, c in _calls_without_encoding(tree)]
    return found


def test_text_io_names_its_encoding():
    assert _offenders() == []


def test_checker_flags_and_exempts_the_right_calls():
    def flagged(src: str) -> int:
        return len(_calls_without_encoding(ast.parse(src)))

    assert flagged('p.write_text("abc")') == 1  # "b" in the data is not a binary mode
    assert flagged("p.read_text()") == 1
    assert flagged('open(p, "w")') == 1
    assert flagged('p.open("r")') == 1
    assert flagged('open(p, "rb")') == 0
    assert flagged('p.open("wb")') == 0
    assert flagged('open(p, mode="wb")') == 0
    assert flagged('p.write_text("abc", encoding="utf-8")') == 0
