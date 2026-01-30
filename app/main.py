import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine

from app.adapters.db.models import Base
from app.adapters.repositories.github_repository import GitHubRepository
from app.adapters.repositories.sqlalchemy_person_repository import (
    SqlAlchemyPersonRepository,
)
from app.adapters.repositories.sqlalchemy_user_repository import (
    SqlAlchemyUserRepository,
)
from app.api.auth_router import router as auth_router
from app.api.deps import current_user_dep
from app.api.git_router import router as git_router
from app.api.person_router import router as person_router

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./persons.db")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-please-use-env")  # change in production
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1"))


def create_app() -> FastAPI:
    engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, future=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # attach engine and session maker to app.state for later use and shutdown
        app.state._db_engine = engine
        app.state._db_session = async_session
        app.state.SECRET_KEY = SECRET_KEY
        app.state.ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES

        # create tables at startup
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        # set repository instances (uses sessionmaker)
        app.state.person_repository = SqlAlchemyPersonRepository(async_session)
        app.state.user_repository = SqlAlchemyUserRepository(async_session)
        app.state.git_repository = GitHubRepository()
        yield
        await engine.dispose()

    app = FastAPI(
        title="Person Service (DDD + Clean Architecture) - SQLite + Auth",
        lifespan=lifespan,
    )

    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(
        person_router,
        prefix="/persons",
        tags=["persons"],
    )

    app.include_router(
        git_router,
        prefix="/git",
        tags=["git"],
        # dependencies=[Depends(current_user_dep)],
    )
    
    return app


app = create_app()
