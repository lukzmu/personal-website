from abc import ABC
from typing import Generic, TypeVar

import yaml

from personal_website.core.exception import ImproperlyConfiguredRepository
from personal_website.core.mapper import BaseMapper

Model = TypeVar("Model")
Mapper = TypeVar("Mapper", bound=BaseMapper)


class BaseRepository(ABC, Generic[Model, Mapper]):
    _DATA_PATH: str = ""

    def __init__(self, mapper: type[Mapper]) -> None:
        if not self._DATA_PATH:
            raise ImproperlyConfiguredRepository
        self._mapper = mapper

    def get_items(self) -> list[Model]:
        with open(self._DATA_PATH) as file:
            data = yaml.safe_load(file)
            return [self._mapper.dict_to_dto(item=item) for item in data["items"]]
