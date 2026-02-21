from dataclasses import dataclass
from typing import Any

import pytest

from personal_website.core.mapper import BaseMapper


class TestMapper:
    def test_mapper_validation(self):
        class InvalidMapper(BaseMapper):
            pass

        with pytest.raises(NotImplementedError):
            InvalidMapper.dict_to_dto({"Hello": "There"})
