from dataclasses import dataclass, field
from uuid import UUID, uuid4

@dataclass(frozen=True)
class User:
    id: UUID = field(default_factory=uuid4)
    email: str = ""
    hashed_password: str = ""
    is_active: bool = True