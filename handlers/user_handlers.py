from aiogram import Router
from aiogram.filters import Text
from aiogram.types import Message

router = Router()


# Этот хэндлер срабатывает на кодовое слово и присваивает роль методиста
@router.message(Text(text='methodist'))
async def process_start_command(message: Message):
    await message.answer(text='Вы получили права доступа методиста.')


# Этот хэндлер срабатывает на кодовое слово и присваивает роль вожатого
@router.message(Text(text='councelor'))
async def process_start_command(message: Message):
    await message.answer(text='Вы получили права доступа вожатого.')
