from src.interfaces.iworkdays_repository import IWorkdaysRepository


class DeleteWorkdayUseCase:
    def __init__(self, workdays_repository: IWorkdaysRepository):
        self.workdays_repository = workdays_repository

    async def execute(self, workday_id: int) -> None:
        await self.workdays_repository.delete(workday_id)
