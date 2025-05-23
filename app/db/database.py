from datetime import datetime
from decimal import Decimal
import uuid
from sqlalchemy import Integer, func, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import \
    AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from app.core.config import settings


engine = create_async_engine(url=settings.get_database_url)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)


class Base(AsyncAttrs, DeclarativeBase):
    """
    Класс Base будет использоваться для создания моделей таблиц, которые автоматически добавляют поля created_at и updated_at для отслеживания времени создания и обновления записей.
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now())

    def to_dict(self, exclude_none: bool = False):
        """
        Преобразует объект модели в словарь.
        Args: exclude_none (bool): Исключать ли None значения из результата
        Returns: dict: Словарь с данными объекта
        """
        result = {}
        for column in inspect(self.__class__).columns:
            value = getattr(self, column.key)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = float(value)
            elif isinstance(value, uuid.UUID):
                value = str(value)
            if not exclude_none or value is not None:
                result[column.key] = value
        return result
