from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Request
from app.domain.user import User
from app.domain.repository.user_repository import UserRepository

# Use argon2 for password hashing (no 72-byte bcrypt limit)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# constants - in production set via env
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24h
ALGORITHM = "HS256"


def get_password_hash(password: str) -> str:
    if isinstance(password, bytes):
        password = password.decode("utf-8", errors="ignore")
    try:
        return pwd_context.hash(password)
    except Exception as exc:
        # raise a plain ValueError so callers can map to HTTP 400
        raise ValueError(f"Error hashing password: {exc}") from exc


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if isinstance(plain_password, bytes):
        plain_password = plain_password.decode("utf-8", errors="ignore")
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # treat verification errors as non-matching
        return False


def create_access_token(
    data: dict, secret_key: str, expires_delta: Optional[timedelta] = None
) -> (str, datetime, str):  # type: ignore
    to_encode = data.copy()
    jti = str(uuid4())
    now = datetime.utcnow()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": now, "jti": jti})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt, expire, jti


async def authenticate_user(
    repo: UserRepository, email: str, password: str
) -> Optional[User]:
    user = await repo.get_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


async def get_current_user(request: Request, token: str, secret_key: str) -> User:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        jti: str = payload.get("jti")
        if email is None or jti is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    repo: UserRepository = request.app.state.user_repository
    revoked = await repo.is_token_revoked(jti)
    if revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked"
        )
    user = await repo.get_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user
