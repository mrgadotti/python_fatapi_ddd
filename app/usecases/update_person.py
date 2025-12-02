from uuid import UUID
from typing import Optional
from app.domain.person import Person
from app.domain.repository.person_repository import PersonRepository

class UpdatePerson:
    def __init__(self, repository: PersonRepository):
        self.repository = repository

    async def execute(self, person_id: UUID, name: Optional[str]=None, email: Optional[str]=None, age: Optional[int]=None) -> Optional[Person]:
        existing = await self.repository.get_by_id(person_id)
        if not existing:
            return None
        # Build updated entity (immutability)
        updated = Person(
            id=existing.id,
            name=name if name is not None else existing.name,
            email=email if email is not None else existing.email,
            age=age if age is not None else existing.age,
        )
        return await self.repository.update(updated)