from dataclasses import asdict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from src.app.controllers.schemas.pydantic.workdays_dtos import (
    BatchCreateWorkdaysDTO,
    BatchCreateWorkdaysPayload,
    BatchDeleteWorkdaysPayload,
    BatchIndividualCreateWorkdaysDTO,
    BatchIndividualCreateWorkdaysPayload,
    CreateWorkdayPayload,
    UpdateWorkdayDTO,
    UpdateWorkdayPayload,
    WorkdayResponse,
)
from src.app.dependencies import get_workdays_repository
from src.domain.entities.work_day import WorkDay
from src.domain.errors import AlreadyExistsError, NotFoundError
from src.interfaces.iworkdays_repository import IWorkdaysRepository
from src.usecases.workdays.batch_delete_workday_usecase import BatchDeleteWorkdayUseCase
from src.usecases.workdays.batch_individual_create_workday_usecase import BatchIndividualCreateWorkdayUseCase
from src.usecases.workdays.batch_interval_create_workday_usecase import BatchIntervalCreateWorkdayUseCase
from src.usecases.workdays.create_workday_usecase import CreateWorkdayUseCase
from src.usecases.workdays.delete_workday_usecase import DeleteWorkdayUseCase
from src.usecases.workdays.list_workdays_usecase import ListWorkdaysUseCase
from src.usecases.workdays.update_workday_usecase import UpdateWorkdayUseCase

router = APIRouter(tags=["workdays"], prefix="/workdays")


def get_list_workday_usecase(workdays_repository: IWorkdaysRepository = Depends(get_workdays_repository)):
    return ListWorkdaysUseCase(workdays_repository)


def get_create_workday_usecase(workdays_repository: IWorkdaysRepository = Depends(get_workdays_repository)):
    return CreateWorkdayUseCase(workdays_repository)


def get_update_workday_usecase(workdays_repository: IWorkdaysRepository = Depends(get_workdays_repository)):
    return UpdateWorkdayUseCase(workdays_repository)


def get_delete_workday_usecase(workdays_repository: IWorkdaysRepository = Depends(get_workdays_repository)):
    return DeleteWorkdayUseCase(workdays_repository)


def get_batch_interval_create_workday_usecase(workdays_repository: IWorkdaysRepository = Depends(get_workdays_repository)):
    return BatchIntervalCreateWorkdayUseCase(workdays_repository)


def get_batch_individual_create_workday_usecase(workdays_repository: IWorkdaysRepository = Depends(get_workdays_repository)):
    return BatchIndividualCreateWorkdayUseCase(workdays_repository)


def get_batch_delete_workday_usecase(workdays_repository: IWorkdaysRepository = Depends(get_workdays_repository)):
    return BatchDeleteWorkdayUseCase(workdays_repository)


@router.get("", response_model=list[WorkdayResponse])
async def list_workdays(list_workdays_usecase: ListWorkdaysUseCase = Depends(get_list_workday_usecase)):
    try:
        workdays = await list_workdays_usecase.execute()
        return [asdict(w) for w in workdays]
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("", response_model=WorkdayResponse, status_code=status.HTTP_201_CREATED)
async def create_workday(payload: CreateWorkdayPayload, create_workday_usecase: CreateWorkdayUseCase = Depends(get_create_workday_usecase)):
    try:
        date = datetime.fromisoformat(payload.date.isoformat().replace("Z", "+00:00"))

        weekday = date.weekday()

        new_workday = await create_workday_usecase.execute(
            workday=WorkDay(id=None, role_id=payload.role_id, date=payload.date, is_holiday=payload.is_holiday, weekday=weekday)
        )

        return asdict(new_workday)
    except AlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.patch("/{workday_id}", response_model=WorkdayResponse)
async def update_workday(workday_id: int, payload: UpdateWorkdayPayload, update_workday_usecase: UpdateWorkdayUseCase = Depends(get_update_workday_usecase)):
    try:
        updated_workday = await update_workday_usecase.execute(workday_id=workday_id, payload=UpdateWorkdayDTO.from_payload(payload))
        return asdict(updated_workday)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/batch_individuals", response_model=list[WorkdayResponse])
async def batch_individual_create_workdays(payload: BatchIndividualCreateWorkdaysPayload, batch_create_workday_usecase: BatchIndividualCreateWorkdayUseCase = Depends(get_batch_individual_create_workday_usecase)):
    try:
        workdays = await batch_create_workday_usecase.execute(payloads=BatchIndividualCreateWorkdaysDTO().from_payload(payload))
        return [asdict(w) for w in workdays]
    except AlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/batch", response_model=list[WorkdayResponse])
async def batch_create_workdays(payload: BatchCreateWorkdaysPayload, batch_create_workday_usecase: BatchIntervalCreateWorkdayUseCase = Depends(get_batch_interval_create_workday_usecase)):
    try:
        workdays = await batch_create_workday_usecase.execute(payload=BatchCreateWorkdaysDTO().from_payload(payload))
        return [asdict(w) for w in workdays]
    except AlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete("/batch_delete", status_code=status.HTTP_200_OK)
async def batch_delete_workdays(payload: BatchDeleteWorkdaysPayload, batch_delete_workday_usecase: BatchDeleteWorkdayUseCase = Depends(get_batch_delete_workday_usecase)):
    try:
        await batch_delete_workday_usecase.execute(workday_ids=list(payload.workday_ids))
        return {"detail": "Workdays deleted successfully"}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{workday_id}")
async def delete_workday(workday_id: int, delete_workday_usecase: DeleteWorkdayUseCase = Depends(get_delete_workday_usecase)):
    try:
        await delete_workday_usecase.execute(workday_id=workday_id)
        return {"detail": "Workday deleted successfully"}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
