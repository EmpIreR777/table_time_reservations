from contextlib import asynccontextmanager
from app.core.logger_config import setup_logger
from app.tg_bot.create_bot import dp, start_bot, bot, stop_bot
from app.core.config import settings, broker, scheduler
from aiogram.types import Update
from fastapi import FastAPI, Request

from app.api.router import disable_booking


logger = setup_logger(
    log_dir='logs',
    log_file='app_def.log',
    log_level='DEBUG',  # В разработке
    rotation='10 MB',  # Ротация каждые 10 МБ
    retention='30 days',  # Хранить логи 30 дней
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Бот запущен...')
    await start_bot()
    try:
        await broker.start()
    except Exception as e:
        logger.error(f'Не удалось подключиться к RabbitMQ: {e}')
        raise
    scheduler.start()
    scheduler.add_job(
        disable_booking,
        trigger='interval',
        minutes=30,
        id='disable_booking_task',
        replace_existing=True
    )
    webhook_url = settings.get_webhook_url
    await bot.set_webhook(url=webhook_url,
                          allowed_updates=dp.resolve_used_update_types(),
                          drop_pending_updates=True)
    logger.success(f'Вебхук установлен: {webhook_url}')
    yield
    logger.info('Бот остановлен...')
    await stop_bot()
    await broker.close()
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

@app.post('/webhook')
async def webhook(request: Request) -> None:
    logger.info('Получен запрос с вебхука.')
    try:
        update_data = await request.json()
        update = Update.model_validate(update_data, context={'bot': bot})
        await dp.feed_update(bot, update)
        logger.info('Обновление успешно обработано.')
    except Exception as e:
        logger.error(f'Ошибка при обработке обновления с вебхука: {e}')


