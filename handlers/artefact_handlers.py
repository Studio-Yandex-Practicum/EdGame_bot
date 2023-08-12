import logging

from aiogram.types import Message, InlineKeyboardMarkup, ReplyKeyboardMarkup

from keyboards.methodist_keyboards import art_list_keyboard
from keyboards.keyboards import task_keyboard

logger = logging.getLogger(__name__)


async def process_photo(message: Message):
    '''
    Сохраняем id фото в базу данных. Телеграм может отправить фото по его id.
    '''
    try:
        photo_id = message.photo[0].file_id
    except Exception as err:
        logger.error(f'Ошибка при обработке артефакта с фото: {err}')
