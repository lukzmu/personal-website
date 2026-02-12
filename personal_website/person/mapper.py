from typing import Any, Dict

from personal_website.core.mapper import BaseMapper
from personal_website.person.dto import Person


class PersonMapper(BaseMapper[Person]):
    @staticmethod
    def dict_to_dto(item: Dict[str, Any]) -> Person:
        return Person(
            name=item["name"],
            avatar=item["avatar"],
            title=item["title"],
        )
