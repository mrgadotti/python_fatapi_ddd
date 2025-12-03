from typing import List
from app.domain.person import Person
from app.domain.repository.person_repository import PersonRepository


class ListPersons:
    def __init__(self, repository: PersonRepository):
        self.repository = repository

    async def execute(self) -> List[Person]:
        return await self.repository.list()
