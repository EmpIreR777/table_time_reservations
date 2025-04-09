import os
from typing import List
from dotenv import load_dotenv

from urllib.parse import quote
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from faststream.rabbit import RabbitBroker
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


env_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '.env')

load_dotenv(env_file_path, override=True)


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: List[int]

    DATABASE_URL: str
    STORE_URL: str

    BASE_URL: str
    RABBITMQ_USERNAME: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    VHOST: str

    model_config = SettingsConfigDict(env_file=env_file_path)

    @property
    def get_rabbitmq_url(self) -> str:
        """Возвращаем URL RabbitMQ."""
        return f'amqp://{quote(self.RABBITMQ_USERNAME)}:{quote(self.RABBITMQ_PASSWORD)}@' + \
               f'{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/{quote(self.VHOST)}'

    @property
    def get_database_url(self) -> str:
        """Возвращает путь к базе данных"""
        return self.DATABASE_URL

    @property
    def get_webhook_url(self) -> str:
        """Возвращаем URL вебхука."""
        return f'{self.BASE_URL}/webhook'


# Инициализация конфигурации
settings = Settings()

# Создание брокера сообщений RabbitMQ
broker = RabbitBroker(url=settings.get_rabbitmq_url)

# Создание планировщика задач
scheduler = AsyncIOScheduler(
    jobstores={'default': SQLAlchemyJobStore(url=settings.STORE_URL)
               })
