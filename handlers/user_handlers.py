from aiogram import Router
from aiogram.filters import Text, CommandStart

from lexicon.lexicon import LEXICON, LEXICON_COMMANDS
from keyboards.keyboards import create_welcome_keyboard
from utils.db_commands import register_user, select_user
from db.engine import session

router = Router()


# Этот хэндлер срабатывает на кодовое слово и присваивает роль методиста
@router.message(Text(text='methodist'))
async def process_methodist_command(message):
    user = select_user(message.chat.id)
    user.role = 'methodist'
    session.add(user)
    session.commit()
    if user.language == 'ru':
        await message.answer(text=LEXICON['RU']['methodist'])
    elif user.language == 'tt':
        await message.answer(text=LEXICON['TT']['methodist'])
    else:
        await message.answer(text=LEXICON['EN']['methodist'])


# Этот хэндлер срабатывает на кодовое слово и присваивает роль вожатого
@router.message(Text(text='councelor'))
async def process_councelor_command(message):
    user = select_user(message.chat.id)
    user.role = 'councelor'
    session.add(user)
    session.commit()
    if user.language == 'ru':
        await message.answer(text=LEXICON['RU']['councelor'])
    elif user.language == 'tt':
        await message.answer(text=LEXICON['TT']['councelor'])
    else:
        await message.answer(text=LEXICON['EN']['councelor'])


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
    if callback.data == 'ru_pressed':
        user.language = 'ru'
        session.add(user)
        session.commit()
        text = LEXICON['RU']['ru_pressed']
    elif callback.data == 'tt_pressed':
        user.language = 'tt'
        session.add(user)
        session.commit()
        text = LEXICON['TT']['tt_pressed']
    else:
        user.language = 'en'
        session.add(user)
        session.commit()
        text = LEXICON['EN']['en_pressed']
    await callback.answer(text=text)
