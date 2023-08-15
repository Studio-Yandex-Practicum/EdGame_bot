from aiogram import Router
from aiogram.filters import Text, CommandStart

from lexicon.lexicon import LEXICON, LEXICON_COMMANDS
from keyboards.keyboards import create_welcome_keyboard
from utils.db_commands import register_user, select_user
from db.engine import session

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
    # Сохраняем пользователя в БД, роль по умолчанию 'kid'
    register_user(message)
    await message.answer(
        text=f"{LEXICON_COMMANDS['/start']}",
        reply_markup=create_welcome_keyboard()
    )


# Этот хендлер срабатывает на апдейт CallbackQuery с выбором языка
@router.callback_query(
    Text(text=['ru_pressed', 'tt_pressed', 'en_pressed']))
async def process_buttons_press(callback):
    user = select_user(callback.from_user.id)
    print(user)
    if callback.data == 'ru_pressed':
        user.language = 'ru'
        session.add(user)
        session.commit()
        print(user.language)
        text = LEXICON['RU']['ru_pressed']
    elif callback.data == 'tt_pressed':
        user.language = 'tt'
        session.add(user)
        session.commit()
        print(user.language)
        text = LEXICON['TT']['tt_pressed']
    else:
        user.language = 'en'
        session.add(user)
        session.commit()
        print(user.language)
        text = LEXICON['EN']['en_pressed']
    await callback.answer(text=text)
