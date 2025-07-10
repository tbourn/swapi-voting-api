"""
tests.utils.test_rate_limit_util

================================================================================
Unit Tests for Redis-based Rate Limiting Utility
================================================================================

Overview
--------
Tests the functions in `src.utils.rate_limit_util`, which implement Redis-backed
IP rate limiting and blocking for the API. Validates that Redis operations are
called with correct arguments and that behavior aligns with expected rate limit
semantics.

Tested Responsibilities
------------------------
- `increment_rate`: Increments the request counter with correct expiry for first hit
- `is_blocked_ip`: Checks membership in the blocked IP set
- `block_ip`: Adds an IP to the blocked set
- `unblock_ip`: Removes an IP from the blocked set

Key Characteristics
--------------------
- Mocks Redis client calls with unittest.mock
- Verifies correct Redis key usage and expiry semantics
- Ensures no actual Redis operations are performed during testing

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from unittest import mock

import pytest

import src.utils.rate_limit_util as rate_util


@pytest.fixture
def redis_mock(monkeypatch):
    """
    Pytest fixture that patches the Redis client used in rate_limit_util.

    :param monkeypatch: Pytest built-in fixture for dynamic patching of attributes
    :type monkeypatch: _pytest.MonkeyPatch
    :return: Mocked Redis client object for controlling and asserting Redis calls
    :rtype: unittest.mock.Mock
    """
    r = mock.Mock()
    monkeypatch.setattr(rate_util, "r", r)
    return r


def test_increment_rate_first_call_sets_expiry(redis_mock):
    """
    Tests that increment_rate sets the expiry when counter is first created.

    :param redis_mock: Mocked Redis client with incr and expire methods
    :type redis_mock: unittest.mock.Mock
    :return: None
    :rtype: None
    """
    redis_mock.incr.return_value = 1
    count = rate_util.increment_rate("1.2.3.4", limit_window=123)
    assert count == 1
    redis_mock.incr.assert_called_once_with("rate:1.2.3.4")
    redis_mock.expire.assert_called_once_with("rate:1.2.3.4", 123)


def test_increment_rate_existing_key(redis_mock):
    """
    Tests that increment_rate does not set expiry if key already exists.

    :param redis_mock: Mocked Redis client with incr method
    :type redis_mock: unittest.mock.Mock
    :return: None
    :rtype: None
    """
    redis_mock.incr.return_value = 5
    count = rate_util.increment_rate("5.6.7.8")
    assert count == 5
    redis_mock.incr.assert_called_once_with("rate:5.6.7.8")
    redis_mock.expire.assert_not_called()


def test_is_blocked_ip(redis_mock):
    """
    Tests that is_blocked_ip correctly queries the Redis set for blocked IPs.

    :param redis_mock: Mocked Redis client with sismember method
    :type redis_mock: unittest.mock.Mock
    :return: None
    :rtype: None
    """
    redis_mock.sismember.return_value = True
    assert rate_util.is_blocked_ip("1.2.3.4") is True
    redis_mock.sismember.assert_called_once_with("blocked_ips", "1.2.3.4")


def test_block_ip(redis_mock):
    """
    Tests that block_ip adds the given IP to the Redis blocked set.

    :param redis_mock: Mocked Redis client with sadd method
    :type redis_mock: unittest.mock.Mock
    :return: None
    :rtype: None
    """
    rate_util.block_ip("5.6.7.8")
    redis_mock.sadd.assert_called_once_with("blocked_ips", "5.6.7.8")


def test_unblock_ip(redis_mock):
    """
    Tests that unblock_ip removes the given IP from the Redis blocked set.

    :param redis_mock: Mocked Redis client with srem method
    :type redis_mock: unittest.mock.Mock
    :return: None
    :rtype: None
    """
    rate_util.unblock_ip("9.10.11.12")
    redis_mock.srem.assert_called_once_with("blocked_ips", "9.10.11.12")
