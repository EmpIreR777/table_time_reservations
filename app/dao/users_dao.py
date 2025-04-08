from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.base_dao import BaseDAO
from app.db.models.models import User


class UserDAO(BaseDAO[User]):
    model = User

    @classmethod
    async def get_user_id(cls, session: AsyncSession, telegram_id: int) -> int | None:
        query = select(cls.model.id).filter_by(telegram_id=telegram_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
