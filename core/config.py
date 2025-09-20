from pydantic_settings import BaseSettings
import logging
import sys


class Settings(BaseSettings):
    DATABASE_URL: str
    DB_ECHO: bool
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

import logging
import sys

def setup_logging():
    """
    Настройка логирования для приложения.
    """
    # Создаем форматтер для логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Создаем обработчик для вывода в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    # Настраиваем логгеры для наших модулей
    loggers = [
        'repositories.users',
        'repositories.organizers',
        'services.user_service',
        'services.organizer_service',
        'core.auth.password'
    ]

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        # Убираем дублирование логов
        logger.propagate = False
        logger.addHandler(console_handler) 