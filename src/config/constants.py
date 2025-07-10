"""
src.config.constants

================================================================================
Global Application Constants
================================================================================

Overview
--------
This module defines true, hard-coded constants used throughout the
SWAPI Voting API service. These values are not environment-configurable
and are intended to be stable across deployments.

Use these for:
- Default HTTP headers
- Service identification
- Internal timeouts
- Standard pagination parameter names

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

USER_AGENT = "SWAPI-Voting-Service/1.0"

SWAPI_REQUEST_TIMEOUT = 10  # seconds

DEFAULT_LIMIT_PARAM = "limit"
DEFAULT_OFFSET_PARAM = "offset"
MAX_PAGE_SIZE = 100

CONTENT_TYPE_JSON = "application/json"

DATE_FORMAT = "%Y-%m-%d"

SENSITIVE_KEYS = {
    "DATABASE_URL",
    "SWAPI_BASE_URL",
    "VERIFY_SWAPI_SSL",
    "DEFAULT_PAGE_SIZE",
    "APP_NAME",
    "APP_VERSION",
}
