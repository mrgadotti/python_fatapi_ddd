from typing import List
from app.domain.repository.git_repository import GitRepository
from app.domain.git_repo import GitRepo


class ListGitRepos:
    def __init__(self, repo: GitRepository):
        self.repo = repo

    async def execute(self) -> List[GitRepo]:
        return await self.repo.list_repos()
