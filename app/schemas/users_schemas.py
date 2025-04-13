from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TelegramIDModel(BaseModel):
    """
    Базовая модель для работы с Telegram ID.
    """

    telegram_id: int = Field(description='Telegram ID пользователя', example=123456789)

    model_config = ConfigDict(from_attributes=True)


class SpecIDModel(BaseModel):
    """
    Модель для работы с ID специализации.
    """

    specialization_id: int = Field(description='ID специализации', example=1)


class UserModel(TelegramIDModel):
    """
    Модель пользователя с дополнительной информацией.
    """

    username: Optional[str] = Field(None, description='Имя пользователя', example='john_doe')
    first_name: Optional[str] = Field(None, description='Имя', example='John')
    last_name: Optional[str] = Field(None, description='Фамилия', example='Doe')


class SMSRequest(BaseModel):
    phone: str
    message: str
