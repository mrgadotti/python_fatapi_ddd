from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, update as sa_update, delete as sa_delete
from app.domain.person import Person
from app.domain.repository.person_repository import PersonRepository
from app.adapters.db.models import PersonModel


class SqlAlchemyPersonRepository(PersonRepository):
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self._sessionmaker = sessionmaker

    async def add(self, person: Person) -> Person:
        async with self._sessionmaker() as session:
            orm = PersonModel(
                id=str(person.id),
                name=person.name,
                email=person.email,
                age=person.age,
            )
            session.add(orm)
            await session.commit()
            await session.refresh(orm)
            return Person(id=UUID(orm.id), name=orm.name, email=orm.email, age=orm.age)

    async def get_by_id(self, person_id: UUID) -> Optional[Person]:
        async with self._sessionmaker() as session:
            result = await session.get(PersonModel, str(person_id))
            if not result:
                return None
            return Person(
                id=UUID(result.id), name=result.name, email=result.email, age=result.age
            )

    async def list(self) -> List[Person]:
        async with self._sessionmaker() as session:
            q = select(PersonModel)
            res = await session.execute(q)
            rows = res.scalars().all()
            return [
                Person(id=UUID(r.id), name=r.name, email=r.email, age=r.age)
                for r in rows
            ]

    async def update(self, person: Person) -> Person:
        async with self._sessionmaker() as session:
            q = (
                sa_update(PersonModel)
                .where(PersonModel.id == str(person.id))
                .values(name=person.name, email=person.email, age=person.age)
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(q)
            await session.commit()
            # reload
            orm = await session.get(PersonModel, str(person.id))
            if not orm:
                raise KeyError("Person not found")
            return Person(id=UUID(orm.id), name=orm.name, email=orm.email, age=orm.age)

    async def delete(self, person_id: UUID) -> None:
        async with self._sessionmaker() as session:
            q = sa_delete(PersonModel).where(PersonModel.id == str(person_id))
            await session.execute(q)
            await session.commit()
