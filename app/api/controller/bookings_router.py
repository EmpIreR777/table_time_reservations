from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
import pytz
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.bookings_dao import BookingDAO
from app.dao.doctors_dao import DoctorDAO
from app.dao.users_dao import UserDAO
from app.db.session_maker_fast_api import db_session
from app.schemas.bookings_schemas import BookingRequest
from app.tg_bot.scheduler_task import schedule_appointment_notification


MOSCOW_TZ = pytz.timezone('Europe/Moscow')

router = APIRouter(tags=['Bookings'])


@router.get('/booking/available-slots/{doctor_id}')
async def get_available_slots(
    doctor_id: int, start_date: date, session: AsyncSession = Depends(db_session.get_session)
        ):
    """
    Эндпоинт для получения доступных слотов для записи к врачу.
    """
    try:
        slots = await BookingDAO.get_available_slots(session=session, doctor_id=doctor_id, start_date=start_date)
        return slots
    except Exception as e:
        logger.error(f"Ошибка при получении доступных слотов: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка при получении доступных слотов"
        )


@router.post("/book")
async def book_appointment_and_schedule_notifications(
    booking_request: BookingRequest, session: AsyncSession = Depends(db_session.get_session)
        ):
    """
    Эндпоинт для бронирования записи и планирования уведомлений.
    """
    try:
        # Получение user_id по Telegram ID
        user_id = await UserDAO.get_user_id(session=session, telegram_id=booking_request.user_id)
        if not user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

        # Создание брони в базе данных
        appointment = await BookingDAO.book_appointment(
            session=session,
            doctor_id=booking_request.doctor_id,
            user_id=user_id,
            day_booking=booking_request.day_booking,
            time_booking=booking_request.time_booking,
        )

        # Получение информации о враче
        doctor_info = await DoctorDAO.find_one_or_none_by_id(session=session, data_id=booking_request.doctor_id)
        if not doctor_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Врач не найден')

        # Формирование объекта appointment для уведомлений
        appointment_details = {
            'id': appointment.id,
            'day_booking': appointment.day_booking.strftime("%Y-%m-%d"),
            'time_booking': appointment.time_booking.strftime("%H:%M"),
            'special': doctor_info.special,
            'doctor_full_name': f'{doctor_info.first_name} {doctor_info.last_name} {doctor_info.patronymic}',
        }

        # Расчет времени напоминаний
        booking_time_str = f"{appointment_details['day_booking']} {appointment_details['time_booking']}"
        booking_time = datetime.strptime(booking_time_str, '%Y-%m-%d %H:%M').replace(tzinfo=MOSCOW_TZ)
        now = datetime.now(MOSCOW_TZ)
        notification_times = []

        # Напоминание 1: Сразу
        await schedule_appointment_notification(
            user_tg_id=booking_request.user_id,
            appointment=appointment_details,
            notification_time=now,
            reminder_label="immediate",
        )
        notification_times.append(now)

        # Напоминание 2: За сутки
        time_24h = booking_time - timedelta(hours=24)
        if time_24h > now:
            await schedule_appointment_notification(
                user_tg_id=booking_request.user_id,
                appointment=appointment_details,
                notification_time=time_24h,
                reminder_label="24h",
            )
            notification_times.append(time_24h)

        # Напоминание 3: За 6 часов
        time_6h = booking_time - timedelta(hours=6)
        if time_6h > now:
            await schedule_appointment_notification(
                user_tg_id=booking_request.user_id,
                appointment=appointment_details,
                notification_time=time_6h,
                reminder_label="6h",
            )
            notification_times.append(time_6h)

        # Напоминание 4: За 30 минут
        time_30min = booking_time - timedelta(minutes=30)
        if time_30min > now:
            await schedule_appointment_notification(
                user_tg_id=booking_request.user_id,
                appointment=appointment_details,
                notification_time=time_30min,
                reminder_label="30min",
            )
            notification_times.append(time_30min)

        # Форматирование времени уведомлений для ответа
        notification_times_formatted = [time.strftime("%Y-%m-%d %H:%M:%S") for time in notification_times]

        return {
            "status": "SUCCESS",
            "message": "Запись успешно создана и напоминания запланированы!",
            "appointment": appointment_details,
            "notification_times": notification_times_formatted,
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Ошибка в book_appointment_and_schedule_notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании брони и планировании уведомлений",
        )
