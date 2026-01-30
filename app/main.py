import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
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
from app.api.git_router import router as git_router
from app.api.person_router import router as person_router

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./persons.db")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-please-use-env")  # change in production
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_ENABLED = os.getenv("LOG_ENABLED", "true").lower() in {"1", "true", "yes", "on"}
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "false").lower() in {"1", "true", "yes", "on"}
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")


def configure_logging() -> None:
    if not LOG_ENABLED:
        logging.disable(logging.CRITICAL)
        return
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if LOG_TO_FILE:
        log_dir = os.path.dirname(LOG_FILE)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        # Ensure the log file exists even before first write
        open(LOG_FILE, "a", encoding="utf-8").close()
        handlers.append(logging.FileHandler(LOG_FILE))

    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        handlers=handlers,
    )
    # Reduce noisy logs
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
    logging.getLogger("passlib").setLevel(logging.WARNING)


def create_app() -> FastAPI:
    configure_logging()
    logger = logging.getLogger(__name__)
    engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, future=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # attach engine and session maker to app.state for later use and shutdown
        app.state._db_engine = engine
        app.state._db_session = async_session
        app.state.SECRET_KEY = SECRET_KEY
        app.state.ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES
        logger.info("Application startup complete")

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
