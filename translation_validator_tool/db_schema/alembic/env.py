import sys
import os

# Add the api directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'api'))
# Ensure environment variables from the API .env are loaded before importing the app
try:
    # python-dotenv is in requirements; if available, use it to load the .env file
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'api', '.env'))
except Exception:
    # If python-dotenv isn't available, silently continue; Settings will try other sources
    pass

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import your models here
from app.database import Base
from app.models import user, translation, validation, suggestion

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    """Get database URL from config or environment."""
    import os
    from app.config import settings
    
    # Try to get from environment first, then from settings
    url = os.getenv("DATABASE_URL")
    if not url:
        try:
            url = settings.DATABASE_URL
        except Exception:
            # Fallback URL for initial setup
            url = "postgresql://user:password@localhost:5432/translation_validator"
    
    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Enable detailed autogenerate comparisons so Alembic detects
        # type changes and server_default changes.
        def _process_revision_directives(context, revision, directives):
            # If autogenerate produced an empty migration, don't create a file
            if getattr(config.cmd_opts, 'autogenerate', False):
                script = directives[0]
                if not script.upgrade_ops.is_empty():
                    return
                # If empty, clear directives to prevent creating an empty revision
                directives[:] = []

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            process_revision_directives=_process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()