"""
src.utils.rate_limit_util

================================================================================
IP-Based Rate Limiting and Blocklist Utility for SWAPI Voting API
================================================================================

Overview
--------
Centralized utility module for managing per-IP rate limiting and IP blocklists
using Upstash Redis. Supports:

- Incrementing request counters with TTL windows
- Enforcing global IP-based request limits
- Managing a persistent blocklist set in Redis

Responsibilities
----------------
- Define helpers to increment per-IP counters with expiration
- Provide blocklist management for banning/unbanning IPs
- Integrate with middleware for rate limit and blocklist enforcement

Key Characteristics
--------------------
- Uses Redis (Upstash) as a scalable backing store
- TTL-based counters for precise sliding-window limits
- Simple set-based blocklist
- Centralized configuration via env loader

Usage Context
-------------
Typically used by FastAPI middleware:

Example:
    from src.utils.rate_limit_util import increment_rate, is_blocked_ip

    if is_blocked_ip(ip):
        # block request

    count = increment_rate(ip)
    if count > limit:
        # rate limit response

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import redis

from src.config.env import get_app_config

config = get_app_config()
r = redis.from_url(config["UPSTASH_REDIS_URL"])


# -----------------------------------------------------------------------------
# Rate limit logic
# -----------------------------------------------------------------------------
def increment_rate(ip: str, limit_window: int = 3600) -> int:
    """
    Increment the request counter for a given IP with expiration.

    :param ip: Client IP address.
    :type ip: str
    :param limit_window: Window in seconds before the counter resets, defaults to 3600
    :type limit_window: int, optional
    :return: Updated count of requests from this IP in the window.
    :rtype: int
    """
    key = f"rate:{ip}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, limit_window)
    return count


# -----------------------------------------------------------------------------
# Blocklist logic
# -----------------------------------------------------------------------------
def is_blocked_ip(ip: str) -> bool:
    """
    Check if an IP address is currently in the Redis blocklist.

    :param ip: Client IP address.
    :type ip: str
    :return: True if the IP is blocked; False otherwise.
    :rtype: bool
    """
    return r.sismember("blocked_ips", ip)


def block_ip(ip: str):
    """
    Add an IP address to the persistent Redis blocklist.

    :param ip: IP address to block.
    :type ip: str
    :return: None
    :rtype: None
    """
    r.sadd("blocked_ips", ip)


def unblock_ip(ip: str):
    """
    Remove an IP address from the Redis blocklist.

    :param ip: IP address to unblock.
    :type ip: str
    :return: None
    :rtype: None
    """
    r.srem("blocked_ips", ip)
