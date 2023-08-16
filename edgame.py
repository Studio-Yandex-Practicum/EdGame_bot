import asyncio
import logging

from aiogram import Bot, Dispatcher

from config_data.config import load_config
from handlers import counselor_handlers, user_handlers
from keyboards.set_menu import set_main_menu

# Инициализируем логгер
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s "
        "[%(asctime)s] - %(name)s - %(message)s",
    )

    # Выводим в консоль информацию о начале запуска бота
    logger.info("Starting bot")

    # Загружаем конфиг в переменную config
    config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    dp = Dispatcher()

    # Регистриуем роутеры в диспетчере и устанавливаем меню
    # dp.startup.register(set_main_menu) и устанавливаем меню
    # dp.startup.register(set_main_menu)
    dp.include_router(user_handlers.router)
    dp.include_router(counselor_handlers.router)
    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
