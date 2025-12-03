from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from app.domain.user import User
from datetime import datetime


class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def add_revoked_token(self, jti: str, expires_at: datetime) -> None:
        raise NotImplementedError

    @abstractmethod
    async def is_token_revoked(self, jti: str) -> bool:
        raise NotImplementedError
