from abc import ABC, abstractmethod
from typing import List
from app.domain.git_repo import GitRepo


class GitRepository(ABC):
    @abstractmethod
    async def list_repos(self) -> List[GitRepo]:
        raise NotImplementedError
