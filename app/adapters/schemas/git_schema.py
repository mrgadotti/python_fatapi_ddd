from pydantic import BaseModel, ConfigDict


class GitRepoOut(BaseModel):
    name: str
    full_name: str

    model_config = ConfigDict(from_attributes=True)
