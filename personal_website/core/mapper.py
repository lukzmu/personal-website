from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

Model = TypeVar("Model")


class BaseMapper(ABC, Generic[Model]):
    @staticmethod
    @abstractmethod
    def dict_to_dto(item: dict[str, Any]) -> Model:
        raise NotImplementedError
