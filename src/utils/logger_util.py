"""
src.utils.logger_util

================================================================================
Structured Logging Utility with Sensitive Data Redaction
================================================================================

Overview
--------
This module provides a centralized, structured logging utility for the SWAPI Voting API,
ensuring consistent, JSON-formatted logs with integrated sensitive data redaction.

It defines standardized logging functions for error, warning, and informational
messages, enforcing a uniform log schema across all modules while protecting
secrets in context payloads. By handling nested structures safely, it prevents
accidental exposure of credentials, connection strings, or other sensitive
configuration values.

Responsibilities
----------------
- Log messages in structured JSON format with consistent fields
- Support multiple log levels (error, warning, info)
- Automatically include function names and contextual metadata
- Recursively redact sensitive keys and values from context payloads
- Provide centralized, reusable logging for all modules and services

Key Characteristics
--------------------
- Compatible with structured logging pipelines and JSON-based log aggregators
- Defensive, recursive redaction of known sensitive terms from nested structures
- Supports customizable context objects for improved observability
- Configurable logging level via standard Python logging configuration
- Minimal external dependencies, fully standard-library based

Functions
---------
- `log_error(err, function_name=None, context=None)`
  Logs an error message with exception details and optional context, including
  full traceback, redacted as necessary.

- `log_warning(message, function_name=None, context=None)`
  Logs a warning message with optional context, ensuring consistent structure
  and redacted sensitive data.

- `log_info(message, function_name=None, context=None)`
  Logs an informational message with optional context, redacting any
  sensitive information.

- `redact_sensitive_info(data)`
  Recursively processes any data structure, replacing sensitive values
  with placeholders based on a configurable list of known secret keys.

Usage Context
-------------
Intended for use by:
- All service-layer modules performing data fetching or persistence
- Client modules handling database or API connectivity
- Utility modules supporting retry logic with structured logging
- Any component requiring secure, standardized, JSON-formatted logs

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import logging
from json import dumps
from traceback import format_exc
from typing import Any, Dict, Optional, Union

from src.config.constants import SENSITIVE_KEYS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SENSITIVE_KEYS = {key.upper() for key in SENSITIVE_KEYS}


def log_error(
    err: Exception,
    function_name: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Logs an error message in structured JSON format with traceback, ensuring sensitive data is redacted.

    :param err: The exception object.
    :type err: Exception
    :param function_name: The name of the function where the error occurred (optional).
    :type function_name: Optional[str]
    :param context: Additional debugging context (optional, redacted).
    :type context: Optional[Dict[str, Any]]
    """
    error_data = {
        "level": "error",
        "error_type": type(err).__name__,
        "message": str(err),
        "function": function_name or "unknown",
        "context": redact_sensitive_info(context) if context else {},
    }

    trace = format_exc()
    if trace.strip():
        error_data["traceback"] = trace

    logger.error(dumps(error_data))


def log_warning(
    message: str,
    function_name: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Logs a warning message in structured JSON format, ensuring sensitive data is redacted.

    :param message: Warning message.
    :type message: str
    :param function_name: The function where the warning occurred (optional).
    :type function_name: Optional[str]
    :param context: Additional debugging context (optional, redacted).
    :type context: Optional[Dict[str, Any]]
    """
    logger.warning(
        dumps(
            {
                "level": "warning",
                "message": message,
                "function": function_name or "unknown",
                "context": redact_sensitive_info(context) if context else {},
            }
        )
    )


def log_info(
    message: str,
    function_name: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Logs an informational message in structured JSON format, ensuring sensitive data is redacted.

    :param message: Informational message.
    :type message: str
    :param function_name: The function where the log occurred (optional).
    :type function_name: Optional[str]
    :param context: Additional debugging context (optional, redacted).
    :type context: Optional[Dict[str, Any]]
    """
    logger.info(
        dumps(
            {
                "level": "info",
                "message": message,
                "function": function_name or "unknown",
                "context": redact_sensitive_info(context) if context else {},
            }
        )
    )


def redact_sensitive_info(data: Union[Dict[str, Any], list, str, Any]) -> Any:
    """
    Recursively redacts sensitive information from any data structure.

    - Replaces sensitive values with "****" if the key matches known sensitive terms.
    - Handles dictionaries, lists, and other nested structures.

    :param data: The input data that may contain sensitive information.
    :type data: Union[Dict[str, Any], list, str, Any]
    :return: A sanitized version of the input data.
    :rtype: Any
    """
    if isinstance(data, dict):
        return {
            key: (
                "****"
                if key.upper() in SENSITIVE_KEYS
                else redact_sensitive_info(value)
            )
            for key, value in data.items()
        }

    elif isinstance(data, list):
        return [redact_sensitive_info(item) for item in data]

    elif isinstance(data, str):
        return "****" if data.upper() in SENSITIVE_KEYS else data

    return data
