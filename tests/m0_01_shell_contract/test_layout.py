"""Acceptance: five shells are identifiable from layout with runnable entrypoints."""

import json
from pathlib import Path

from .conftest import APPS, ROOT, SHELLS


def test_five_shell_directories_exist():
    for shell in SHELLS:
        assert (APPS / shell).is_dir(), f"missing shell directory: apps/{shell}"


def test_each_shell_has_readme_and_dockerfile():
    for shell in SHELLS:
        assert (APPS / shell / "README.md").is_file(), f"apps/{shell}/README.md missing"
        assert (APPS / shell / "Dockerfile").is_file(), f"apps/{shell}/Dockerfile missing"


def test_js_shells_have_build_start_scripts():
    for shell in ("web", "control-plane"):
        pkg = json.loads((APPS / shell / "package.json").read_text())
        scripts = pkg.get("scripts", {})
        for verb in ("build", "start", "lint", "type-check", "test", "integration-test"):
            assert verb in scripts, f"apps/{shell}/package.json missing script: {verb}"
        assert pkg["name"].startswith("@nerveops/")


def test_python_shells_have_requirements_and_makefile_targets():
    for shell in ("runtime-api", "runtime-worker", "celery-worker"):
        assert (APPS / shell / "requirements.txt").is_file()
        makefile = (APPS / shell / "Makefile").read_text()
        for verb in ("build:", "start:", "lint:", "type-check:", "test:", "integration-test:"):
            assert verb in makefile, f"apps/{shell}/Makefile missing target: {verb}"


def test_python_shell_entrypoints_exist():
    assert (APPS / "runtime-api" / "app" / "main.py").is_file()
    assert (APPS / "runtime-worker" / "worker" / "main.py").is_file()
    assert (APPS / "celery-worker" / "app" / "celery_app.py").is_file()
    assert (APPS / "celery-worker" / "app" / "check.py").is_file()


def test_docs_cover_layout_commands_config():
    for doc in ("repo-layout.md", "local-shells.md", "config-contract.md", "commands.md"):
        assert (ROOT / "docs" / doc).is_file(), f"docs/{doc} missing"
    assert (ROOT / ".env.example").is_file()
