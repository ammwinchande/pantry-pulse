import pytest
from fastapi.testclient import TestClient


def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["agent_sdk"] == "AWS Strands Agents SDK"


def test_business_routes_require_auth(client):
    # Without a token, protected routes must reject with 401.
    assert client.get("/api/stats").status_code == 401
    assert client.get("/api/volunteers").status_code == 401
    assert client.get("/api/donations").status_code == 401


def test_get_stats(client, auth_headers):
    res = client.get("/api/stats", headers=auth_headers)
    assert res.status_code == 200
    stats = res.json()
    assert "total_rescued_lbs" in stats
    assert "meals_provided" in stats


def test_get_volunteers(client, auth_headers):
    res = client.get("/api/volunteers", headers=auth_headers)
    assert res.status_code == 200
    vols = res.json()
    assert len(vols) >= 5


def test_simulate_alert_and_approve(client, auth_headers):
    # Trigger simulated alert
    res_sim = client.post("/api/donations/simulate", headers=auth_headers)
    assert res_sim.status_code == 200
    proposal = res_sim.json()
    assert "id" in proposal
    assert proposal["status"] == "PROPOSED"
    prop_id = proposal["id"]

    # Check pending decisions
    res_pending = client.get("/api/decisions/pending", headers=auth_headers)
    assert res_pending.status_code == 200
    pending = res_pending.json()
    assert any(p["id"] == prop_id for p in pending)

    # Approve decision
    res_approve = client.post(
        f"/api/decisions/{prop_id}/approve",
        json={"approved_by": "Coordinator Sarah L."},
        headers=auth_headers,
    )
    assert res_approve.status_code == 200
    dispatch = res_approve.json()
    assert dispatch["status"] == "APPROVED"
    assert "pickup_verification_code" in dispatch
    # Code must be a fresh 4-digit value, not the old hardcoded default.
    assert dispatch["pickup_verification_code"] != "5821"
    assert len(dispatch["pickup_verification_code"]) == 4

    # Check traces
    res_traces = client.get("/api/agent/traces", headers=auth_headers)
    assert res_traces.status_code == 200
    traces = res_traces.json()
    assert len(traces) > 0


def test_approve_twice_is_conflict(client, auth_headers):
    res_sim = client.post("/api/donations/simulate", headers=auth_headers)
    prop_id = res_sim.json()["id"]

    first = client.post(
        f"/api/decisions/{prop_id}/approve",
        json={"approved_by": "Coordinator Sarah L."},
        headers=auth_headers,
    )
    assert first.status_code == 200

    # Second decision on the same (now APPROVED) proposal must be rejected.
    second = client.post(
        f"/api/decisions/{prop_id}/approve",
        json={"approved_by": "Coordinator Sarah L."},
        headers=auth_headers,
    )
    assert second.status_code == 409


def test_unknown_dispatch_is_404(client, auth_headers):
    res = client.post(
        "/api/dispatches/does-not-exist/pickup",
        json={"verification_code": "0000"},
        headers=auth_headers,
    )
    assert res.status_code == 404


def test_pickup_requires_correct_code(client, auth_headers):
    res_sim = client.post("/api/donations/simulate", headers=auth_headers)
    prop_id = res_sim.json()["id"]
    dispatch = client.post(
        f"/api/decisions/{prop_id}/approve",
        json={"approved_by": "Coordinator Sarah L."},
        headers=auth_headers,
    ).json()
    disp_id = dispatch["id"]

    # Wrong code -> 409 (incompatible)
    bad = client.post(
        f"/api/dispatches/{disp_id}/pickup",
        json={"verification_code": "0000"},
        headers=auth_headers,
    )
    assert bad.status_code == 409

    # Correct code -> 200
    good = client.post(
        f"/api/dispatches/{disp_id}/pickup",
        json={"verification_code": dispatch["pickup_verification_code"]},
        headers=auth_headers,
    )
    assert good.status_code == 200
    assert good.json()["status"] == "PICKED_UP"

    # Picking up again -> 409 (state machine)
    again = client.post(
        f"/api/dispatches/{disp_id}/pickup",
        json={"verification_code": dispatch["pickup_verification_code"]},
        headers=auth_headers,
    )
    assert again.status_code == 409
