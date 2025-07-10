"""
src.config.constants

================================================================================
Global Application Constants
================================================================================

Overview
--------
This module defines fixed, hard-coded constants used throughout the
SWAPI Voting API service. These values are *not* environment-configurable
and are intended to remain stable across deployments.

Includes:
- Pagination limits
- Known sensitive environment variable keys

Usage
-----
Import these values wherever consistent, hard-coded configuration is needed
without relying on environment overrides.

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

MAX_PAGE_SIZE = 100

SENSITIVE_KEYS = {
    "DATABASE_URL",
    "SWAPI_BASE_URL",
    "VERIFY_SWAPI_SSL",
    "DEFAULT_PAGE_SIZE",
    "APP_NAME",
    "APP_VERSION",
}
