"""
End-to-end tests for the authentication & account-management flow.

Covers: registration, email verification, login, protected routes,
password reset, and password change.
"""
import pytest


def _register(client, email="jane@example.com", password="Password123!", name="Jane Driver", role="VOLUNTEER"):
    return client.post(
        "/api/auth/register",
        json={"name": name, "email": email, "password": password, "role": role},
    )


def _verify(client, activation_url):
    token = activation_url.split("token=")[1]
    return client.post("/api/auth/verify-email", json={"token": token})


def test_register_returns_201_and_inactive(client):
    res = _register(client)
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["user"]["is_active"] is False
    assert body["user"]["email_verified_at"] is None
    # Dev aid exposes an activation URL so the flow can be completed.
    assert body["activation_url"] is not None
    # The password hash must never be serialized in any response.
    assert "password_hash" not in body["user"]


def test_register_duplicate_email_is_409(client):
    assert _register(client).status_code == 201
    dup = _register(client)
    assert dup.status_code == 409


def test_register_short_password_is_422(client):
    res = _register(client, password="short")
    assert res.status_code == 422


def test_login_before_verification_is_401(client):
    _register(client)
    res = client.post(
        "/api/auth/login",
        json={"email": "jane@example.com", "password": "Password123!"},
    )
    assert res.status_code == 401


def test_full_register_verify_login_flow(client):
    reg = _register(client)
    _verify(client, reg.json()["activation_url"])

    login = client.post(
        "/api/auth/login",
        json={"email": "jane@example.com", "password": "Password123!"},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    # Login response must not leak the password hash.
    assert "password_hash" not in login.json()["user"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "jane@example.com"
    assert me.json()["is_active"] is True
    assert "password_hash" not in me.json()


def test_verify_email_bad_token_is_400(client):
    res = client.post("/api/auth/verify-email", json={"token": "not-a-real-token"})
    assert res.status_code == 400


def test_protected_route_rejects_missing_token(client):
    assert client.get("/api/stats").status_code == 401


def test_protected_route_rejects_bad_token(client):
    res = client.get("/api/stats", headers={"Authorization": "Bearer bogus.token.here"})
    assert res.status_code == 401


def test_password_reset_flow(client):
    reg = _register(client)
    _verify(client, reg.json()["activation_url"])

    # Request reset (uniform response even for unknown emails).
    req = client.post(
        "/api/auth/password-reset/request",
        json={"email": "jane@example.com"},
    )
    assert req.status_code == 200
    assert "reset" in req.json()["message"].lower()

    # Unknown email also returns the same uniform 200 (no enumeration).
    unknown = client.post(
        "/api/auth/password-reset/request",
        json={"email": "ghost@example.com"},
    )
    assert unknown.status_code == 200
    assert unknown.json()["message"] == req.json()["message"]
    assert unknown.json()["reset_url"] is None

    # Dev aid: a known email yields a reset_url (expose_dev_tokens defaults True).
    assert req.json()["reset_url"] is not None
    assert "/reset-password?token=" in req.json()["reset_url"]


def test_password_change_requires_current_password(client, auth_headers):
    # The demo coordinator's password is known; a wrong current password fails.
    res = client.post(
        "/api/auth/password-change",
        json={"current_password": "WrongPass123!", "new_password": "NewPass123!"},
        headers=auth_headers,
    )
    assert res.status_code == 401


def test_password_change_success(client, auth_headers):
    res = client.post(
        "/api/auth/password-change",
        json={"current_password": "Coordinator123!", "new_password": "NewPass123!"},
        headers=auth_headers,
    )
    assert res.status_code == 200, res.text

    # Old password no longer works.
    old = client.post(
        "/api/auth/login",
        json={"email": "coordinator@pantrypulse.org", "password": "Coordinator123!"},
    )
    assert old.status_code == 401

    # New password works.
    new = client.post(
        "/api/auth/login",
        json={"email": "coordinator@pantrypulse.org", "password": "NewPass123!"},
    )
    assert new.status_code == 200
