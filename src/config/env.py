"""
src.config.env

================================================================================
Centralized Environment Variable Loader - Function-Based Access
================================================================================

Overview
--------
This module centralizes secure, consistent loading of environment variables
needed by the SWAPI Voting API, using lazy, function-based accessors instead
of module-level constants.

By encapsulating environment access in dedicated functions, it ensures:
- Strict validation of required variables
- Support for optional/default values
- Avoidance of import-time environment reads
- Improved testability and flexibility

Responsibilities
----------------
- Define `get_env_var()` for safe environment variable retrieval with validation.
- Provide grouped configuration accessors returning dictionaries:
  - `get_app_config()` for all deployment-scoped settings used by the API.

Key Characteristics
--------------------
- Lazy evaluation: environment variables are read only when needed.
- Raises explicit errors if required variables are missing.
- Supports optional/default values via `get_env_var()`.
- Centralizes environment management for consistent, secure configuration.

Usage Context
-------------
Call these accessors wherever environment-driven configuration is needed:

Example:
    >>> from src.config.env import get_app_config
    >>> config = get_app_config()
    >>> db_url = config["DATABASE_URL"]

Intended for use by:
- Database connection setup
- External API clients (e.g., SWAPI integration)
- Application initialization and settings management

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def get_env_var(name: str, required: bool = True, default: Optional[str] = None) -> str:
    """
    Retrieve a single environment variable with optional default and strict validation.

    This function ensures that required environment variables are present,
    supports defaults for optional variables, and enforces consistent reading
    from the environment at runtime.

    :param name: The name of the environment variable.
    :type name: str
    :param required: Whether the variable is mandatory. If True and missing, raises an error.
    :type required: bool
    :param default: Optional fallback value if the variable is not found.
    :type default: Optional[str]
    :raises EnvironmentError: If required is True and the variable is missing.
    :return: The resolved environment variable value.
    :rtype: str
    """
    value = os.getenv(name, default)
    if required and value is None:
        raise EnvironmentError(f"Missing required environment variable: {name}")
    return value if value is not None else ""


def get_app_config() -> dict:
    """
    Load and return the application's configuration as a dictionary.

    This function aggregates all relevant environment variables into a single
    dictionary, applying type conversions and defaults as necessary.

    Configuration keys include:
    - DATABASE_URL: Required database connection URL.
    - SWAPI_BASE_URL: Optional, with default.
    - VERIFY_SWAPI_SSL: Optional, coerced to bool.
    - DEFAULT_PAGE_SIZE: Optional, coerced to int.
    - APP_NAME: Optional, with default.
    - APP_VERSION: Optional, with default.
    - UPSTASH_REDIS_URL: Required.

    :return: A dictionary containing the application's configuration values.
    :rtype: dict
    """
    return {
        "DATABASE_URL": get_env_var("DATABASE_URL"),
        "SWAPI_BASE_URL": get_env_var(
            "SWAPI_BASE_URL", required=False, default="https://swapi.info/api/"
        ),
        "VERIFY_SWAPI_SSL": get_env_var(
            "VERIFY_SWAPI_SSL", required=False, default="True"
        ).lower()
        in ("true", "1", "yes"),
        "DEFAULT_PAGE_SIZE": int(
            get_env_var("DEFAULT_PAGE_SIZE", required=False, default="20")
        ),
        "APP_NAME": get_env_var("APP_NAME", required=False, default="SWAPI Voting API"),
        "APP_VERSION": get_env_var("APP_VERSION", required=False, default="1.0.0"),
        "UPSTASH_REDIS_URL": get_env_var("UPSTASH_REDIS_URL"),
    }
