from app.adapters.repositories.in_memory_person_repository import InMemoryPersonRepository
from fastapi import FastAPI
from app.api.person_router import router as person_router
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from app.adapters.db.models import Base
from app.adapters.repositories.sqlalchemy_person_repository import SqlAlchemyPersonRepository

# def create_app() -> FastAPI:
#     app = FastAPI(title="Person Service (DDD + Clean Architecture)")
#     # attach default repository instance to app.state for simple DI
#     app.state.person_repository = InMemoryPersonRepository()
#     app.include_router(person_router, prefix="/persons", tags=["persons"])
#     return app


DATABASE_URL = "sqlite+aiosqlite:///./persons.db"

def create_app() -> FastAPI:
    app = FastAPI(title="Person Service (DDD + Clean Architecture) - SQLite")

    # create async engine and sessionmaker
    engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, future=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    # attach engine and session maker to app.state for later use and shutdown
    app.state._db_engine = engine
    app.state._db_session = async_session

    # create tables at startup
    @app.on_event("startup")
    async def startup():
        # create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        # set repository instance (uses sessionmaker)
        app.state.person_repository = SqlAlchemyPersonRepository(async_session)

    @app.on_event("shutdown")
    async def shutdown():
        await engine.dispose()

    app.include_router(person_router, prefix="/persons", tags=["persons"])
    return app

app = create_app()