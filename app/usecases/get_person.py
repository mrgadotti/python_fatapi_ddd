from uuid import UUID
from typing import Optional
from app.domain.person import Person
from app.domain.repository.person_repository import PersonRepository

class GetPerson:
    def __init__(self, repository: PersonRepository):
        self.repository = repository

    async def execute(self, person_id: UUID) -> Optional[Person]:
        return await self.repository.get_by_id(person_id)