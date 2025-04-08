import locale
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram_dialog import setup_dialogs
from loguru import logger
from app.tg_bot.booking.dialog import booking_dialog
from app.tg_bot.user.router import router as user_router
from app.tg_bot.admin.router import router as admin_router
from app.core.config import settings
from app.db.database_middleware import DatabaseMiddlewareWithoutCommit, DatabaseMiddlewareWithCommit


bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher(storage=MemoryStorage())


async def set_commands():
    commands = [BotCommand(command='start', description='Старт')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


def set_russian_locale():
    try:
        # Пробуем установить локаль для Windows
        locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')
    except locale.Error:
        try:
            # Пробуем установить локаль для Linux/macOS
            locale.setlocale(locale.LC_TIME, 'ru_RU.utf8')
        except locale.Error:
            # Игнорируем ошибку, если локаль не поддерживается
            pass


async def start_bot():
    set_russian_locale()
    setup_dialogs(dp)
    dp.update.middleware.register(DatabaseMiddlewareWithoutCommit())
    dp.update.middleware.register(DatabaseMiddlewareWithCommit())
    await set_commands()
    dp.include_router(booking_dialog)
    dp.include_router(user_router)
    dp.include_router(admin_router)

    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.send_message(admin_id, f'Я запущен🥳.')
        except:
            pass
    logger.info("Бот успешно запущен.")
