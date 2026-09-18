"""Acceptance: repository-level command conventions and wiring (stable interfaces)."""

import json
from pathlib import Path

from .conftest import ROOT

REQUIRED_ROOT_SCRIPTS = ["lint", "type-check", "test", "integration-test", "build"]


def test_root_package_json_wiring():
    pkg = json.loads((ROOT / "package.json").read_text())
    scripts = pkg.get("scripts", {})
    for verb in REQUIRED_ROOT_SCRIPTS:
        assert verb in scripts, f"root package.json missing script: {verb}"
    # Wiring must delegate to shells, not hide behavior.
    assert "workspace" in scripts["build"] or "apps" in scripts["build"]
    assert "pytest" in scripts["test"]
    assert "integration-shell-check" in scripts["integration-test"]


def test_root_workspaces_cover_js_shells():
    pkg = json.loads((ROOT / "package.json").read_text())
    workspaces = pkg.get("workspaces", [])
    assert "apps/web" in workspaces
    assert "apps/control-plane" in workspaces


def test_scripts_exist_and_are_executable_shape():
    for name in ("check-shell-http.sh", "check-python-shells.py", "integration-shell-check.sh"):
        p = ROOT / "scripts" / name
        assert p.is_file(), f"scripts/{name} missing"
        text = p.read_text()
        assert len(text.strip()) > 20


def test_eslint_wiring_present():
    assert (ROOT / "eslint.config.mjs").is_file()
