from dataclasses import dataclass


@dataclass(frozen=True)
class Citation:
    number: int
    label: str
    url: str

    @property
    def anchor(self) -> str:
        return f"citation-{self.number}"
