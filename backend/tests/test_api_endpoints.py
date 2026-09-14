import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["agent_sdk"] == "AWS Strands Agents SDK"

def test_get_stats(client):
    res = client.get("/api/stats")
    assert res.status_code == 200
    stats = res.json()
    assert "total_rescued_lbs" in stats
    assert "meals_provided" in stats

def test_get_volunteers(client):
    res = client.get("/api/volunteers")
    assert res.status_code == 200
    vols = res.json()
    assert len(vols) >= 5

def test_simulate_alert_and_approve(client):
    # Trigger simulated alert
    res_sim = client.post("/api/donations/simulate")
    assert res_sim.status_code == 200
    proposal = res_sim.json()
    assert "id" in proposal
    assert proposal["status"] == "PROPOSED"
    prop_id = proposal["id"]

    # Check pending decisions
    res_pending = client.get("/api/decisions/pending")
    assert res_pending.status_code == 200
    pending = res_pending.json()
    assert any(p["id"] == prop_id for p in pending)

    # Approve decision
    res_approve = client.post(
        f"/api/decisions/{prop_id}/approve",
        json={"approved_by": "Coordinator Sarah L."}
    )
    assert res_approve.status_code == 200
    dispatch = res_approve.json()
    assert dispatch["status"] == "APPROVED"
    assert "pickup_verification_code" in dispatch

    # Check traces
    res_traces = client.get("/api/agent/traces")
    assert res_traces.status_code == 200
    traces = res_traces.json()
    assert len(traces) > 0
