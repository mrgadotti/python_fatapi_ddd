import pytest
import asyncio
from fastapi.testclient import TestClient
from typing import Dict, Optional
from datetime import datetime
from uuid import UUID, uuid4

from app.main import create_app
from app.domain.user import User
from app.services.auth import get_password_hash

# import Person dataclass / domain entity used by repositories in tests
from app.domain.person import (
    Person,
)  # adjust import if your project uses a different path/name


# Simple in-memory UserRepository implementation for tests
class InMemoryUserRepository:
    def __init__(self):
        self._users_by_email: Dict[str, User] = {}
        self._users_by_id: Dict[str, User] = {}
        self._revoked_tokens: Dict[str, datetime] = {}

    async def create(self, user: User) -> User:
        self._users_by_email[user.email] = user
        self._users_by_id[str(user.id)] = user
        return user

    async def get_by_email(self, email: str) -> Optional[User]:
        return self._users_by_email.get(email)

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self._users_by_id.get(str(user_id))

    async def add_revoked_token(self, jti: str, expires_at: datetime) -> None:
        self._revoked_tokens[jti] = expires_at

    async def is_token_revoked(self, jti: str) -> bool:
        exp = self._revoked_tokens.get(jti)
        if not exp:
            return False
        return datetime.utcnow() < exp  # token considered revoked if now < expires_at


# Simple in-memory PersonRepository implementation for tests
class InMemoryPersonRepository:
    def __init__(self):
        self._store: Dict[str, Person] = {}

    async def add(self, person: Person) -> Person:
        self._store[str(person.id)] = person
        return person

    async def get_by_id(self, person_id: UUID) -> Optional[Person]:
        return self._store.get(str(person_id))

    async def list(self):
        return list(self._store.values())

    async def update(self, person: Person) -> Person:
        if str(person.id) not in self._store:
            raise KeyError("Person not found")
        self._store[str(person.id)] = person
        return person

    async def delete(self, person_id: UUID) -> None:
        self._store.pop(str(person_id), None)


@pytest.fixture
def app():
    """
    Create a FastAPI app and replace repositories by in-memory ones for tests.
    """
    app = create_app()

    # override repositories with in-memory versions
    app.state.user_repository = InMemoryUserRepository()
    app.state.person_repository = InMemoryPersonRepository()

    # ensure a consistent secret key in tests
    app.state.SECRET_KEY = getattr(app.state, "SECRET_KEY", "test-secret-key")
    return app


@pytest.fixture
def client(app):
    """
    Provide a TestClient instance (will trigger startup/shutdown events).
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def test_user(app):
    """
    Create a pre-existing user in the in-memory repo for tests that need it.
    Returns the plain credentials and the created User object.
    Synchronous fixture that runs the async repo.create via asyncio.run to avoid async-fixture warnings.
    """
    repo = app.state.user_repository
    email = "test@gmail.com"
    raw_password = "password"
    hashed = get_password_hash(raw_password)
    user = User(id=uuid4(), email=email, hashed_password=hashed, is_active=True)

    # run the async create coroutine synchronously for the fixture
    asyncio.run(repo.create(user))
    return {"email": email, "password": raw_password, "user": user}
