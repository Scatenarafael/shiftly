from typing import Protocol

class {{Entity}}Record(Protocol):
    id: int
    name: str

class {{Entity}}RepositoryPort(Protocol):
    async def exists_by_name(self, name: str) -> bool: ...
    async def create(self, name: str) -> {{Entity}}Record: ...
