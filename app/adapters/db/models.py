from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class PersonModel(Base):
    __tablename__ = "persons"

    id = Column(String(length=36), primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    age = Column(Integer, nullable=True)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(length=36), primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)


class RevokedTokenModel(Base):
    __tablename__ = "revoked_tokens"

    jti = Column(String, primary_key=True, index=True)
    expires_at = Column(DateTime, nullable=False)

    def is_expired(self) -> bool:
        return datetime.utcnow() >= self.expires_at
