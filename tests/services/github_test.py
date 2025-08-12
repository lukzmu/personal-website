import pytest
import httpx


class TestGitHubService:
    def test_init_requires_token(self, github_client):
        with pytest.raises(ValueError):
            type(github_client)(None)
        with pytest.raises(ValueError):
            type(github_client)("")

    def test_get_repositories_happy_path_filters_ignored_and_uses_correct_request(
        self,
        monkeypatch,
        github_client,
        stub_response,
    ):
        captured = {}

        def fake_get(*, url, headers, params):
            captured["url"] = url
            captured["headers"] = headers
            captured["params"] = params
            data = [
                {"name": "lukzmu", "id": 1},
                {"name": "hello-there", "id": 2},
                {"name": "general-kenobi", "id": 3},
            ]
            return stub_response(json_data=data)

        monkeypatch.setattr(httpx, "get", fake_get)

        repos = github_client.get_repositories()

        assert [r["name"] for r in repos] == ["hello-there", "general-kenobi"]
        assert captured["url"] == "https://api.github.com/user/repos"
        assert captured["headers"]["Accept"] == "application/vnd.github+json"
        assert captured["headers"]["Authorization"] == f"Bearer dummy-token"
        assert captured["headers"]["X-GitHub-Api-Version"] == "2022-11-28"
        assert captured["params"] == {"sort": "updated", "type": "public"}

    def test_get_repositories_propagates_http_errors(self, monkeypatch, github_client, stub_response):
        url = "https://api.github.com/user/repos"
        request = httpx.Request("GET", url)
        response = httpx.Response(403, request=request)
        err = httpx.HTTPStatusError("Forbidden", request=request, response=response)

        def fake_get(*, url, headers, params):
            return stub_response(json_data=None, raise_err=err)

        monkeypatch.setattr(httpx, "get", fake_get)

        with pytest.raises(httpx.HTTPStatusError):
            github_client.get_repositories()

    def test_get_repositories_returns_empty_when_all_ignored(self, monkeypatch, github_client, stub_response):
        def fake_get(*, url, headers, params):
            return stub_response(json_data=[{"name": "lukzmu", "id": 1}])

        monkeypatch.setattr(httpx, "get", fake_get)

        assert github_client.get_repositories() == []
