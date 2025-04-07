from datetime import date, time
from typing import List, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class BookingRequest(BaseModel):
    """
    Модель для запроса на бронирование.
    """

    doctor_id: int = Field(description='ID врача', example=1)
    user_id: int = Field(description='ID пользователя', example=123)
    day_booking: date = Field(description='Дата бронирования', example='2023-10-15')
    time_booking: time = Field(description='Время бронирования', example='14:30')

    @field_validator('time_booking')
    def validate_time_booking(cls, value: time) -> time:
        """
        Валидация времени бронирования.
        Время должно быть между 08:00 и 19:30 с шагом в 30 минут.
        """
        if not (time(8, 0) <= value <= time(19, 30)):
            raise ValueError('Время бронирования должно быть между 08:00 и 19:30')
        if value.minute not in [0, 30]:
            raise ValueError('Время бронирования должно быть на целый час или на 30 минут')
        return value


class BookingSlot(BaseModel):
    """
    Модель для представления временного слота.
    """

    time: str = Field(description='Время слота в формате HH:MM', example='14:30')
    is_available: bool = Field(description='Доступен ли слот для бронирования', example=True)


class BookingWeek(BaseModel):
    """
    Модель для представления доступных слотов на неделю.
    """

    week: Dict[date, List[BookingSlot]] = Field(
        description='Словарь с доступными слотами по дням недели',
        example={
            '2023-10-15': [
                {'time': '14:00', 'is_available': True},
                {'time': '14:30', 'is_available': False},
            ]
        },
    )
