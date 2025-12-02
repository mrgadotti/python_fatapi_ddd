from uuid import UUID
from app.domain.repository.person_repository import PersonRepository

class DeletePerson:
    def __init__(self, repository: PersonRepository):
        self.repository = repository

    async def execute(self, person_id: UUID) -> None:
        await self.repository.delete(person_id)