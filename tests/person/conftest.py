import pytest

from personal_website.person.mapper import PersonMapper
from personal_website.person.repository import PersonRepository


@pytest.fixture
def person_repository():
    return PersonRepository(mapper=PersonMapper)


@pytest.fixture
def person_data():
    return {
        "items": [
            {
                "name": "Łukasz",
                "avatar": "lukasz.png",
                "title": "Python Engineer",
            },
            {
                "name": "Anna",
                "avatar": "ania.png",
                "title": "Animal Sciences PhD",
            },
        ]
    }
