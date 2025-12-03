from fastapi.testclient import TestClient
from uuid import UUID


def _register_and_login(
    client: TestClient, email="test@gmail.com", password="password"
):
    # register user (ignore 400 if already exists)
    client.post("/auth/register", json={"email": email, "password": password})
    # login and return token
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, f"login failed: {resp.status_code} {resp.text}"
    token = resp.json()["access_token"]
    return token


def test_create_and_get_person(client):
    token = _register_and_login(client)
    payload = {"name": "Alice", "email": "alice@example.com", "age": 30}
    res = client.post(
        "/persons/", json=payload, headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 201
    created = res.json()
    assert created["name"] == "Alice"
    person_id = created["id"]

    # get by id
    get_res = client.get(f"/persons/{person_id}")
    assert get_res.status_code == 200
    got = get_res.json()
    assert got["email"] == "alice@example.com"


def test_list_and_delete_person(client):
    token = _register_and_login(client)
    # create two persons
    r1 = client.post(
        "/persons/",
        json={"name": "A", "email": "a@example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r1.status_code == 201
    r2 = client.post(
        "/persons/",
        json={"name": "B", "email": "b@example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r2.status_code == 201

    # list
    res = client.get("/persons/")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 2

    # delete one
    person_id = r1.json()["id"]
    del_res = client.delete(f"/persons/{person_id}")
    assert del_res.status_code == 204 or del_res.status_code == 200

    # list again -> should have decreased (>=1)
    res2 = client.get("/persons/")
    assert res2.status_code == 200
    assert len(res2.json()) >= 1
