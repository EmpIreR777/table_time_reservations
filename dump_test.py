# seed_db.py
import asyncio
from datetime import date, time
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.db.database import Base
from app.db.models.models import User, Table, TimeSlot, Booking


async def seed_database():
    # Создаем engine и подключаемся к БД
    engine = create_async_engine("sqlite+aiosqlite:///db.sqlite3")

    async with engine.begin() as conn:
        # Удаляем все таблицы и создаем заново (для тестовых целей)
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Создаем сессию для добавления данных
    async with AsyncSession(engine) as session:
        # Добавляем пользователей
        users = [
            {"telegram_id": 123456789, "username": "ivan_ivanov", "first_name": "Иван", "last_name": "Иванов"},
            {"telegram_id": 987654321, "username": "petr_petrov", "first_name": "Петр", "last_name": "Петров"},
            {"telegram_id": 555555555, "username": "anna_smith", "first_name": "Анна", "last_name": "Смит"},
        ]
        await session.execute(insert(User), users)

        # Добавляем столы
        tables = [
            {"capacity": 4, "description": "У окна"},
            {"capacity": 6, "description": "В центре зала"},
            {"capacity": 2, "description": "Романтический столик"},
            {"capacity": 8, "description": "Для большой компании"},
        ]
        await session.execute(insert(Table), tables)

        # Добавляем временные слоты
        time_slots = [
            {"start_time": time(10, 0), "end_time": time(12, 0)},
            {"start_time": time(12, 0), "end_time": time(14, 0)},
            {"start_time": time(14, 0), "end_time": time(16, 0)},
            {"start_time": time(16, 0), "end_time": time(18, 0)},
            {"start_time": time(18, 0), "end_time": time(20, 0)},
            {"start_time": time(20, 0), "end_time": time(22, 0)},
        ]
        await session.execute(insert(TimeSlot), time_slots)

        # Фиксируем изменения, чтобы получить ID
        await session.commit()

        # Получаем ID добавленных записей
        result = await session.execute(select(User.id))
        user_ids = [row[0] for row in result.all()]

        result = await session.execute(select(Table.id))
        table_ids = [row[0] for row in result.all()]

        result = await session.execute(select(TimeSlot.id))
        time_slot_ids = [row[0] for row in result.all()]

        # Добавляем бронирования
        bookings = [
            {
                "user_id": user_ids[0],
                "table_id": table_ids[0],
                "time_slot_id": time_slot_ids[1],
                "date": date(2023, 12, 15),
                "status": "booked",
            },
            {
                "user_id": user_ids[1],
                "table_id": table_ids[1],
                "time_slot_id": time_slot_ids[3],
                "date": date(2023, 12, 16),
                "status": "completed",
            },
            {
                "user_id": user_ids[2],
                "table_id": table_ids[2],
                "time_slot_id": time_slot_ids[4],
                "date": date(2023, 12, 17),
                "status": "canceled",
            },
            {
                "user_id": user_ids[0],
                "table_id": table_ids[3],
                "time_slot_id": time_slot_ids[2],
                "date": date(2023, 12, 18),
                "status": "booked",
            },
        ]
        await session.execute(insert(Booking), bookings)

        await session.commit()
        print("База данных успешно заполнена тестовыми данными!")


if __name__ == "__main__":
    asyncio.run(seed_database())
