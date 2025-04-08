from datetime import datetime, time
# from enum import Enum
from typing import Optional, List
from sqlalchemy import BigInteger, Date, Integer, String, Text, ForeignKey, Time, Enum as SQLEnum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


# class BookingStatus(str, Enum):
#     CONFIRMED = 'ПОДТВЕРЖДЕНО'
#     CANCELLED = 'ОТМЕНЕНО'
#     PENDING = 'ОЖИДАНИЕ'


class User(Base):
    __tablename__ = 'users'

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    first_name: Mapped[str] = mapped_column(Text, nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    bookings: Mapped[List['Booking']] = relationship(back_populates='user', cascade='all, delete-orphan')

    @hybrid_property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name or ""}'.strip()

    def __repr__(self) -> str:
        return f'User(id={self.id}, username={self.username}, full_name={self.full_name})'


class Table(Base):
    __tablename__ = 'tables'

    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    bookings: Mapped[List['Booking']] = relationship(back_populates='table', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'Table(id={self.id}, capacity={self.capacity}, description={self.description})'


class TimeSlot(Base):
    __tablename__ = 'time_slots'

    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    bookings: Mapped[List['Booking']] = relationship(back_populates='time_slot', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'TimeSlot(id={self.id}, {self.start_time.strftime("%H:%M")}-{self.end_time.strftime("%H:%M")})'


class Booking(Base):
    __tablename__ = 'bookings'

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), nullable=False)
    table_id: Mapped[int] = mapped_column(Integer, ForeignKey('tables.id'), nullable=False)
    time_slot_id: Mapped[int] = mapped_column(Integer, ForeignKey('time_slots.id'), nullable=False)
    date: Mapped[datetime] = mapped_column(Date, nullable=False)
    # status: Mapped[BookingStatus] = mapped_column(SQLEnum(BookingStatus), nullable=False)
    status: Mapped[str]

    user: Mapped['User'] = relationship('User', back_populates='bookings')
    table: Mapped['Table'] = relationship('Table', back_populates='bookings')
    time_slot: Mapped['TimeSlot'] = relationship('TimeSlot', back_populates='bookings')

    def __repr__(self) -> str:
        return (
            f'Booking(id={self.id}, user_id={self.user_id}, table_id={self.table_id}, '
            f'time_slot_id={self.time_slot_id}, date={self.date}, status={self.status})'
        )
