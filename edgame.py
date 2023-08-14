import logging
import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from config_data.config import load_config
from handlers.user_handlers import router
from keyboards.set_menu import set_main_menu

logger = logging.getLogger(__name__)


async def main():
    '''Функция конфигурирования и запуска бота.'''
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s',
        stream=sys.stdout)
    config = load_config()

    dp = Dispatcher()
    dp.startup.register(set_main_menu)
    dp.include_router(router)

    logger.info('Запускаем бота!')

    bot = Bot(token=config.bot.token, parse_mode=ParseMode.HTML)

    logger.info('Бот запущен!')
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Бот остановлен!')
