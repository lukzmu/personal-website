import json

from personal_website.animal.mapper import AnimalMapper
from personal_website.animal.repository import AnimalRepository


class TestAnimalRepository:
    def test_animal_repository_constructor(self):
        repository = AnimalRepository(mapper=AnimalMapper)

        assert repository._mapper == AnimalMapper

    def test_animals_list_returns_correct_animal_count(self, animal_repository, animal_data, mocker):
        mocked_data = mocker.mock_open(read_data=json.dumps(animal_data))
        mocker.patch("builtins.open", mocked_data)

        result = animal_repository.get_items()

        assert len(result) == 4

    def test_animals_list_returns_sorted_animals_by_name_and_alive(self, animal_repository, animal_data, mocker):
        mocked_data = mocker.mock_open(read_data=json.dumps(animal_data))
        mocker.patch("builtins.open", mocked_data)

        result = animal_repository.get_items()

        assert result[0].name == "Vader"
        assert result[1].name == "Wifi"
        assert result[2].name == "Bingo"
        assert result[3].name == "Stefa"
