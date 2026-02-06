from dataclasses import dataclass


@dataclass(slots=True)
class Role:
    id: str
    name: str
    company_id: str | None
    number_of_cooldown_days: int = 0
