from datetime import datetime
from loguru import logger

from app.async_client import http_client_manager
from app.core.config import scheduler
from app.tg_bot.methods import bot_send_message
from app.tg_bot.utils import format_appointment


async def send_user_noti(user_tg_id: int, appointment: dict):
    async with http_client_manager.client() as client:
        text = format_appointment(
            appointment, start_text='❗ Напоминаем, что у вас назначена запись к доктору ❗')
        try:
            await bot_send_message(client=client, chat_id=user_tg_id, text=text)
        except Exception as e:
            logger.error(e)


async def schedule_appointment_notification(
    user_tg_id: int, appointment: dict, notification_time: datetime, reminder_label: str
        ):
    """
    Планирует напоминание с уникальным job_id для каждого случая.

    :param user_tg_id: ID пользователя Telegram
    :param appointment: Данные о записи
    :param notification_time: Время напоминания
    :param reminder_label: Уникальный идентификатор напоминания (например, 'immediate', '24h', '6h', '30min')
    """

    job_id = f'notification_{user_tg_id}_{appointment["id"]}_{reminder_label}'

    scheduler.add_job(
        send_user_noti,  # Функция, которая будет выполнена
        'date',  # Тип триггера (в данном случае одноразовая задача)
        run_date=notification_time,  # Время выполнения задачи
        args=[user_tg_id, appointment],  # Аргументы для функции
        id=job_id,  # Уникальный идентификатор задачи
        replace_existing=True,  # Заменить задачу, если ID уже существует
    )
