from personal_website.animal.dto import Animal
from personal_website.animal.mapper import AnimalMapper


class TestAnimalMapper:
    def test_animal_mapper_parses_data_correctly(self, animal_data):
        selected_animal = animal_data["items"][0]

        result = AnimalMapper.dict_to_dto(item=selected_animal)

        assert type(result) is Animal
        assert result.name == selected_animal["name"]
        assert result.avatar == selected_animal["avatar"]
        assert result.alive == selected_animal["alive"]
