from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class PersonModel(Base):
    __tablename__ = "persons"

    id = Column(String(length=36), primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    age = Column(Integer, nullable=True)