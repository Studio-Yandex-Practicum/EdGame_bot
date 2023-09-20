from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from db.engine import url_object
from db.models import DeclarativeBase

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

url_object = url_object
target_metadata = DeclarativeBase.metadata

engine = engine_from_config(
    context.config.get_section(context.config.config_ini_section),
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,
)

connection = engine.connect()

context.configure(
    connection=connection,
    target_metadata=target_metadata,
)


def run_migrations_offline():
    context.configure(url=url_object)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
