import logging
import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class SMSService:
    def __init__(self):
        """
        Класс для работы с API SMS.ru
        Инициализирует необходимые параметры из настроек
        """
        self.api_id = settings.SMS_RU_API_ID
        # self.sender = settings.SMS_RU_SENDER
        self.api_url = 'https://sms.ru/sms/send'

        if not self.api_id:
            raise ValueError('API ключ SMS.ru не установлен в настройках')

    async def send_sms(self, phone: str, message: str) -> dict:
        """
        Асинхронный метод для отправки SMS через сервис SMS.ru

        Параметры:
            phone: str - Номер телефона получателя (формат: 79991234567)
            message: str - Текст сообщения (до 800 символов)

        Возвращает:
            dict - Ответ от API SMS.ru

        Исключения:
            HTTPException - В случае ошибки при отправке
        """

        if not phone or not message:
            raise ValueError('Требуется указать номер телефона и текст сообщения')

        params = {
            'api_id': self.api_id,  # API-ключ
            'to': phone,  # Номер получателя
            'msg': message,  # Текст сообщения
            'json': 1,  # Запрашиваем ответ в JSON-формате
            # 'from': self.sender  # Имя отправителя
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.api_url, params=params)
                response.raise_for_status() # Проверяем статус ответа
                data = response.json() # Парсим JSON-ответ

                if data.get('status') != 'OK':
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,  # 400 - Неверный запрос
                        detail=f'Ошибка отправки SMS: {data.get("status_text", "Неизвестная ошибка")}',)
                return data

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,  # 503 - Сервис недоступен
                detail=f'Ошибка подключения к API SMS.ru: {str(e)}',
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,  # 500 - Внутренняя ошибка сервера
                detail=f'Внутренняя ошибка при отправке SMS: {str(e)}',
            )


sms_service = SMSService()
