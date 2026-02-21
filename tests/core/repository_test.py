import pytest

from personal_website.core.exception import ImproperlyConfiguredRepository
from personal_website.core.repository import BaseRepository


class TestRepository:
    def test_repository_validation(self):
        class InvalidRepository(BaseRepository):
            _DATA_PATH = ""

        with pytest.raises(ImproperlyConfiguredRepository):
            InvalidRepository(mapper=...)
