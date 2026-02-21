import json

from personal_website.person.mapper import PersonMapper
from personal_website.person.repository import PersonRepository


class TestPersonRepository:
    def test_person_repository_constructor(self, person_repository):
        repository = PersonRepository(mapper=PersonMapper)

        assert repository._mapper == PersonMapper

    def test_people_list_returns_correct_person_count(self, person_repository, person_data, mocker):
        mocked_data = mocker.mock_open(read_data=json.dumps(person_data))
        mocker.patch("builtins.open", mocked_data)

        result = person_repository.get_items()

        assert len(result) == 2
