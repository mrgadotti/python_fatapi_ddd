import logging

from fastapi import APIRouter, Request, HTTPException, status, Depends
from datetime import timedelta, datetime, timezone
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.adapters.schemas.auth_schema import (
    TokenResponse,
    LoginRequest,
    RegisterRequest,
)
from app.services.auth import authenticate_user, create_access_token, get_password_hash
from app.domain.user import User
from uuid import uuid4

router = APIRouter()
logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer()


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Authenticates a user and returns a JWT access token.",
)
async def login(request: Request, body: LoginRequest):
    """
    Logs a user in. Accepts JSON body: {"email": "...", "password": "..."}.
    Returns access token (JWT) that expires in 24h.
    """
    user_repo = request.app.state.user_repository
    user = await authenticate_user(user_repo, body.email, body.password)
    if not user:
        logger.info("Login failed for email=%s", body.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    # create token
    expires = timedelta(minutes=request.app.state.ACCESS_TOKEN_EXPIRE_MINUTES)
    token, expire_dt, _ = create_access_token(
        {"sub": user.email}, request.app.state.SECRET_KEY, expires_delta=expires
    )
    logger.info(
        "Login success for email=%s expires_at=%s",
        user.email,
        expire_dt,
        stacklevel=2
    )
    return TokenResponse(access_token=token, expires_at=expire_dt)


@router.post(
    "/register",
    status_code=201,
    summary="Register",
    description="Registers a new user with email and password.",
)
async def register(request: Request, body: RegisterRequest) -> dict[str, str]:
    """
    Register a new user (email + password).
    """
    # Basic limits
    if len(body.password) == 0:
        raise HTTPException(status_code=400, detail="Password cannot be empty")
    if len(body.password) > 1024:
        raise HTTPException(status_code=400, detail="Password too long")

    user_repo = request.app.state.user_repository
    existing = await user_repo.get_by_email(body.email)
    if existing:
        logger.info("Register blocked: email already registered=%s", body.email)
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        hashed = get_password_hash(body.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    user = User(id=uuid4(), email=body.email, hashed_password=hashed, is_active=True)
    created = await user_repo.create(user)
    logger.info("User registered: email=%s", created.email)
    return {"id": str(created.id), "email": created.email}


@router.post(
    "/logout",
    status_code=204,
    summary="Logout",
    description="Revokes the current access token.",
)
async def logout(
    request: Request, creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    """
    Logout by revoking the current token. Token jti is stored in DB with its expiry.
    """
    secret_key = request.app.state.SECRET_KEY
    from jose import jwt, JWTError

    token = creds.credentials

    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        jti = payload.get("jti")
        exp = payload.get("exp")
        if jti is None or exp is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )

    expires_at = datetime.fromtimestamp(exp, timezone.utc)
    user_repo = request.app.state.user_repository
    await user_repo.add_revoked_token(jti, expires_at)
    logger.info("Token revoked: jti=%s", jti)
    return None
