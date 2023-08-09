from aiogram import Router
from aiogram.filters import Text
from aiogram.types import Message

router = Router()

ROLE = {'methodist': [], 'councelor': [], 'kid': []}


# Этот хэндлер срабатывает на кодовое слово и присваивает роль методиста
@router.message(Text(text='methodist'))
async def process_start_command(message: Message):
    ROLE['methodist'].append(message.chat.id)
    await message.answer(text='Вы получили права доступа методиста.')


# Этот хэндлер срабатывает на кодовое слово и присваивает роль вожатого
@router.message(Text(text='councelor'))
async def process_start_command(message: Message):
    ROLE['councelor'].append(message.chat.id)
    await message.answer(text='Вы получили права доступа вожатого.')
