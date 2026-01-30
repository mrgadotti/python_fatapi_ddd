from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer

from app.services.auth import get_current_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def current_user_dep(request: Request, token: str = Depends(oauth2_scheme)):
    secret = request.app.state.SECRET_KEY
    return await get_current_user(request, token, secret)
