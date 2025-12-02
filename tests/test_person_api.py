import asyncio
from fastapi.testclient import TestClient
from app.main import create_app
from app.adapters.repositories.in_memory_person_repository import InMemoryPersonRepository

app = create_app()

def test_create_and_get_person():
    # override repository with a fresh in-memory repo for test isolation
    app.state.person_repository = InMemoryPersonRepository()
    client = TestClient(app)

    payload = {"name": "Alice", "email": "alice@example.com", "age": 30}
    res = client.post("/persons/", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    person_id = data["id"]

    # retrieve
    res2 = client.get(f"/persons/{person_id}")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["id"] == person_id
    assert data2["name"] == "Alice"

def test_list_and_delete_person():
    app.state.person_repository = InMemoryPersonRepository()
    client = TestClient(app)

    # create two
    client.post("/persons/", json={"name": "A", "email": "a@example.com"})
    client.post("/persons/", json={"name": "B", "email": "b@example.com"})
    res = client.get("/persons/")
    assert res.status_code == 200
    assert len(res.json()) == 2

    # delete one
    persons = res.json()
    client.delete(f'/persons/{persons[0]["id"]}')
    res2 = client.get("/persons/")
    assert len(res2.json()) == 1