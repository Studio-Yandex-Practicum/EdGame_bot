import logging

from aiogram.types import Message

from data.temp_db import ARTEFACTS

logger = logging.getLogger(__name__)


async def process_photo(message: Message):
    """
    Сохраняем id фото в базу данных. Телеграм может отправить фото по его id.
    """
    try:
        photo_id = message.photo[0].file_id
        user = message.from_user.first_name
        if user not in ARTEFACTS:
            ARTEFACTS[user] = {}
        ARTEFACTS[user]["photo"] = photo_id
        logger.debug(ARTEFACTS)
    except KeyError as err:
        logger.error(f"KeyWord {err}")
    except Exception as err:
        logger.error(f"Ошибка при обработке артефакта с фото: {err}")


async def process_video(message: Message):
    """
    Сохраняем id видео в базу данных. Телеграм может отправить видео по его id.
    """
    try:
        video_id = message.video.file_id
        user = message.from_user.first_name
        if user not in ARTEFACTS:
            ARTEFACTS[user] = {}
        ARTEFACTS[user]["video"] = video_id
        logger.debug(ARTEFACTS)
    except Exception as err:
        logger.error(f"Ошибка при обработке артефакта с video: {err}")


async def process_document(message: Message):
    """
    Сохраняем id файла в базу данных. Телеграм может отправить файл по его id.
    """
    try:
        doc_id = message.document.file_id
        user = message.from_user.first_name
        if user not in ARTEFACTS:
            ARTEFACTS[user] = {}
        ARTEFACTS[user]["document"] = doc_id
        logger.debug(ARTEFACTS)
    except Exception as err:
        logger.error(f"Ошибка при обработке артефакта с document: {err}")


async def process_audio(message: Message):
    """
    Сохраняем id аудио (не путать с голосовым сообщением) в базу данных.
    Телеграм может отправить аудио по его id.
    """
    try:
        audio_id = message.audio.file_id
        user = message.from_user.first_name
        if user not in ARTEFACTS:
            ARTEFACTS[user] = {}
        ARTEFACTS[user]["audio"] = audio_id
        logger.debug(ARTEFACTS)
    except Exception as err:
        logger.error(f"Ошибка при обработке артефакта с audio: {err}")


async def process_voice(message: Message):
    """
    Сохраняем id голосового сообщения в базу данных.
    Телеграм может отправить голосовое по его id.
    """
    try:
        voice_id = message.voice.file_id
        user = message.from_user.first_name
        if user not in ARTEFACTS:
            ARTEFACTS[user] = {}
        ARTEFACTS[user]["voice"] = voice_id
        logger.debug(ARTEFACTS)
    except Exception as err:
        logger.error(f"Ошибка при обработке артефакта с voice: {err}")
