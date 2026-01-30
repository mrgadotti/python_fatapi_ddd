from typing import List
import httpx
from app.domain.repository.git_repository import GitRepository
from app.domain.git_repo import GitRepo


class GitHubRepository(GitRepository):
    def __init__(self, repos_url: str = "https://api.github.com/users/mrgadotti/repos"):
        self.repos_url = repos_url

    async def list_repos(self) -> List[GitRepo]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                self.repos_url,
                headers={"Accept": "application/vnd.github+json"},
            )

        if response.status_code != 200:
            raise RuntimeError(
                f"GitHub API error: {response.status_code} - {response.text}"
            )

        payload = response.json()
        repos: List[GitRepo] = []
        for item in payload:
            name = item.get("name")
            full_name = item.get("full_name")
            if name is None or full_name is None:
                continue
            repos.append(GitRepo(name=name, full_name=full_name))

        return repos
