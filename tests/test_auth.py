import pytest
import uuid
from jose import jwt


def test_register_and_login(client):
    # use a unique email to avoid UNIQUE constraint with persistent DB
    unique_email = f"newuser+{uuid.uuid4().hex[:8]}@example.com"
    resp = client.post(
        "/auth/register", json={"email": unique_email, "password": "secret123"}
    )
    assert resp.status_code == 201, f"register failed: {resp.status_code} {resp.text}"
    body = resp.json()
    assert body["email"] == unique_email
    assert "id" in body

    # login
    resp2 = client.post(
        "/auth/login", json={"email": unique_email, "password": "secret123"}
    )
    assert resp2.status_code == 200, f"login failed: {resp2.status_code} {resp2.text}"
    data = resp2.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_at" in data

    # validate token payload
    token = data["access_token"]
    secret = client.app.state.SECRET_KEY
    payload = jwt.decode(token, secret, algorithms=["HS256"])
    assert payload.get("sub") == unique_email
    assert "jti" in payload
    assert "exp" in payload


def test_login_wrong_password(test_user, client):
    # attempt login with wrong password
    resp = client.post(
        "/auth/login", json={"email": test_user["email"], "password": "wrongpassword"}
    )
    assert resp.status_code == 401


def test_logout_revokes_token_and_protected_endpoint(test_user, client):
    # login to get token
    resp = client.post(
        "/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]},
    )
    assert resp.status_code == 200, f"login failed: {resp.status_code} {resp.text}"
    token = resp.json()["access_token"]

    # call a protected endpoint (create person) - should succeed
    create_resp = client.post(
        "/persons/",
        json={"name": "Alice", "email": "alice@example.com", "age": 30},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_resp.status_code == 201

    # logout -> revoke token
    logout_resp = client.post(
        "/auth/logout", headers={"Authorization": f"Bearer {token}"}
    )
    assert logout_resp.status_code == 204

    # further calls with same token must be unauthorized
    create_resp2 = client.post(
        "/persons/",
        json={"name": "Bob", "email": "bob@example.com", "age": 40},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_resp2.status_code == 401
