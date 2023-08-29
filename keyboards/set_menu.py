from aiogram import Bot
from aiogram.types import BotCommand

from lexicon.lexicon import BUTTONS


async def set_main_menu(bot: Bot, language: str = 'RU'):
    '''Создаем список с командами и их описанием для кнопки menu.'''
    buttons = BUTTONS[language]
    main_menu_commands = [
        BotCommand(command='/start',
                   description=buttons["start_description"]),
        BotCommand(command='/help',
                   description=buttons["help"]),
        BotCommand(command='/lk',
                   description=buttons["lk"]),
        BotCommand(command='/achievements',
                   description=buttons["available_achievements"]),
        BotCommand(command='/current_achievements',
                   description=buttons["current_achievements"]),
        BotCommand(command='/reviewed_achievements',
                   description=buttons["reviewed_achievements"])
        ]
    await bot.set_my_commands(commands=main_menu_commands)
