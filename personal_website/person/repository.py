from personal_website.core.repository import BaseRepository
from personal_website.person.dto import Person
from personal_website.person.mapper import PersonMapper


class PersonRepository(BaseRepository[Person, PersonMapper]):
    _DATA_PATH = "personal_website/data/people.yml"


person_repository = PersonRepository(mapper=PersonMapper)
