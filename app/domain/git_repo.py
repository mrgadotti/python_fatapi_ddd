from dataclasses import dataclass


@dataclass(frozen=True)
class GitRepo:
    name: str
    full_name: str
