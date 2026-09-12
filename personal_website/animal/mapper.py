from typing import Any, Dict

from personal_website.animal.dto import Animal
from personal_website.core.mapper import BaseMapper


class AnimalMapper(BaseMapper[Animal]):
    @staticmethod
    def dict_to_dto(item: Dict[str, Any]) -> Animal:
        return Animal(
            name=item["name"],
            avatar=item["avatar"],
            alive=item["alive"],
        )
