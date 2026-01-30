from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import List

from app.adapters.schemas.git_schema import GitRepoOut
from app.usecases.list_git_repos import ListGitRepos
from app.domain.repository.git_repository import GitRepository

router = APIRouter()


def repo_dep(request: Request) -> GitRepository:
    return request.app.state.git_repository


@router.get(
    "",
    response_model=List[GitRepoOut],
    status_code=status.HTTP_200_OK,
    summary="List GitHub repositories",
    description="Fetches public repositories from GitHub and returns name and full_name.",
)
async def list_git_repos(repo: GitRepository = Depends(repo_dep)):
    try:
        uc = ListGitRepos(repo)
        repos = await uc.execute()
        return [GitRepoOut(**r.__dict__) for r in repos]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
