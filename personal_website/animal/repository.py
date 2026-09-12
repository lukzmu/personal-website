from typing import List

from personal_website.animal.dto import Animal
from personal_website.animal.mapper import AnimalMapper
from personal_website.core.repository import BaseRepository


class AnimalRepository(BaseRepository[Animal, AnimalMapper]):
    _DATA_PATH = "personal_website/data/animals.yml"

    def get_items(self) -> List[Animal]:
        items = super().get_items()
        return sorted(items, key=lambda x: (-x.alive, x.name))


animal_repository = AnimalRepository(mapper=AnimalMapper)
