"""
tests.utils.test_logger_util

================================================================================
Unit Tests for Logging Utilities
================================================================================

Overview
--------
Tests the functions in `src.utils.logger_util`, which provide structured logging
with context redaction for sensitive information. Ensures that log outputs
include expected metadata, redact configured keys, and include error tracebacks
when appropriate.

Tested Responsibilities
------------------------
- `redact_sensitive_info`: Masks sensitive fields in dicts, lists, and nested structures
- `log_error`: Logs errors with tracebacks and redacted context
- `log_warning`: Logs warnings with redacted context
- `log_info`: Logs informational messages with redacted context

Key Characteristics
--------------------
- Uses unittest.mock to patch logger configuration and sensitive keys
- Captures in-memory log output via custom logging.Handler
- Validates JSON-formatted log messages for expected fields and redaction

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import logging
from unittest import mock

import pytest

import src.utils.logger_util as logger_util


@pytest.fixture
def log_capture(monkeypatch):
    """
    Pytest fixture that attaches an in-memory log handler to capture log outputs.

    :param monkeypatch: Pytest's monkeypatch fixture for replacing logger configuration
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    :yield: List of captured log message strings emitted during the test
    :rtype: list
    """
    log_records = []

    class DummyHandler(logging.Handler):
        def emit(self, record):
            log_records.append(record.getMessage())

    handler = DummyHandler()
    handler.setLevel(logging.DEBUG)

    root_logger = logger_util.logger
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)

    yield log_records

    root_logger.removeHandler(handler)


def test_redact_sensitive_info_simple(monkeypatch):
    """
    Tests redact_sensitive_info with nested dict input containing sensitive keys.

    :param monkeypatch: Pytest's monkeypatch fixture to override SENSITIVE_KEYS
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    :return: None
    :rtype: None
    """
    monkeypatch.setattr(logger_util, "SENSITIVE_KEYS", {"PASSWORD", "SECRET"})

    input_data = {
        "username": "bob",
        "password": "supersecret",
        "profile": {"secret": "abc123", "age": 30},
    }
    redacted = logger_util.redact_sensitive_info(input_data)
    assert redacted["username"] == "bob"
    assert redacted["password"] == "****"
    assert redacted["profile"]["secret"] == "****"
    assert redacted["profile"]["age"] == 30


def test_redact_sensitive_info_list(monkeypatch):
    """
    Tests redact_sensitive_info with a list of dicts containing sensitive keys.

    :param monkeypatch: Pytest's monkeypatch fixture to override SENSITIVE_KEYS
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    :return: None
    :rtype: None
    """
    monkeypatch.setattr(logger_util, "SENSITIVE_KEYS", {"TOKEN"})
    data = [{"name": "x"}, {"token": "abcd"}]
    redacted = logger_util.redact_sensitive_info(data)
    assert redacted == [{"name": "x"}, {"token": "****"}]


def test_log_error_includes_traceback(log_capture):
    """
    Tests that log_error emits JSON with error level, traceback, and redacted context.

    :param log_capture: Captured log outputs from the custom in-memory handler
    :type log_capture: list
    :return: None
    :rtype: None
    """
    err = ValueError("boom")
    logger_util.log_error(err, function_name="fail_func", context={"api_key": "abcd"})
    output = log_capture[0]
    assert '"level": "error"' in output
    assert '"function": "fail_func"' in output
    assert '"error_type": "ValueError"' in output
    assert '"api_key": "abcd"' in output or '"context":' in output
    assert '"traceback":' in output


def test_log_warning_redacts(log_capture, monkeypatch):
    """
    Tests that log_warning redacts sensitive fields in the context.

    :param log_capture: Captured log outputs from the custom in-memory handler
    :type log_capture: list
    :param monkeypatch: Pytest's monkeypatch fixture to override SENSITIVE_KEYS
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    :return: None
    :rtype: None
    """
    monkeypatch.setattr(logger_util, "SENSITIVE_KEYS", {"API_KEY"})

    context = {"user": "bob", "api_key": "secret"}
    logger_util.log_warning("watch out", function_name="warn_func", context=context)

    out = log_capture[0]
    assert '"level": "warning"' in out
    assert '"function": "warn_func"' in out
    assert '"user": "bob"' in out
    assert '"api_key": "****"' in out


def test_log_info_redacts(log_capture, monkeypatch):
    """
    Tests that log_info redacts sensitive fields in the context.

    :param log_capture: Captured log outputs from the custom in-memory handler
    :type log_capture: list
    :param monkeypatch: Pytest's monkeypatch fixture to override SENSITIVE_KEYS
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    :return: None
    :rtype: None
    """
    monkeypatch.setattr(logger_util, "SENSITIVE_KEYS", {"SECRET"})

    context = {"note": "ok", "secret": "top"}
    logger_util.log_info("all good", function_name="info_func", context=context)

    out = log_capture[0]
    assert '"level": "info"' in out
    assert '"function": "info_func"' in out
    assert '"note": "ok"' in out
    assert '"secret": "****"' in out
