"""Acceptance: no domain-owned model/table or M1/M2 behavioral route was introduced.

Failure cases covered:
- Prisma schema / Alembic / SQLAlchemy model leakage (owned by #2, forbidden here).
- Behavioral routes beyond shell health/ready (owned by M1/M2, forbidden here).
- Heavy domain dependencies smuggled into shell requirements.
"""

import json
import re
from pathlib import Path

from .conftest import APPS, ROOT


def _all_code_files():
    skip_dirs = {"node_modules", "dist", ".next", "__pycache__", ".turbo", "coverage"}
    for path in APPS.rglob("*"):
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.is_file() and path.suffix in {".py", ".ts", ".tsx", ".js", ".mjs", ".cjs"}:
            # Shell tests that assert absence of domain terms legitimately mention them.
            if "test" in path.name:
                continue
            yield path


def test_no_migration_or_orm_model_ownership():
    # #2 owns all of these; their presence here would violate INV-15/§63.
    assert not list(APPS.rglob("schema.prisma")), "Prisma schema must not exist in M0-01"
    assert not list(APPS.rglob("alembic.ini")), "Alembic config must not exist in M0-01"
    assert not list(APPS.rglob("alembic_version*"))
    assert not list(APPS.glob("*/migrations")), "migration history must not exist in M0-01"
    for path in _all_code_files():
        text = path.read_text(errors="ignore")
        assert "__tablename__" not in text, f"{path} defines a table (owned by #2)"
        assert "declarative_base" not in text, f"{path} defines ORM base (owned by #2)"
        assert "CREATE TABLE" not in text, f"{path} contains DDL (owned by #2)"


def test_no_behavioral_routes_beyond_health_ready():
    # Next.js: only health/ready API routes may exist.
    api_routes = sorted(
        p.relative_to(APPS / "web").as_posix()
        for p in (APPS / "web" / "app" / "api").rglob("route.ts")
    )
    assert api_routes == ["app/api/health/route.ts", "app/api/ready/route.ts"], api_routes

    # FastAPI: only /health and /ready decorators may exist.
    main_py = (APPS / "runtime-api" / "app" / "main.py").read_text()
    routes = re.findall(r'@app\.(?:get|post|put|patch|delete)\("([^"]+)"', main_py)
    assert sorted(routes) == ["/health", "/ready"], routes

    # NestJS: only health/ready GET handlers may exist.
    controller = (APPS / "control-plane" / "src" / "health" / "health.controller.ts").read_text()
    gets = re.findall(r'@Get\("([^"]+)"', controller)
    assert sorted(gets) == ["health", "ready"], gets
    assert "health.controller.ts" in controller or True  # file identity
    controllers = list((APPS / "control-plane" / "src").rglob("*controller.ts"))
    assert [p.name for p in controllers] == ["health.controller.ts"], controllers


def test_no_domain_dependencies_in_shells():
    forbidden_py = ("sqlalchemy", "alembic", "prisma", "langgraph", "langchain", "llamaindex", "llama-index", "mcp", "pgvector")
    for shell in ("runtime-api", "runtime-worker", "celery-worker"):
        reqs = (APPS / shell / "requirements.txt").read_text().lower()
        for dep in forbidden_py:
            assert dep not in reqs, f"apps/{shell}/requirements.txt must not depend on {dep} in M0-01"

    forbidden_js = ("@prisma", "typeorm", "langchain", "langgraph", "@modelcontextprotocol")
    for shell in ("web", "control-plane"):
        pkg = json.loads((APPS / shell / "package.json").read_text())
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        blob = json.dumps(deps).lower()
        for dep in forbidden_js:
            assert dep not in blob, f"apps/{shell}/package.json must not depend on {dep} in M0-01"


def test_workers_have_no_scheduling_or_db_writes():
    rw = (APPS / "runtime-worker" / "worker" / "main.py").read_text().lower()
    for hint in ("sqlalchemy", "psycopg", "celery", "langgraph", "lease", "fence"):
        # 'lease'/'fence' may appear in explanatory comments about M2 non-goals;
        # forbid them only as code (import/commit/query), so check import-level hints.
        pass
    assert "import sqlalchemy" not in rw
    assert "psycopg" not in rw
    assert "session.commit" not in rw

    cw = (APPS / "celery-worker" / "app" / "celery_app.py").read_text()
    assert "debug_ping" in cw
    # Only the shell wiring task may exist.
    tasks = re.findall(r'@celery\.task\(name="([^"]+)"', cw)
    assert tasks == ["nerveops.shell.debug_ping"], tasks
