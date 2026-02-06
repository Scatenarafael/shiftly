from dataclasses import dataclass
from ...domain.ports.{{entity}}_repo import {{Entity}}RepositoryPort
from ..dto.{{entity}} import {{Entity}}CreateDTO, {{Entity}}DTO
from ...domain.exceptions import {{Entity}}AlreadyExists

@dataclass(slots=True)
class Create{{Entity}}UseCase:
    repo: {{Entity}}RepositoryPort

    async def execute(self, data: {{Entity}}CreateDTO) -> {{Entity}}DTO:
        exists = await self.repo.exists_by_name(data.name)
        if exists:
            raise {{Entity}}AlreadyExists(name=data.name)

        created = await self.repo.create(name=data.name)
        return {{Entity}}DTO(id=created.id, name=created.name)
