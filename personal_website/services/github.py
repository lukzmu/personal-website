from datetime import datetime
from enum import Enum

import httpx


class GitHubClient:
    class _Endpoints(Enum):
        REPOSITORIES = "https://api.github.com/user/repos"

    _IGNORED_REPOSITORIES = ["lukzmu"]

    def __init__(self, token: str | None = None) -> None:
        if not token:
            raise ValueError("GitHub token needs to be set")

        self._token = token

    def get_repositories(self) -> list[dict]:
        response = httpx.get(
            url=GitHubClient._Endpoints.REPOSITORIES.value,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self._token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            params={
                "sort": "updated",
                "type": "public",
            },
        )
        response.raise_for_status()
        result = response.json()

        return [
            repository
            for repository in sorted(
                result,
                key=lambda x: (x["archived"], -self._parse_date(date_string=x["updated_at"]).timestamp()),
            )
            if repository["name"] not in self._IGNORED_REPOSITORIES
        ]

    @staticmethod
    def _parse_date(date_string: str) -> datetime:
        return datetime.fromisoformat(date_string)
