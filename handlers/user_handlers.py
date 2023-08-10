from aiogram import Router
from aiogram.filters import Text, CommandStart
from lexicon.lexicon import LEXICON_RU
from keyboards.keyboards import welcome_kb

router = Router()

ROLE = {'methodist': {}, 'councelor': {}, 'kid': {}}


# Этот хэндлер срабатывает на кодовое слово и присваивает роль методиста
@router.message(Text(text='methodist'))
async def process_methodist_command(message):
    # Проверяем не получал ли юзер ранее права вожатого
    if message.chat.id not in ROLE['councelor']:
        ROLE['methodist'].append(message.chat.id)
        await message.answer(text='Вы получили права доступа методиста.')
    else:
        await message.answer(text='У вас права доступа вожатого.')


# Этот хэндлер срабатывает на кодовое слово и присваивает роль вожатого
@router.message(Text(text='councelor'))
async def process_councelor_command(message):
    # Проверяем не получал ли юзер ранее права методиста
    if message.chat.id not in ROLE['methodist']:
        ROLE['councelor'].append(message.chat.id)
        await message.answer(text='Вы получили права доступа вожатого.')
    else:
        await message.answer(text='У вас права доступа методиста.')


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message):
    await message.answer(text=LEXICON_RU['/start'], reply_markup=welcome_kb)
