import pytest

from personal_website.event.mapper import EventMapper
from personal_website.event.repository import EventRepository


@pytest.fixture
def event_repository():
    return EventRepository(mapper=EventMapper)


@pytest.fixture
def event_data():
    return {
        "items": [
            {
                "title": "Anna and Łukasz get engaged",
                "icon": "💍",
                "date": "2017.09.15",
            },
            {
                "title": "Anna and Łukasz get married",
                "icon": "👰🏻‍♀️",
                "date": "2021.05.04",
            },
        ]
    }
