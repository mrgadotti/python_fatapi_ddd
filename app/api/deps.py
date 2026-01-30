from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.auth import get_current_user

bearer_scheme = HTTPBearer()


async def current_user_dep(
    request: Request, creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    token = creds.credentials
    secret = request.app.state.SECRET_KEY
    return await get_current_user(request, token, secret)
