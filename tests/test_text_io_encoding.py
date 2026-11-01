"""Text I/O must name its encoding: on Windows the default is cp1252, not UTF-8."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT_CALLS = {"open", "read_text", "write_text"}


def _is_binary(call: ast.Call) -> bool:
    args = [*call.args, *(k.value for k in call.keywords if k.arg == "mode")]
    return any(
        isinstance(a, ast.Constant) and isinstance(a.value, str) and "b" in a.value for a in args
    )


def _offenders() -> list[str]:
    found = []
    for folder in ("coach", "scripts", "tests"):
        for path in sorted((ROOT / folder).rglob("*.py")):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if not isinstance(node, ast.Call):
                    continue
                f = node.func
                name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
                if name not in TEXT_CALLS or _is_binary(node):
                    continue
                if not any(k.arg == "encoding" for k in node.keywords):
                    found.append(f"{path.relative_to(ROOT)}:{node.lineno} {name}")
    return found


def test_text_io_names_its_encoding():
    assert _offenders() == []
