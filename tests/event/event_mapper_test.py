from datetime import date

from personal_website.event.dto import Event
from personal_website.event.mapper import EventMapper


class TestEventMapper:
    def test_event_mapper_parses_data_correctly(data, event_data):
        selected_event = event_data["items"][1]

        result = EventMapper.dict_to_dto(item=selected_event)

        assert type(result) is Event
        assert result.title == selected_event["title"]
        assert result.icon == selected_event["icon"]
        assert isinstance(result.date, date)
