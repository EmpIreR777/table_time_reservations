from datetime import date, datetime

from loguru import logger
from sqlalchemy import select, and_, or_, func, update, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.dao.base_dao import BaseDAO
from app.db.models.models import Booking, TimeSlot


class BookingDAO(BaseDAO[Booking]):
    """DAO для работы с бронированиями."""

    model = Booking

    @classmethod
    async def check_available_bookings(
        cls, session: AsyncSession, table_id: int, booking_date: date, time_slot_id: int
    ) -> bool:
        """
        Проверяет наличие существующих броней для стола на указанную дату и временной слот.

        :param session: Асинхронная сессия SQLAlchemy
        :param table_id: ID стола
        :param booking_date: Дата бронирования
        :param time_slot_id: ID временного слота
        :return: True если стол свободен, False если занят
        """
        logger.info(f'Проверка доступности стола {table_id} на {booking_date} в слот {time_slot_id}')
        try:
            query = select(cls.model).filter_by(table_id=table_id, date=booking_date, time_slot_id=time_slot_id)
            result = await session.execute(query)
            bookings = result.scalars().all()

            if not bookings:
                logger.info('Стол свободен - броней не найдено')
                return True

            for booking in bookings:
                if booking.status == "booked":
                    logger.info(f'Стол занят - найдена активная бронь ID {booking.id}')
                    return False

            logger.info('Стол свободен - все брони неактивны')
            return True

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при проверке доступности брони: {e}")
            raise

    @classmethod
    async def get_available_time_slots(cls, session: AsyncSession, table_id: int, booking_date: date) -> list[TimeSlot]:
        """
        Получает список доступных временных слотов для стола на указанную дату.

        :param session: Асинхронная сессия SQLAlchemy
        :param table_id: ID стола
        :param booking_date: Дата бронирования
        :return: Список доступных временных слотов
        """
        logger.info(f'Получение доступных слотов для стола {table_id} на {booking_date}')
        try:
            # Получаем все брони для данного стола и даты
            bookings_query = select(cls.model).filter_by(table_id=table_id, date=booking_date)
            bookings_result = await session.execute(bookings_query)
            # Составляем набор занятых слотов (только с активными бронями)
            booked_slots = {
                booking.time_slot_id for booking in bookings_result.scalars().all() if booking.status == "booked"
            }
            # Получаем все доступные слоты
            available_slots_query = select(TimeSlot).where(~TimeSlot.id.in_(booked_slots))
            available_slots_result = await session.execute(available_slots_query)

            slots = available_slots_result.scalars().all()
            logger.info(f'Найдено {len(slots)} доступных слотов')
            return slots
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении слотов: {e}")
            raise

    @classmethod
    async def get_bookings_with_details(cls, session: AsyncSession, user_id: int) -> list[Booking]:
        """
        Получает список бронирований пользователя с деталями о столе и времени.

        :param session: Асинхронная сессия SQLAlchemy
        :param user_id: ID пользователя
        :return: Список бронирований с деталями
        """
        logger.info(f'Получение бронирований с деталями для пользователя {user_id}')
        try:
            query = (
                select(cls.model)
                .options(joinedload(cls.model.table), joinedload(cls.model.time_slot))
                .filter_by(user_id=user_id)
            )

            result = await session.execute(query)
            bookings = result.scalars().all()
            logger.info(f'Найдено {len(bookings)} бронирований')
            return bookings

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении бронирований: {e}")
            raise

    @classmethod
    async def complete_past_bookings(cls, session: AsyncSession) -> None:
        """
        Обновляет статус прошедших бронирований на 'completed'.

        :param session: Асинхронная сессия SQLAlchemy
        """
        logger.info('Обновление статусов прошедших бронирований')
        try:
            now = datetime.now()

            # Подзапрос для времени начала слота
            slot_time_subq = select(TimeSlot.start_time).where(TimeSlot.id == cls.model.time_slot_id).scalar_subquery()

            # Запрос для получения ID бронирований для обновления
            query = select(cls.model.id).where(
                and_(
                    cls.model.status == "booked",
                    or_(cls.model.date < now.date(), and_(cls.model.date == now.date(), slot_time_subq < now.time())),
                )
            )

            result = await session.execute(query)
            booking_ids = result.scalars().all()

            if not booking_ids:
                logger.info('Нет бронирований для обновления')
                return

            # Обновление статуса
            update_query = update(cls.model).where(cls.model.id.in_(booking_ids)).values(status="completed")

            await session.execute(update_query)
            await session.commit()
            logger.info(f'Обновлено {len(booking_ids)} бронирований')

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при обновлении статусов: {e}")
            await session.rollback()
            raise

    @classmethod
    async def cancel_booking(cls, session: AsyncSession, booking_id: int) -> int:
        """
        Отменяет бронирование по ID.

        :param session: Асинхронная сессия SQLAlchemy
        :param booking_id: ID бронирования
        :return: Количество изменённых записей
        """
        logger.info(f'Отмена бронирования {booking_id}')
        try:
            query = (
                update(cls.model)
                .where(cls.model.id == booking_id)
                .values(status="canceled")
                .execution_options(synchronize_session="fetch")
            )
            result = await session.execute(query)
            await session.flush()

            count = result.rowcount
            if count:
                logger.info(f'Бронирование {booking_id} отменено')
            else:
                logger.warning(f'Бронирование {booking_id} не найдено')

            return count

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при отмене бронирования: {e}")
            await session.rollback()
            raise

    @classmethod
    async def delete_booking(cls, session: AsyncSession, booking_id: int) -> int:
        """
        Удаляет бронирование по ID.

        :param session: Асинхронная сессия SQLAlchemy
        :param booking_id: ID бронирования
        :return: Количество удалённых записей
        """
        logger.info(f'Удаление бронирования {booking_id}')
        try:
            query = delete(cls.model).where(cls.model.id == booking_id)
            result = await session.execute(query)

            count = result.rowcount
            logger.info(f'Удалено {count} бронирований')
            await session.flush()
            return count

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при удалении бронирования: {e}")
            await session.rollback()
            raise

    @classmethod
    async def book_count(cls, session: AsyncSession) -> dict[str, int]:
        """
        Подсчитывает количество бронирований по каждому статусу и общее количество.
        
        :param session: Асинхронная сессия SQLAlchemy
        :return: Словарь с количеством бронирований по статусам и общим количеством
        """
        logger.info('Подсчет статистики бронирований по статусам')
        try:
            statuses = ["booked", "completed", "canceled"]
            stats = {}

            # Получаем количество по каждому статусу
            for status in statuses:
                query = select(func.count(cls.model.id)).where(cls.model.status == status)
                result = await session.execute(query)
                stats[status] = result.scalar_one()
                logger.debug(f'Статус {status}: {stats[status]} бронирований')

            # Получаем общее количество бронирований
            total_query = select(func.count(cls.model.id))
            stats['total'] = (await session.execute(total_query)).scalar_one()

            logger.info(f'Итого бронирований: {stats["total"]} (booked: {stats["booked"]}, '
                    f'completed: {stats["completed"]}, canceled: {stats["canceled"]})')

            return stats

        except SQLAlchemyError as e:
            logger.error(f'Ошибка при подсчете статистики бронирований: {e}')
            raise
