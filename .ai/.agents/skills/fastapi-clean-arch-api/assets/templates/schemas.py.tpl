from pydantic import BaseModel, Field
from ...application.dto.{{entity}} import {{Entity}}CreateDTO, {{Entity}}DTO

class {{Entity}}CreateIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)

    def to_dto(self) -> {{Entity}}CreateDTO:
        return {{Entity}}CreateDTO(name=self.name)

class {{Entity}}Out(BaseModel):
    id: int
    name: str

    @classmethod
    def from_dto(cls, dto: {{Entity}}DTO) -> "{{Entity}}Out":
        return cls(id=dto.id, name=dto.name)
