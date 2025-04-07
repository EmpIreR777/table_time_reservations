from asyncio import sleep
from datetime import datetime

from httpx import AsyncClient
from app.core.config import settings


async def bot_send_typing_action(client: AsyncClient, chat_id: int):
    """
    Отправляет действие 'печатает...' в чат Telegram.
    """
    await client.post(
        f"{settings.get_tg_api_url()}/sendChatAction",
          json={"chat_id": chat_id, "action": "typing"})
    await sleep(2)


def pluralize_appointments(count: int) -> str:
    if count == 1:
        return "прием"
    elif 2 <= count <= 4:
        return "приема"
    else:
        return "приемов"


def format_appointment(appointment, start_text='🗓 <b>Запись на прием</b>'):
    appointment_date = datetime.strptime(
        appointment['day_booking'], '%Y-%m-%d').strftime('%d.%m.%Y')
    return f"""
            {start_text}

            📅 Дата: {appointment_date}
            🕒 Время: {appointment['time_booking']}
            👨‍⚕️ Врач: {appointment['doctor_full_name']}
            🏥 Специализация: {appointment['special']}

            ℹ️ Номер записи: {appointment['id']}

            Пожалуйста, приходите за 10-15 минут до назначенного времени.
            """
