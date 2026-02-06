from fastapi import APIRouter, Depends, status

from .schemas import {{Entity}}CreateIn, {{Entity}}Out
from .dependencies import get_{{entity}}_create_use_case
from ...application.use_cases.create_{{entity}} import Create{{Entity}}UseCase
from ...domain.exceptions import DomainError

router = APIRouter(prefix="/{{module}}", tags=["{{module}}"])

@router.post(
    "",
    response_model={{Entity}}Out,
    status_code=status.HTTP_201_CREATED,
)
async def create_{{entity}}(
    payload: {{Entity}}CreateIn,
    use_case: Create{{Entity}}UseCase = Depends(get_{{entity}}_create_use_case),
) -> {{Entity}}Out:
    try:
        result = await use_case.execute(payload.to_dto())
        return {{Entity}}Out.from_dto(result)
    except DomainError as e:
        # mapear para status code apropriado (422/409/404 etc)
        raise e.to_http()
