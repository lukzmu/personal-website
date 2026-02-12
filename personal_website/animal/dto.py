from dataclasses import dataclass


@dataclass(frozen=True)
class Animal:
    name: str
    avatar: str
    alive: bool
