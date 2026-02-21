from personal_website.person.dto import Person
from personal_website.person.mapper import PersonMapper


class TestPersonMapper:
    def test_person_mapper_parses_data_correctly(self, person_data):
        selected_person = person_data["items"][0]

        result = PersonMapper.dict_to_dto(item=selected_person)

        assert type(result) is Person
        assert result.name == selected_person["name"]
        assert result.avatar == selected_person["avatar"]
        assert result.title == selected_person["title"]
