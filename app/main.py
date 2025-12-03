from fastapi import FastAPI
from app.api.person_router import router as person_router
from app.api.auth_router import router as auth_router
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from app.adapters.db.models import Base
from app.adapters.repositories.sqlalchemy_person_repository import SqlAlchemyPersonRepository
from app.adapters.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./persons.db")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-please-use-env")  # change in production

def create_app() -> FastAPI:
    app = FastAPI(title="Person Service (DDD + Clean Architecture) - SQLite + Auth")

    # create async engine and sessionmaker
    engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, future=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    # attach engine and session maker to app.state for later use and shutdown
    app.state._db_engine = engine
    app.state._db_session = async_session
    app.state.SECRET_KEY = SECRET_KEY

    # create tables at startup
    @app.on_event("startup")
    async def startup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        # set repository instances (uses sessionmaker)
        app.state.person_repository = SqlAlchemyPersonRepository(async_session)
        app.state.user_repository = SqlAlchemyUserRepository(async_session)

    @app.on_event("shutdown")
    async def shutdown():
        await engine.dispose()

    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(person_router, prefix="/persons", tags=["persons"])
    return app

app = create_app()