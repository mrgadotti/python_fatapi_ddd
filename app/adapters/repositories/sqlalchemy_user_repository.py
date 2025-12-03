from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select
from app.domain.user import User
from app.domain.repository.user_repository import UserRepository
from app.adapters.db.models import UserModel, RevokedTokenModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self._sessionmaker = sessionmaker

    async def create(self, user: User) -> User:
        async with self._sessionmaker() as session:
            orm = UserModel(
                id=str(user.id),
                email=user.email,
                hashed_password=user.hashed_password,
                is_active=user.is_active,
            )
            session.add(orm)
            await session.commit()
            await session.refresh(orm)
            return User(
                id=UUID(orm.id),
                email=orm.email,
                hashed_password=orm.hashed_password,
                is_active=orm.is_active,
            )

    async def get_by_email(self, email: str) -> Optional[User]:
        async with self._sessionmaker() as session:
            q = select(UserModel).where(UserModel.email == email)
            res = await session.execute(q)
            orm = res.scalar_one_or_none()
            if not orm:
                return None
            return User(
                id=UUID(orm.id),
                email=orm.email,
                hashed_password=orm.hashed_password,
                is_active=orm.is_active,
            )

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        async with self._sessionmaker() as session:
            orm = await session.get(UserModel, str(user_id))
            if not orm:
                return None
            return User(
                id=UUID(orm.id),
                email=orm.email,
                hashed_password=orm.hashed_password,
                is_active=orm.is_active,
            )

    async def add_revoked_token(self, jti: str, expires_at: datetime) -> None:
        async with self._sessionmaker() as session:
            rt = RevokedTokenModel(jti=jti, expires_at=expires_at)
            session.add(rt)
            await session.commit()

    async def is_token_revoked(self, jti: str) -> bool:
        async with self._sessionmaker() as session:
            orm = await session.get(RevokedTokenModel, jti)
            if not orm:
                return False
            # If token record exists but expired, we can consider it not revoked (or delete it).
            return not orm.is_expired()
