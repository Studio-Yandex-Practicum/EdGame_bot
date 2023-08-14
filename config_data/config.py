from dataclasses import dataclass

from environs import Env


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
