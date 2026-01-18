from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status

from src.app.controllers.schemas.pydantic.workdays_dtos import (
    BatchCreateWorkdaysDTO,
    BatchCreateWorkdaysPayload,
    BatchDeleteWorkdaysPayload,
    BatchIndividualCreateWorkdaysDTO,
    BatchIndividualCreateWorkdaysPayload,
    CreateWorkdayPayload,
    UpdateWorkdayDTO,
    UpdateWorkdayPayload,
)
from src.app.repositories.workdays_repository import WorkdaysRepository
from src.domain.entities.work_day import WorkDay
from src.usecases.workdays.batch_delete_workday_usecase import BatchDeleteWorkdayUseCase
from src.usecases.workdays.batch_individual_create_workday_usecase import BatchIndividualCreateWorkdayUseCase
from src.usecases.workdays.batch_interval_create_workday_usecase import BatchIntervalCreateWorkdayUseCase
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


def get_batch_interval_create_workday_usecase():
    return BatchIntervalCreateWorkdayUseCase(WorkdaysRepository())


def get_batch_individual_create_workday_usecase():
    return BatchIndividualCreateWorkdayUseCase(WorkdaysRepository())


def get_batch_delete_workday_usecase():
    return BatchDeleteWorkdayUseCase(WorkdaysRepository())


@router.get("")
async def list_workdays(list_workdays_usecase: ListWorkdaysUseCase = Depends(get_list_workday_usecase)):
    try:
        workdays = await list_workdays_usecase.execute()
        return workdays
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("")
async def create_workday(payload: CreateWorkdayPayload, create_workday_usecase: CreateWorkdayUseCase = Depends(get_create_workday_usecase)):
    try:
        date = datetime.fromisoformat(payload.date.isoformat().replace("Z", "+00:00"))

        weekday = date.weekday()

        new_workday = await create_workday_usecase.execute(workday=WorkDay(**payload.model_dump(), weekday=weekday))

        return new_workday
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.patch("/{workday_id}")
async def update_workday(workday_id: int, payload: UpdateWorkdayPayload, update_workday_usecase: UpdateWorkdayUseCase = Depends(get_update_workday_usecase)):
    try:
        updated_workday = await update_workday_usecase.execute(workday_id=workday_id, payload=UpdateWorkdayDTO.from_payload(payload))
        return updated_workday
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/batch_individuals")
async def batch_individual_create_workdays(payload: BatchIndividualCreateWorkdaysPayload, batch_create_workday_usecase: BatchIndividualCreateWorkdayUseCase = Depends(get_batch_individual_create_workday_usecase)):
    try:
        return await batch_create_workday_usecase.execute(payloads=BatchIndividualCreateWorkdaysDTO().from_payload(payload))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/batch")
async def batch_create_workdays(payload: BatchCreateWorkdaysPayload, batch_create_workday_usecase: BatchIntervalCreateWorkdayUseCase = Depends(get_batch_interval_create_workday_usecase)):
    try:
        return await batch_create_workday_usecase.execute(payload=BatchCreateWorkdaysDTO().from_payload(payload))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete("/batch_delete")
async def batch_delete_workdays(payload: BatchDeleteWorkdaysPayload, batch_delete_workday_usecase: BatchDeleteWorkdayUseCase = Depends(get_batch_delete_workday_usecase)):
    try:
        print("Deleting workdays with IDs:", payload.workday_ids)
        await batch_delete_workday_usecase.execute(workday_ids=list(payload.workday_ids))
        return Response({"detail": "Workdays deleted successfully"}, status_code=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete("/{workday_id}")
async def delete_workday(workday_id: int, delete_workday_usecase: DeleteWorkdayUseCase = Depends(get_delete_workday_usecase)):
    try:
        await delete_workday_usecase.execute(workday_id=workday_id)
        return {"detail": "Workday deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
