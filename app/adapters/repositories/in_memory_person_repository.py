from typing import Dict, List, Optional
from uuid import UUID
from app.domain.person import Person
from app.domain.repository.person_repository import PersonRepository
import asyncio


class InMemoryPersonRepository(PersonRepository):
    def __init__(self):
        self._store: Dict[UUID, Person] = {}
        # simple lock for concurrency safety in async env
        self._lock = asyncio.Lock()

    async def add(self, person: Person) -> Person:
        async with self._lock:
            self._store[person.id] = person
            return person

    async def get_by_id(self, person_id: UUID) -> Optional[Person]:
        return self._store.get(person_id)

    async def list(self) -> List[Person]:
        return list(self._store.values())

    async def update(self, person: Person) -> Person:
        async with self._lock:
            if person.id not in self._store:
                raise KeyError("Person not found")
            self._store[person.id] = person
            return person

    async def delete(self, person_id: UUID) -> None:
        async with self._lock:
            self._store.pop(person_id, None)
