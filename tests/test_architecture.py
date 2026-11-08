"""Layering rules for app/ (checked on every CI run, including imports inside functions).

    core  <-  models, access, hris, llm, rag  <-  tools, agents  <-  api  <-  bootstrap, main
"""
import ast
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parent.parent / "app"

# package -> app packages it must never import
FORBIDDEN = {
    "app.core": {"app.models", "app.access", "app.hris", "app.llm", "app.rag", "app.tools", "app.agents",
                 "app.api", "app.bootstrap", "app.main"},
    "app.models": {"app.access", "app.llm", "app.rag", "app.tools", "app.agents", "app.api", "app.bootstrap"},
    "app.hris": {"app.access", "app.llm", "app.tools", "app.agents", "app.api", "app.bootstrap", "app.main"},
    "app.access": {"app.llm", "app.tools", "app.agents", "app.api", "app.bootstrap", "app.main"},
    "app.llm": {"app.models", "app.access", "app.hris", "app.rag", "app.tools", "app.agents", "app.api",
                "app.bootstrap", "app.main"},
    "app.rag": {"app.access", "app.llm", "app.tools", "app.agents", "app.api", "app.bootstrap", "app.main"},
    "app.tools": {"app.agents.runtime", "app.agents.conversation", "app.api", "app.bootstrap", "app.main"},
    "app.agents": {"app.api", "app.bootstrap", "app.main"},
    "app.api": {"app.main"},
}


def _module_name(path: Path) -> str:
    rel = path.relative_to(APP.parent).with_suffix("")
    parts = list(rel.parts)
    return ".".join(parts[:-1] if parts[-1] == "__init__" else parts)


def _imports(path: Path) -> set[str]:
    out = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            out.add(node.module)
            out.update(f"{node.module}.{a.name}" for a in node.names)  # `from app import hris`
        elif isinstance(node, ast.Import):
            out.update(a.name for a in node.names)
    return {m for m in out if m == "app" or m.startswith("app.")}


def _violates(imported: str, forbidden: set[str]) -> bool:
    return any(imported == f or imported.startswith(f + ".") for f in forbidden)


MODULES = sorted(p for p in APP.rglob("*.py") if "__pycache__" not in p.parts)


@pytest.mark.parametrize("path", MODULES, ids=lambda p: _module_name(p))
def test_layering(path: Path):
    module = _module_name(path)
    rules = [f for pkg, f in FORBIDDEN.items() if module == pkg or module.startswith(pkg + ".")]
    bad = sorted(i for i in _imports(path) for f in rules if _violates(i, f))
    assert not bad, f"{module} must not import {bad}"


def test_no_relative_imports():
    offenders = [str(p.relative_to(APP.parent)) for p in MODULES
                 if any(isinstance(n, ast.ImportFrom) and n.level > 0
                        for n in ast.walk(ast.parse(p.read_text(encoding="utf-8"))))]
    assert not offenders, f"use absolute imports (from app.x import y): {offenders}"
