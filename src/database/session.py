"""
src.database.session

================================================================================
Async SQLAlchemy Database Engine and Session
================================================================================

Overview
--------
This module defines the application's async database engine and session factory
using SQLAlchemy 2.0 style. It reads the DATABASE_URL from environment variables
and provides a dependency-compatible async session generator for FastAPI.

Responsibilities
----------------
- Configure the async SQLAlchemy engine with environment-provided DATABASE_URL
- Create an async sessionmaker bound to the engine
- Provide FastAPI-compatible dependency to yield an async DB session

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from src.config.env import get_app_config

config = get_app_config()
DATABASE_URL = config["DATABASE_URL"]

if DATABASE_URL.startswith("sqlite:///"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    future=True,
)

async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to provide an async-scoped SQLAlchemy session.

    This generator ensures that the session lifecycle is properly managed
    per-request. It automatically handles committing, rolling back, and
    closing the session in an async context.

    :yields: An active AsyncSession for interacting with the database.
    :rtype: AsyncGenerator[AsyncSession, None]
    """
    async with async_session() as session:
        yield session
