from dataclasses import dataclass

from environs import Env

from utils.db_commands import get_all_achievements


@dataclass
class Pagination:
    """
    С помощью этих настроек можно регулировать кол-во
    заданий на одной странице.
    """
    # Количество ачивок на странице ачивок
    page_size: int = 2
    # Количество возможных кнопок
    achievements_num: int = len(get_all_achievements())


@dataclass
class TgBot:
    token: str
    admin_id: int


@dataclass
class Config:
    tg_bot: TgBot


def load_config() -> Config:
    env = Env()
    env.read_env()
    return Config(tg_bot=TgBot(token=env("BOT_TOKEN"), admin_id=int(env("ADMIN_ID"))))
