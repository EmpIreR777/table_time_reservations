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
