from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.person import Person

class PersonRepository(ABC):
    @abstractmethod
    async def add(self, person: Person) -> Person:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, person_id: UUID) -> Optional[Person]:
        raise NotImplementedError

    @abstractmethod
    async def list(self) -> List[Person]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, person: Person) -> Person:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, person_id: UUID) -> None:
        raise NotImplementedError