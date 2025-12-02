from app.domain.person import Person
from app.domain.repository.person_repository import PersonRepository
from typing import Optional

class CreatePerson:
    def __init__(self, repository: PersonRepository):
        self.repository = repository

    async def execute(self, name: str, email: str, age: Optional[int] = None) -> Person:
        # Domain invariants and business rules would be enforced here
        person = Person(name=name, email=email, age=age)
        return await self.repository.add(person)