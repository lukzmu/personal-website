from datetime import datetime
from typing import Any, Dict

from personal_website.core.mapper import BaseMapper
from personal_website.event.dto import Event


class EventMapper(BaseMapper[Event]):
    @staticmethod
    def dict_to_dto(item: Dict[str, Any]) -> Event:
        return Event(
            title=item["title"],
            icon=item["icon"],
            date=datetime.strptime(item["date"], "%Y.%m.%d").date(),
            important=item.get("important", False),
        )
