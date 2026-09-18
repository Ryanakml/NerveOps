"""Shared helpers for M0-01 shell-contract tests."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APPS = ROOT / "apps"

SHELLS = ["web", "control-plane", "runtime-api", "runtime-worker", "celery-worker"]

# Domain terms that MUST NOT appear as implemented behavior (tables/routes/models).
# Mentions inside docs/tests/comments explaining non-goals are allowed; these tests
# therefore inspect code structure (routes, models, deps), not raw prose.
DOMAIN_TABLE_HINTS = [
    "__tablename__",
    "declarative_base",
    "CREATE TABLE",
    "schema.prisma",
    "alembic",
]
