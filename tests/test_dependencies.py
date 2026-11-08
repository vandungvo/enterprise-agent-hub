"""pyproject.toml (installed by Vercel/uv) and requirements*.txt (pip, Docker, CI) must pin the same versions."""
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _requirements(name: str) -> set[str]:
    out = set()
    for line in (ROOT / name).read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line and not line.startswith("-r"):
            out.add(re.sub(r"\s+", "", line).lower())
    return out


def test_runtime_dependencies_match():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert {d.lower() for d in project["dependencies"]} == _requirements("requirements.txt")


def test_dev_dependencies_match():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert {d.lower() for d in project["optional-dependencies"]["dev"]} == _requirements("requirements-dev.txt")


def test_runtime_dependencies_are_pinned():
    assert all("==" in d for d in _requirements("requirements.txt"))
