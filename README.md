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

Login routes:

```bash
curl -i -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@gmail.com","password":"password"}'

curl -i -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \                 
  -d '{"email":"test@gmail.com","password":"password"}'

  ```

  Person route using token

  ```bash
ACCESS_TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@gmail.com","password":"password"}' | jq -r .access_token)

curl -i -X POST "http://127.0.0.1:8000/persons/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@example.com","age":30}'
```