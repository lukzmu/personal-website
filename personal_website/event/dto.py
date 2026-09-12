from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Event:
    title: str
    icon: str
    date: date
    important: bool

    def __lt__(self, other_event: "Event") -> bool:
        return self.date < other_event.date
