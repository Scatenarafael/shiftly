from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import {{Entity}}Model

class SqlAlchemy{{Entity}}Repository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def exists_by_name(self, name: str) -> bool:
        stmt = select({{Entity}}Model.id).where({{Entity}}Model.name == name).limit(1)
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none() is not None

    async def create(self, name: str) -> {{Entity}}Model:
        obj = {{Entity}}Model(name=name)
        self._session.add(obj)
        await self._session.flush()  # obtém PK sem commit
        return obj
