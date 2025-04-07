"""
Настройка логгера для приложения с использованием loguru.
Поддерживает:
- Вывод в консоль (форматированный, с цветами)
- Запись в файл с ротацией
- Перехват стандартных логов Python (logging)
- Отключение ненужных логов (например, uvicorn.access)
"""

import sys
import logging
import os
from pathlib import Path
from loguru import logger, Logger


class InterceptHandler(logging.Handler):
    """
    Перехватчик стандартных логов Python.
    Перенаправляет логи из модуля logging в loguru.
    Это нужно, чтобы все логи в приложении имели единый формат.
    """

    def emit(self, record):
        try:
            # Получаем уровень лога из record
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Находим нужный кадр в стеке вызовов
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # Логируем сообщение с учетом глубины стека и исключений
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logger(
    log_dir: str = "logs",
    log_file: str = "app.log",
    log_level: str = "INFO",
    rotation: str = "100 MB",
    retention: str = "7 days",
    ) -> Logger:
    """
    Настройка логгера для приложения.

    Параметры:
    - log_dir: Директория для хранения логов
    - log_file: Имя файла логов
    - log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
    - rotation: Правило ротации логов (например, "100 MB" или "1 week")
    - retention: Правило хранения логов (например, "7 days")
    """

    # Удаляем стандартные обработчики loguru
    logger.remove()

    # Создаем директорию для логов, если её нет
    Path(log_dir).mkdir(exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    # 1. Настройка вывода в КОНСОЛЬ
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,  # Цветной вывод
        enqueue=True,  # Асинхронная запись (thread-safe)
        backtrace=True,  # Поддержка traceback
    )

    # 2. Настройка записи в ФАЙЛ с ротацией
    logger.add(
        log_path,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level,
        rotation=rotation,  # Ротация по размеру или времени
        retention=retention,  # Хранение логов
        enqueue=True,
        compression="zip",  # Сжатие старых логов
    )

    # 3. Перехват стандартных логов Python
    logging.basicConfig(
        handlers=[InterceptHandler()], level=log_level, force=True  # Перезаписываем существующие обработчики
    )

    # 4. Отключаем ненужные логи
    logging.getLogger("uvicorn.access").disabled = True  # Доступы Uvicorn
    logging.getLogger("uvicorn.error").setLevel(log_level)  # Ошибки Uvicorn

    return logger