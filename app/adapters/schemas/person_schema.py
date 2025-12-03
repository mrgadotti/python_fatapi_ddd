from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from pydantic import ConfigDict

class PersonCreate(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = None

class PersonUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None

class PersonOut(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    age: Optional[int] = None

    # Pydantic v2: to load from ORM/attribute-style objects
    model_config = ConfigDict(from_attributes=True)