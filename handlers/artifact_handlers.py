import logging

from aiogram.types import Message

from utils.db_commands import send_task

logger = logging.getLogger(__name__)


async def process_artifact(message: Message, achievement_id: int):
    '''
    Достает id из возможных типов сообщения и сохраняет в базе
    информацию об ачивке с новым статусом.
    '''
    user_id = message.from_user.id
    files_id = []
    if message.photo:
        files_id.append(message.photo[0].file_id)
    if message.video:
        files_id.append(message.video.file_id)
    if message.document:
        files_id.append(message.document.file_id)
    if message.voice:
        files_id.append(message.voice.file_id)
    if message.audio:
        files_id.append(message.audio.file_id)
    text = message.text if message.text else message.caption
    try:
        send_task(user_id, achievement_id, files_id, text)
        return True
    except Exception as err:
        logger.error(f'Ошибка при сохранении статуса ачивки в базе: {err}')
        return False
