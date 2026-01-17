from fastapi import APIRouter, Depends, HTTPException, status

from src.app.controllers.schemas.pydantic.workdays_dtos import CreateWorkdayPayload, UpdateWorkdayDTO, UpdateWorkdayPayload
from src.app.repositories.workdays_repository import WorkdaysRepository
from src.domain.entities.work_day import WorkDay
from src.usecases.workdays.create_workday_usecase import CreateWorkdayUseCase
from src.usecases.workdays.delete_workday_usecase import DeleteWorkdayUseCase
from src.usecases.workdays.list_workdays_usecase import ListWorkdaysUseCase
from src.usecases.workdays.update_workday_usecase import UpdateWorkdayUseCase

router = APIRouter(tags=["workdays"], prefix="/workdays")


def get_list_workday_usecase():
    return ListWorkdaysUseCase(WorkdaysRepository())


def get_create_workday_usecase():
    return CreateWorkdayUseCase(WorkdaysRepository())


def get_update_workday_usecase():
    return UpdateWorkdayUseCase(WorkdaysRepository())


def get_delete_workday_usecase():
    return DeleteWorkdayUseCase(WorkdaysRepository())


@router.get("")
async def list_workdays(list_workdays_usecase: ListWorkdaysUseCase = Depends(get_list_workday_usecase)):
    try:
        workdays = await list_workdays_usecase.execute()
        return workdays
    except Exception as e:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("")
async def create_workday(payload: CreateWorkdayPayload, create_workday_usecase: CreateWorkdayUseCase = Depends(get_create_workday_usecase)):
    try:
        new_workday = await create_workday_usecase.execute(workday=WorkDay(**payload.model_dump()))
        return new_workday
    except Exception as e:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{workday_id}")
async def update_workday(workday_id: int, payload: UpdateWorkdayPayload, update_workday_usecase: UpdateWorkdayUseCase = Depends(get_update_workday_usecase)):
    try:
        updated_workday = await update_workday_usecase.execute(workday_id=workday_id, payload=UpdateWorkdayDTO.from_payload(payload))
        return updated_workday
    except Exception as e:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{workday_id}")
async def delete_workday(workday_id: int, delete_workday_usecase: DeleteWorkdayUseCase = Depends(get_delete_workday_usecase)):
    try:
        await delete_workday_usecase.execute(workday_id=workday_id)
        return {"detail": "Workday deleted successfully"}
    except Exception as e:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
