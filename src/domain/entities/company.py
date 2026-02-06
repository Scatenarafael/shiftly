from dataclasses import dataclass


@dataclass(slots=True)
class Company:
    id: str
    name: str
