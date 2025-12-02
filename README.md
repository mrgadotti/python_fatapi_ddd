# Person Service (DDD + Clean Architecture + FastAPI)

Minimal example demonstrating Domain-Driven Design and Clean Architecture for a "Person" bounded context using FastAPI.

Project layout:
- app/domain: Entities and repository interfaces
- app/usecases: Application business logic (use cases / interactors)
- app/adapters: Infrastructure (in-memory and SQLAlchemy repositories, DB models)
- app/api: FastAPI routers / controllers
- app/main.py: App factory and DI

Run locally (uses in-memory repo by default):
1. Install dependencies:
   pip install -r requirements.txt
2. Start:
   uvicorn app.main:app --reload

Run tests:
   pytest

Next steps:
- Add SQLAlchemy persistence and migrations (Alembic).
- Add authentication, validation rules, and more robust error handling/logging.

