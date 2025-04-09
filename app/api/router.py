from datetime import datetime, timedelta
from faststream.rabbit.fastapi import RabbitBroker

from app.core.logger_config import logger
from app.tg_bot.create_bot import bot
from app.core.config import settings, scheduler
from app.dao.bookings_dao import BookingDAO
from app.db.session_maker_fast_api import db_session


router = RabbitBroker(url=settings.get_rabbitmq_url)


@router.subscriber('admin_msg')
async def send_booking_msg(msg: str):
    for admin in settings.ADMIN_IDS:
        await bot.send_message(admin, text=msg)


async def send_user_msg(user_id: int, text: str):
    await bot.send_message(user_id, text=text)


@router.subscriber('noti_user')
async def schedule_user_notifications(user_id: int):
    """Планирует отправку серии сообщений пользователю с разными интервалами."""
    now = datetime.now()

    notifications = [
        {
            "time": now + timedelta(hours=1),
            "text": "Спасибо за выбор нашего ресторана! Мы надеемся, вам понравится. "
            "Оставьте отзыв, чтобы мы стали лучше! 😊",
        },
        {
            "time": now + timedelta(hours=3),
            "text": "Не хотите забронировать столик снова? Попробуйте наше новое меню! 🍽️",
        },
        {
            "time": now + timedelta(hours=12),
            "text": "Специально для вас! Скидка 10% на следующее посещение по промокоду WELCOMEBACK. 🎉",
        },
        {
            "time": now + timedelta(hours=24),
            "text": "Мы ценим ваше мнение! Расскажите о своем опыте и получите приятный бонус! 🎁",
        },
    ]

    for i, notification in enumerate(notifications):
        job_id = f"user_notification_{user_id}_{i}"
        scheduler.add_job(
            send_user_msg,
            "date",
            run_date=notification["time"],
            args=[user_id, notification["text"]],
            id=job_id,
            replace_existing=True,
        )
        logger.info(f"Запланировано уведомление для пользователя {user_id} на {notification['time']}")


async def disable_booking():
    await BookingDAO.complete_past_bookings(session=db_session.get_session(True))
