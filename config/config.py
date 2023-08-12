import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class TgBot:
    token: str


@dataclass
class Config:
    bot: TgBot


def load_config():
    load_dotenv()
    config = Config(bot=TgBot(token=os.getenv('BOT_TOKEN')))
    return config
