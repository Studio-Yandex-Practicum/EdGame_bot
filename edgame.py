import asyncio
import logging
import os
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from config_data.config import load_config
from handlers import counsellor_handlers, user_handlers

logger = logging.getLogger(__name__)


async def main():
    """Функция конфигурирования и запуска бота."""
    # Конфигурируем логирование
    log_dir = os.path.abspath("logs")
    log_filename = os.path.join(log_dir, "bot_logfile.log")
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    rotating_handler = RotatingFileHandler(
        filename=log_filename,
        maxBytes=50000000,
        backupCount=3,
        encoding="utf-8",
    )
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(filename)s:%(lineno)d #%(levelname)-8s "
        "[%(asctime)s] - %(name)s - %(message)s",
        handlers=[rotating_handler],
    )

    # Выводим в консоль информацию о начале запуска бота
    logger.info("Starting bot")

    # Загружаем конфиг в переменную config
    config = load_config()
    print(2)
    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token, parse_mode=ParseMode.HTML)
    print(bot, 3)
    dp = Dispatcher()

    # Регистриуем роутеры в диспетчере и устанавливаем меню
    dp.include_router(user_handlers.router)
    dp.include_router(counsellor_handlers.router)
    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_my_commands()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    logger.info("Bot started!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped!")
