"""
src.utils.retry_util

================================================================================
General-Purpose Retry Decorator with Exponential Backoff
================================================================================

Overview
--------
This utility module defines a flexible, production-grade retry decorator
with exponential backoff logic. It is designed to wrap both synchronous and
asynchronous functions seamlessly, providing a unified approach to handling
transient network failures and other recoverable exceptions.

The decorator enforces consistent error handling and structured logging
across the codebase, reducing duplication and simplifying robust retry
strategies in external API integrations or database calls.

Responsibilities
----------------
- Implement an exponential backoff retry strategy for network-related errors
- Support both synchronous and asynchronous function signatures transparently
- Log all retry attempts, delays, and final failures with structured context
- Provide configurable parameters for tuning retry behavior

Key Characteristics
--------------------
- Handles common network exception types (ConnectionError, TimeoutError, RequestException)
- Exponential backoff with configurable initial delay and maximum delay
- Graceful fallback behavior with final logging upon failure
- Defensive error handling for both sync and async workflows
- Fully reusable across service, client, and integration layers

Function
--------
- `retry_with_backoff(retries=5, delay=1.0, max_delay=30.0)`
  Returns a decorator that wraps a target function with retry logic,
  applying exponential backoff between attempts and logging all retries.

Usage Context
-------------
Intended for use by:
- HTTP or API client modules with intermittent network errors
- Database access layers with transient connectivity issues
- External integration services needing robust retry behavior
- Any function requiring standardized, configurable retry with backoff

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import asyncio
import time
from functools import wraps
from typing import Any, Callable

from requests.exceptions import RequestException

from src.utils.logger_util import log_error, log_warning


def retry_with_backoff(retries: int = 5, delay: float = 1.0, max_delay: float = 30.0):
    """
    Decorator for retrying a function with exponential backoff on network-related failures.

    Supports both synchronous and asynchronous functions.

    :param retries: Number of retry attempts, defaults to 5.
    :type retries: int, optional
    :param delay: Initial delay in seconds, defaults to 1.0.
    :type delay: float, optional
    :param max_delay: Maximum delay between retries, defaults to 30.0 seconds.
    :type max_delay: float, optional
    :return: The function result or None if it failed.
    :rtype: Any
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        is_async = asyncio.iscoroutinefunction(fn)
        network_errors = (
            ConnectionError,
            TimeoutError,
            RequestException,
        )

        @wraps(fn)
        async def async_wrapper(*args, **kwargs) -> Any:
            function_name = fn.__name__
            for attempt in range(1, retries + 1):
                try:
                    return await fn(*args, **kwargs)
                except network_errors as e:
                    if attempt == retries:
                        log_error(
                            e,
                            function_name=function_name,
                            context={"attempts": attempt},
                        )
                        return None

                    wait_time = min(delay * (2**attempt), max_delay)
                    log_warning(
                        f"Network error in '{function_name}' (attempt {attempt}/{retries}). Retrying in {wait_time:.2f} seconds...",
                        context={
                            "error": str(e),
                            "attempt": attempt,
                            "next_wait": wait_time,
                        },
                    )
                    await asyncio.sleep(wait_time)

                except Exception as e:
                    log_error(
                        e,
                        function_name=function_name,
                        context={"attempts": attempt},
                    )
                    return None

        @wraps(fn)
        def sync_wrapper(*args, **kwargs) -> Any:
            function_name = fn.__name__
            for attempt in range(1, retries + 1):
                try:
                    return fn(*args, **kwargs)
                except network_errors as e:
                    if attempt == retries:
                        log_error(
                            e,
                            function_name=function_name,
                            context={"attempts": attempt},
                        )
                        return None

                    wait_time = min(delay * (2**attempt), max_delay)
                    log_warning(
                        f"Network error in '{function_name}' (attempt {attempt}/{retries}). Retrying in {wait_time:.2f} seconds...",
                        context={
                            "error": str(e),
                            "attempt": attempt,
                            "next_wait": wait_time,
                        },
                    )
                    time.sleep(wait_time)

                except Exception as e:
                    log_error(
                        e,
                        function_name=function_name,
                        context={"attempts": attempt},
                    )
                    return None

        return async_wrapper if is_async else sync_wrapper

    return decorator
