"""M0-01 runtime-api shell-operability tests (no domain behavior)."""

from fastapi.testclient import TestClient

from app.main import app

FORBIDDEN = [
    "workspace",
    "incident",
    "hypothesis",
    "evidence",
    "approval",
    "intent",
    "execution",
    "lease",
    "policy",
]

client = TestClient(app)


def test_health_shape_only_operability():
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["service"] == "runtime-api"
    assert isinstance(body["version"], str)
    assert isinstance(body["uptimeSeconds"], int)
    assert sorted(body.keys()) == ["service", "status", "uptimeSeconds", "version"]


def test_ready_adds_ready_flag_only():
    res = client.get("/ready")
    assert res.status_code == 200
    body = res.json()
    assert body["ready"] is True
    assert body["status"] == "ok"


def test_no_domain_fields_leak():
    raw = (client.get("/health").text + client.get("/ready").text).lower()
    for term in FORBIDDEN:
        assert term not in raw
