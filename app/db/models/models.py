from datetime import datetime, time, date, timezone
from typing import Optional, List
from sqlalchemy import Integer, Text, ForeignKey, DateTime, text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):

    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    first_name: Mapped[str] = mapped_column(Text, nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    bookings: Mapped[List['Booking']] = relationship(
        back_populates='user', cascade='all, delete-orphan')

    @hybrid_property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    def __repr__(self) -> str:
        return f'User(id={self.id}, username={self.username}, first_name={self.first_name}, last_name={self.last_name})'


class Doctor(Base):

    first_name: Mapped[str] = mapped_column(Text, nullable=False)
    last_name: Mapped[str] = mapped_column(Text, nullable=False)
    patronymic: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    special: Mapped[str] = mapped_column(Text, nullable=False)
    specialization_id: Mapped[int] = mapped_column(
        ForeignKey('specializations.id'), server_default=text('1'), nullable=False
    )
    work_experience: Mapped[int] = mapped_column(Integer, nullable=False)
    experience: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    photo: Mapped[str] = mapped_column(Text, nullable=False)

    bookings: Mapped[List['Booking']] = relationship(
        back_populates='doctor', cascade='all, delete-orphan')
    specialization: Mapped['Specialization'] = relationship(
        'Specialization', back_populates='doctors', lazy='joined')

    def __repr__(self) -> str:
        return f'Doctor(id={self.id}, first_name={self.first_name}, special={self.special})'


class Specialization(Base):
    __tablename__ = 'specializations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(Text, nullable=False)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    specialization: Mapped[str] = mapped_column(Text, nullable=False)

    doctors: Mapped[List['Doctor']] = relationship(
        back_populates='specialization', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'Specialization(id={self.id}, label={self.label}, specialization={self.specialization})'


class Booking(Base):

    doctor_id: Mapped[int] = mapped_column(ForeignKey('doctors.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    day_booking: Mapped[date] = mapped_column(nullable=False)
    time_booking: Mapped[time] = mapped_column(nullable=False)
    booking_status: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    doctor: Mapped['Doctor'] = relationship(back_populates='bookings')
    user: Mapped['User'] = relationship(back_populates='bookings')

    def __repr__(self) -> str:
        return f'Booking(id={self.id}, doctor_id={self.doctor_id}, user_id={self.user_id}, booking_status={self.booking_status})'
