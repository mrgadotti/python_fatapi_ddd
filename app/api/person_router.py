from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from uuid import UUID

from app.adapters.schemas.person_schema import PersonCreate, PersonUpdate, PersonOut
from app.usecases.create_person import CreatePerson
from app.usecases.get_person import GetPerson
from app.usecases.list_persons import ListPersons
from app.usecases.update_person import UpdatePerson
from app.usecases.delete_person import DeletePerson
from app.domain.repository.person_repository import PersonRepository
from app.services.auth import get_current_user
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def repo_dep(request: Request) -> PersonRepository:
    return request.app.state.person_repository


async def current_user_dep(request: Request, token: str = Depends(oauth2_scheme)):
    secret = request.app.state.SECRET_KEY
    return await get_current_user(request, token, secret)


@router.post(
    "/",
    response_model=PersonOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(current_user_dep)],
)
async def create_person(
    cmd: PersonCreate, request: Request, repo: PersonRepository = Depends(repo_dep)
):
    uc = CreatePerson(repo)
    person = await uc.execute(name=cmd.name, email=cmd.email, age=cmd.age)
    return PersonOut(**person.__dict__)


@router.get("/", response_model=List[PersonOut])
async def list_persons(repo: PersonRepository = Depends(repo_dep)):
    uc = ListPersons(repo)
    persons = await uc.execute()
    return [PersonOut(**p.__dict__) for p in persons]


@router.get("/{person_id}", response_model=PersonOut)
async def get_person(person_id: UUID, repo: PersonRepository = Depends(repo_dep)):
    uc = GetPerson(repo)
    person = await uc.execute(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return PersonOut(**person.__dict__)


@router.put("/{person_id}", response_model=PersonOut)
async def update_person(
    person_id: UUID, cmd: PersonUpdate, repo: PersonRepository = Depends(repo_dep)
):
    uc = UpdatePerson(repo)
    updated = await uc.execute(person_id, name=cmd.name, email=cmd.email, age=cmd.age)
    if not updated:
        raise HTTPException(status_code=404, detail="Person not found")
    return PersonOut(**updated.__dict__)


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(person_id: UUID, repo: PersonRepository = Depends(repo_dep)):
    uc = DeletePerson(repo)
    await uc.execute(person_id)
    return None
