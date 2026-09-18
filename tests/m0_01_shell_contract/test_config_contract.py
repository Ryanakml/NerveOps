"""Acceptance: shared configuration names are documented without committed secrets."""

import re
from pathlib import Path

from .conftest import APPS, ROOT

SECRET_VALUE_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{8,}"),
    re.compile(r"ghp_[A-Za-z0-9]{8,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"BEGIN [A-Z ]*PRIVATE KEY"),
]


def _env_example_names():
    names = set()
    for line in (ROOT / ".env.example").read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            names.add(line.split("=", 1)[0].strip())
    # Ignore commented placeholders like `# FOO=...`.
    return {n for n in names if n and re.fullmatch(r"[A-Z0-9_]+", n)}


def test_env_example_names_are_documented():
    documented = (ROOT / "docs" / "config-contract.md").read_text()
    for name in _env_example_names():
        assert name in documented, f"{name} from .env.example is not documented in docs/config-contract.md"


def test_no_secret_values_committed():
    skip_dirs = {"node_modules", "dist", ".next", "__pycache__", ".git"}
    candidates = []
    for path in ROOT.rglob("*"):
        if any(part in skip_dirs for part in path.parts):
            continue
        if "non-published-docs" in path.parts:
            continue
        if path.is_file() and path.suffix in {".ts", ".tsx", ".js", ".mjs", ".cjs", ".py", ".json", ".example", ".md"}:
            candidates.append(path)
    # Also scan .env.example itself: it must contain names, not secret values.
    candidates.append(ROOT / ".env.example")
    for path in candidates:
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        for pattern in SECRET_VALUE_PATTERNS:
            assert not pattern.search(text), f"{path} appears to contain a committed secret"
    env_text = (ROOT / ".env.example").read_text()
    # .env.example must not set real-looking secrets for token/key names.
    for line in env_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, _, value = stripped.partition("=")
        if any(token in key for token in ("TOKEN", "SECRET", "PRIVATE_KEY")):
            assert value.strip() == "", f".env.example must leave {key} unset (names only)"


def test_no_env_file_committed():
    assert not (ROOT / ".env").exists(), ".env must never be committed (names only in .env.example)"
    assert (ROOT / ".gitignore").read_text().count(".env") >= 1
