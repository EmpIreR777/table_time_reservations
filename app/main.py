import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from fastapi.staticfiles import StaticFiles


from app.async_client import http_client_manager
from app.core.config import settings, scheduler
from app.core.logger_config import setup_logger
from app.tg_bot.router import router as router_tg_bot


logger = setup_logger(
    log_dir="logs",
    log_file="app_def.log",
    log_level="DEBUG",  # В разработке
    rotation="10 MB",  # Ротация каждые 10 МБ
    retention="30 days",  # Хранить логи 30 дней
)

async def set_webhook(client):
    """Устанавливает вебхук для Telegram-бота."""
    try:
        response = await client.post(
            f'{settings.get_tg_api_url()}/setWebhook', json={'url': settings.get_webhook_url()}
        )
        logger.info(f'Webhook: {settings.get_webhook_url()}')
        response_data = response.json()
        if response.status_code == status.HTTP_200_OK and response_data.get('ok'):
            logger.info(f'Webhook установлен: {response_data}')
        else:
            logger.error(f'Ошибка при установке вебхука: {response_data}')
    except Exception as e:
        logger.exception(f'Не удалось установить вебхук: {e}')


async def send_admin_msg(client, text):
    """Отправляет сообщение администраторам."""
    for admin in settings.ADMIN_IDS:
        try:
            await client.post(
                f'{settings.get_tg_api_url()}/sendMessage', json={'chat_id': admin, 'text': text, 'parse_mode': 'HTML'}
            )
        except Exception as e:
            logger.exception(f'Ошибка при отправке сообщения админу: {e}')


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекстный менеджер для настройки и завершения работы бота."""
    async with http_client_manager.client() as client:  # Используем контекстный менеджер
        logger.info('Настройка бота...')
        scheduler.start()
        await set_webhook(client)
        await client.post(
            f'{settings.get_tg_api_url()}/setMyCommands',
            data={'commands': json.dumps([{'command': 'start', 'description': 'Главное меню'}])},
        )
        await send_admin_msg(client, 'Бот запущен!')
        yield
        logger.info('Завершение работы бота...')
        await send_admin_msg(client, 'Бот остановлен!')
        scheduler.shutdown()


app = FastAPI(lifespan=lifespan)
app.mount('/static', StaticFiles(directory='app/static'), name='static')

# Добавляем middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Разрешаем все источники
    allow_credentials=True,
    allow_methods=['*'],  # Разрешаем все методы
    allow_headers=['*'],  # Разрешаем все заголовки
)

# Подключаем роутеры
app.include_router(bookings_router)
app.include_router(specializations_router)
app.include_router(users_router)
app.include_router(doctors_router)
app.include_router(router_tg_bot)
