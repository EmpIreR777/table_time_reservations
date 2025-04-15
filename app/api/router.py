from datetime import datetime, timedelta
from loguru import logger

from app.schemas.users_schemas import SMSRequest
from app.tg_bot.create_bot import bot
from app.core.config import settings, scheduler, broker
from app.dao.bookings_dao import BookingDAO
from app.api.utils import sms_service
from app.db.database import async_session_maker


async def disable_booking():
    async with async_session_maker() as session:
        await BookingDAO(session).complete_past_bookings()


@broker.subscriber("admin_msg")
async def send_booking_msg(msg: str):
    for admin in settings.ADMIN_IDS:
        await bot.send_message(admin, text=msg)


async def send_sms_scheduler(request: SMSRequest):
    result = await sms_service.send_sms(request.phone, request.message)
    return {'status': 'success', 'data': result, 'message': 'SMS отправлено успешно'}


async def send_user_msg(user_id: int, text: str):
    await bot.send_message(user_id, text=text)


@broker.subscriber('noti_user')
async def schedule_user_notifications(user_id: int):
    """Планирует отправку серии сообщений пользователю с разными интервалами."""
    now = datetime.now()

    notifications = [
        {
            "time": now + timedelta(minutes=1),
            "text": "Спасибо за выбор нашего ресторана! Мы надеемся, вам понравится. "
            "Оставьте отзыв, чтобы мы стали лучше! 😊",
        },
        {
            "time": now + timedelta(minutes=3),
            "text": "Не хотите забронировать столик снова? Попробуйте наше новое меню! 🍽️",
        },
        {
            "time": now + timedelta(minutes=12),
            "text": "Специально для вас! Скидка 10% на следующее посещение по промокоду WELCOMEBACK. 🎉",
        },
        {
            "time": now + timedelta(minutes=24),
            "text": "Мы ценим ваше мнение! Расскажите о своем опыте, и получите приятный бонус! 🎁",
        },
    ]

    for i, notification in enumerate(notifications):
        job_id = f"user_notification_{user_id}_{i}"
        scheduler.add_job(
            send_user_msg,  # Функция для вызова
            "date",  # Тип триггера (однократно в указанное время)
            run_date=notification["time"],  # Когда выполнить
            args=[user_id, notification["text"]],  # Аргументы
            id=job_id,  # Уникальный ID задачи
            replace_existing=True,  # Перезаписать, если задача существует
        )

        scheduler.add_job(
            sms_service.send_sms,
            "date",
            run_date=notification["time"] + timedelta(seconds=5),
            args=["89939654511", notification["text"][:10]],
            id=f"sms_{user_id}_{i}",
            replace_existing=True,
        )
        logger.info(f"Запланировано уведомление для пользователя {user_id} на {notification['time']}")
