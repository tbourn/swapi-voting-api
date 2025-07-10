"""
tests.config.test_env

================================================================================
Unit Tests for Environment Variable Parsing and App Config
================================================================================

Overview
--------
Tests the `src.config.env` module's logic for reading and validating environment
variables used to configure the SWAPI Voting API.

Tested Responsibilities
------------------------
- Required environment variables raise errors when missing
- Optional variables return defaults or empty strings when missing
- Boolean coercion of VERIFY_SWAPI_SSL from various string forms
- Overall configuration object composition with default and custom values

Key Characteristics
--------------------
- Uses pytest's monkeypatch fixture to control environment variables
- Validates defaults, required enforcement, and type coercion
- Simulates both minimal and custom user-defined environment setups
- Ensures consistent and predictable behavior of application configuration

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import os

import pytest

from src.config import env


def test_get_env_var_required_present(monkeypatch):
    """
    Tests that a required environment variable returns its value when present.

    :param monkeypatch: Pytest fixture to set environment variables
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    :raises AssertionError: If the retrieved value is incorrect
    :return: None
    :rtype: None
    """
    monkeypatch.setenv("MY_REQUIRED_VAR", "value")
    assert env.get_env_var("MY_REQUIRED_VAR") == "value"


def test_get_env_var_required_missing_raises(monkeypatch):
    """
    Tests that missing required environment variables raise EnvironmentError.

    :param monkeypatch: Pytest fixture to delete environment variables
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    :raises EnvironmentError: If required variable is missing
    :return: None
    :rtype: None
    """
    monkeypatch.delenv("MISSING_VAR", raising=False)
    with pytest.raises(EnvironmentError) as e:
        env.get_env_var("MISSING_VAR")
    assert "Missing required environment variable" in str(e.value)


def test_get_env_var_optional_present(monkeypatch):
    """
    Tests that an optional environment variable returns its value when present.

    :param monkeypatch: Pytest fixture to set environment variables
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    :raises AssertionError: If the value does not match expectation
    :return: None
    :rtype: None
    """
    monkeypatch.setenv("OPTIONAL_VAR", "present")
    val = env.get_env_var("OPTIONAL_VAR", required=False, default="default")
    assert val == "present"


def test_get_env_var_optional_missing_with_default(monkeypatch):
    """
    Tests that missing optional variable returns provided default value.

    :param monkeypatch: Pytest fixture to delete environment variables
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    :raises AssertionError: If default value is not returned
    :return: None
    :rtype: None
    """
    monkeypatch.delenv("OPTIONAL_VAR", raising=False)
    val = env.get_env_var("OPTIONAL_VAR", required=False, default="default")
    assert val == "default"


def test_get_env_var_optional_missing_no_default(monkeypatch):
    """
    Tests that missing optional variable with no default returns empty string.

    :param monkeypatch: Pytest fixture to delete environment variables
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    :raises AssertionError: If returned value is not an empty string
    :return: None
    :rtype: None
    """
    monkeypatch.delenv("OPTIONAL_VAR", raising=False)
    val = env.get_env_var("OPTIONAL_VAR", required=False)
    assert val == ""


@pytest.mark.parametrize(
    "ssl_value,expected",
    [
        ("true", True),
        ("True", True),
        ("1", True),
        ("yes", True),
        ("false", False),
        ("0", False),
        ("no", False),
    ],
)
def test_get_app_config_verify_ssl_coercion(monkeypatch, ssl_value, expected):
    """
    Tests VERIFY_SWAPI_SSL environment variable coercion from various string forms.

    :param monkeypatch: Pytest fixture to set environment variables
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    :param ssl_value: String value to coerce
    :type ssl_value: str
    :param expected: Expected boolean result
    :type expected: bool
    :raises AssertionError: If coercion result is incorrect
    :return: None
    :rtype: None
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    monkeypatch.setenv("UPSTASH_REDIS_URL", "redis://")
    monkeypatch.setenv("VERIFY_SWAPI_SSL", ssl_value)
    config = env.get_app_config()
    assert config["VERIFY_SWAPI_SSL"] is expected


def test_get_app_config_all_defaults(monkeypatch):
    """
    Tests get_app_config returns correct defaults when optional vars are missing.

    :param monkeypatch: Pytest fixture to set/delete environment variables
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    :raises AssertionError: If defaults are incorrect
    :return: None
    :rtype: None
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    monkeypatch.setenv("UPSTASH_REDIS_URL", "redis://")
    monkeypatch.delenv("SWAPI_BASE_URL", raising=False)
    monkeypatch.delenv("VERIFY_SWAPI_SSL", raising=False)
    monkeypatch.delenv("DEFAULT_PAGE_SIZE", raising=False)
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("APP_VERSION", raising=False)

    config = env.get_app_config()

    assert config["DATABASE_URL"] == "sqlite://"
    assert config["UPSTASH_REDIS_URL"] == "redis://"
    assert config["SWAPI_BASE_URL"] == "https://swapi.info/api/"
    assert config["VERIFY_SWAPI_SSL"] is True
    assert config["DEFAULT_PAGE_SIZE"] == 20
    assert config["APP_NAME"] == "SWAPI Voting API"
    assert config["APP_VERSION"] == "1.0.0"


def test_get_app_config_with_custom_values(monkeypatch):
    """
    Tests get_app_config returns overridden values from custom environment variables.

    :param monkeypatch: Pytest fixture to set environment variables
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    :raises AssertionError: If returned config does not match custom values
    :return: None
    :rtype: None
    """
    monkeypatch.setenv("DATABASE_URL", "postgres://")
    monkeypatch.setenv("UPSTASH_REDIS_URL", "redis://")
    monkeypatch.setenv("SWAPI_BASE_URL", "https://custom-swapi.com/api/")
    monkeypatch.setenv("VERIFY_SWAPI_SSL", "false")
    monkeypatch.setenv("DEFAULT_PAGE_SIZE", "50")
    monkeypatch.setenv("APP_NAME", "Custom SWAPI")
    monkeypatch.setenv("APP_VERSION", "2.0.0")

    config = env.get_app_config()

    assert config["DATABASE_URL"] == "postgres://"
    assert config["UPSTASH_REDIS_URL"] == "redis://"
    assert config["SWAPI_BASE_URL"] == "https://custom-swapi.com/api/"
    assert config["VERIFY_SWAPI_SSL"] is False
    assert config["DEFAULT_PAGE_SIZE"] == 50
    assert config["APP_NAME"] == "Custom SWAPI"
    assert config["APP_VERSION"] == "2.0.0"
