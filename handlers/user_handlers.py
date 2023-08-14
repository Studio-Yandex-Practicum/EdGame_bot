from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.filters import Text, CommandStart
from lexicon.lexicon import LEXICON_RU, LEXICON_TATAR, LEXICON_EN, \
    LEXICON_COMMANDS
from keyboards.keyboards import create_welcome_keyboard

router = Router()
ROLE = {'methodist': {}, 'councelor': {}, 'kid': {}}


# Этот хэндлер срабатывает на кодовое слово и присваивает роль методиста
@router.message(Text(text='methodist'))
async def process_methodist_command(message):
    # Проверяем не получал ли юзер ранее права вожатого
    if message.chat.id in ROLE['councelor']:
        await message.answer(text='У вас права доступа вожатого.')
    # Проверяем получал ли юзер права доступа ребенка, если да, то переносим id в права доступа методиста
    else:
        user_name = message.chat.first_name
        if message.chat.id in ROLE['kid']:
            user_name = ROLE['kid'][message.chat.id]
            del ROLE['kid'][message.chat.id]
        ROLE['methodist'][message.chat.id] = user_name
        await message.answer(text='Вы получили права доступа методиста.')


# Этот хэндлер срабатывает на кодовое слово и присваивает роль вожатого
@router.message(Text(text='councelor'))
async def process_councelor_command(message):
    # Проверяем не получал ли юзер ранее права методиста
    if message.chat.id in ROLE['methodist']:
        await message.answer(text='У вас права доступа методиста.')
    # Проверяем получал ли юзер права доступа ребенка, если да, то переносим id в права доступа методиста
    else:
        user_name = message.chat.first_name
        if message.chat.id in ROLE['kid']:
            user_name = ROLE['kid'][message.chat.id]
            del ROLE['kid'][message.chat.id]
        ROLE['councelor'][message.chat.id] = user_name
        await message.answer(text='Вы получили права доступа вожатого.')


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message):
    # Сохраняем имя пользователя
    ROLE['kid'][message.chat.id] = message.chat.first_name
    await message.answer(
        text=f"{LEXICON_COMMANDS['/start']}",
        reply_markup=create_welcome_keyboard()
    )


# Этот хендлер срабатывает на апдейт CallbackQuery с выбором языка
@router.callback_query(
    Text(text=['rus_lang_pressed', 'tatar_lang_pressed', 'eng_lang_pressed']))
async def process_buttons_press(callback):
    if callback.data == 'rus_lang_pressed':
        text = LEXICON_RU['rus_lang_pressed']
    elif callback.data == 'tatar_lang_pressed':
        text = LEXICON_TATAR['tatar_lang_pressed']
    else:
        text = LEXICON_EN['eng_lang_pressed']
    await callback.answer(text=text)
