import httpx
import pytest

from personal_website.services.github import GitHubClient


class TestGitHubClient:
    def test_github_client_constructor_raises_error_when_token_is_missing(self):
        with pytest.raises(ValueError, match="GitHub token needs to be set"):
            GitHubClient(token=None)

    def test_get_repositories_returns_sorted_and_filtered_repositories(self, mocker):
        mocked_response = mocker.Mock()
        mocked_response.json.return_value = [
            {
                "name": "old-public-repo",
                "archived": False,
                "updated_at": "2025-12-01T10:00:00Z",
            },
            {
                "name": "lukzmu",
                "archived": False,
                "updated_at": "2026-02-20T10:00:00Z",
            },
            {
                "name": "archived-newest",
                "archived": True,
                "updated_at": "2026-02-21T10:00:00Z",
            },
            {
                "name": "active-newest",
                "archived": False,
                "updated_at": "2026-02-21T09:00:00Z",
            },
        ]
        mocked_get = mocker.patch("personal_website.services.github.httpx.get", return_value=mocked_response)

        result = GitHubClient(token="test-token").get_repositories()

        mocked_get.assert_called_once_with(
            url="https://api.github.com/user/repos",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": "Bearer test-token",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            params={
                "sort": "updated",
                "type": "public",
            },
        )
        mocked_response.raise_for_status.assert_called_once()
        assert [repository["name"] for repository in result] == [
            "active-newest",
            "old-public-repo",
            "archived-newest",
        ]

    def test_get_repositories_raises_for_failed_api_response(self, mocker):
        mocked_response = mocker.Mock()
        mocked_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            message="Request failed",
            request=httpx.Request("GET", "https://api.github.com/user/repos"),
            response=httpx.Response(status_code=500),
        )
        mocker.patch("personal_website.services.github.httpx.get", return_value=mocked_response)

        with pytest.raises(httpx.HTTPStatusError, match="Request failed"):
            GitHubClient(token="test-token").get_repositories()

        mocked_response.json.assert_not_called()
