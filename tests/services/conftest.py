import pytest

from personal_website.services.github import GitHubClient


class _StubResponse:
    def __init__(self, *, json_data, raise_err: Exception | None = None):
        self._json_data = json_data
        self._raise_err = raise_err

    def raise_for_status(self):
        if self._raise_err:
            raise self._raise_err

    def json(self):
        return self._json_data


@pytest.fixture
def stub_response():
    return _StubResponse


@pytest.fixture
def github_client():
    return GitHubClient("dummy-token")
