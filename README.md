# Person Service (DDD + Clean Architecture + FastAPI)

Minimal example demonstrating Domain-Driven Design and Clean Architecture for a "Person" bounded context using FastAPI.

Project layout:
- app/domain: Entities and repository interfaces
- app/usecases: Application business logic (use cases / interactors)
- app/adapters: Infrastructure (in-memory and SQLAlchemy repositories, DB models)
- app/api: FastAPI routers / controllers
- app/main.py: App factory and DI

## How to run

1. Install dependencies:
   pip install -r requirements.txt
2. (Optional) Create a .env file at the project root:
   - DATABASE_URL=sqlite+aiosqlite:///./persons.db
   - SECRET_KEY=change-me-please-use-env
   - ACCESS_TOKEN_EXPIRE_MINUTES=1
3. Start the API:
   uvicorn app.main:app --reload

Example .env:

```dotenv
DATABASE_URL=sqlite+aiosqlite:///./persons.db
SECRET_KEY=change-me-please-use-env
ACCESS_TOKEN_EXPIRE_MINUTES=1
LOG_LEVEL=INFO
LOG_ENABLED=true
LOG_TO_FILE=false
LOG_FILE=logs/app.log
```

## Run tests

pytest

## Migrations

Alembic is not configured yet. Tables are created automatically on startup via SQLAlchemy (`Base.metadata.create_all`).

If you want to reset the local SQLite DB, delete persons.db and restart the API.

If you want to use migrations (Alembic), add the configuration and then run:

alembic upgrade head

## Routes

### Auth

- POST /auth/register
- POST /auth/login
- POST /auth/logout (Bearer token)

### Persons (Bearer token)

- POST /persons
- GET /persons
- GET /persons/{person_id}
- PUT /persons/{person_id}
- DELETE /persons/{person_id}

### Git (Bearer token)

- GET /git

## Examples

## Swagger (API docs)

After starting the server, open:

- http://127.0.0.1:8000/docs

### Login

```bash
curl -i -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@gmail.com","password":"password"}'

curl -i -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \                 
  -d '{"email":"test@gmail.com","password":"password"}'

  ```

### Person using token

```bash
ACCESS_TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@gmail.com","password":"password"}' | jq -r .access_token)

curl -i -X POST "http://127.0.0.1:8000/persons/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@example.com","age":30}'
```