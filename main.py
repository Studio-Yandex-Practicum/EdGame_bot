import logging
import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from config.config import load_config
from handlers.user_handlers import router

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s - %(lineno)d - %(levelname)s - '
               '%(asctime)s - %(name)s - %(funcName)s - %(message)s',
        stream=sys.stdout)
    config = load_config()

    dp = Dispatcher()
    dp.include_router(router)

    logger.info('Запускаем бота!')

    bot = Bot(token=config.bot.token, parse_mode=ParseMode.HTML)

    logger.info('Бот запущен!')
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Бот остановлен!')
