"""
migrations.env

================================================================================
Alembic Migration Environment Configuration
================================================================================

Overview
--------
This module defines the Alembic migration environment for the project.
It configures the offline and online migration modes for SQLAlchemy,
including asynchronous database connectivity for online runs.

Responsibilities
----------------
- Load application configuration and database URL
- Configure Alembic context for migrations
- Support both offline (SQL script) and online (async DB) migration modes
- Handle SQLAlchemy metadata for auto-generation

Key Characteristics
--------------------
- Uses SQLAlchemy AsyncEngine for modern async database support
- Supports type comparison during autogenerate
- Isolated migration contexts for offline/online modes

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from src.config.env import get_app_config
from src.database.session import Base
from src.models import character, film, starship  # noqa

# -------------------------------------------------------
# Alembic Config
# -------------------------------------------------------

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

app_config = get_app_config()
target_url = app_config.get("DATABASE_URL")
if target_url:
    config.set_main_option("sqlalchemy.url", target_url)

target_metadata = Base.metadata

# -------------------------------------------------------
# Offline migration
# -------------------------------------------------------


def run_migrations_offline():
    """
    Run Alembic migrations in offline mode.

    This generates SQL scripts without needing a live database connection.
    Ideal for previewing changes or generating deployment SQL.
    """
    context.configure(
        url=target_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# -------------------------------------------------------
# Online migration (async)
# -------------------------------------------------------


def run_migrations_online():
    """
    Run Alembic migrations in online (async) mode.

    This connects to the actual database using SQLAlchemy AsyncEngine
    and applies migrations directly.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async def do_run_migrations():
        """
        Execute asynchronous migration transaction.

        Opens an async connection to the database and runs
        migrations using a synchronous context.
        """
        async with connectable.connect() as connection:
            await connection.run_sync(run_sync_migrations)

    import asyncio

    asyncio.run(do_run_migrations())


def run_sync_migrations(connection):
    """
    Configure Alembic context and run migrations synchronously.

    This sets up the migration context using the provided connection
    and runs migrations within a transaction.

    :param connection: The SQLAlchemy connection to use
    :type connection: sqlalchemy.engine.Connection
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# -------------------------------------------------------
# Entrypoint
# -------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
