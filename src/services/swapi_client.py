"""
src.services.swapi_client

================================================================================
SWAPI Integration Client
================================================================================

Overview
--------
This module provides an asynchronous client for fetching Star Wars data from
the SWAPI (https://swapi.info/api/). It handles network retries, SSL verification,
and structured logging. Supports fetching characters, films, and starships.

Responsibilities
----------------
- Fetch data from SWAPI endpoints
- Handle transient network failures with retry logic
- Log all requests and errors with context

Key Characteristics
--------------------
- Uses async httpx client for non-blocking calls
- Configurable base URL and SSL verification via environment
- Retry with exponential backoff for robustness

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from typing import Any, Dict, Optional

import httpx

from src.config.env import get_app_config
from src.exceptions.custom_exceptions import ExternalAPIError
from src.utils.logger_util import log_error, log_info
from src.utils.retry_util import retry_with_backoff

config = get_app_config()
BASE_URL = config["SWAPI_BASE_URL"]
VERIFY_SSL = config["VERIFY_SWAPI_SSL"]


@retry_with_backoff(retries=5, delay=1.0, max_delay=10.0)
async def fetch_resource(
    endpoint: str, params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Fetch a resource from the SWAPI endpoint with retry and logging.

    Always normalizes the response into a {"results": [...], "next": None} shape.

    :param endpoint: SWAPI endpoint path (e.g. "people/")
    :param params: Query parameters for pagination or filtering
    :return: Parsed JSON response in standard format
    :raises ExternalAPIError: On failed fetch or invalid response
    """
    url = f"{BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    log_info(f"Fetching SWAPI resource: {url}", context={"params": params})

    try:
        async with httpx.AsyncClient(verify=VERIFY_SSL, timeout=10.0) as client:
            response = await client.get(url, params=params, follow_redirects=True)
            response.raise_for_status()

            try:
                data = response.json()
            except Exception as e:
                body = await response.aread()
                log_error(
                    e,
                    function_name="fetch_resource",
                    context={
                        "url": url,
                        "params": params,
                        "body": body.decode(errors="replace"),
                    },
                )
                raise ExternalAPIError(f"Invalid JSON response from SWAPI: {url}")

            if isinstance(data, list):
                log_info(
                    "SWAPI returned a raw list. Normalizing to {'results': list, 'next': None}",
                    context={"url": url},
                )
                return {"results": data, "next": None}

            if isinstance(data, dict):
                return data

            log_error(
                Exception(f"Unexpected JSON type: {type(data)}"),
                function_name="fetch_resource",
                context={"data": data},
            )
            raise ExternalAPIError(f"Unexpected JSON type from SWAPI: {type(data)}")

    except httpx.HTTPStatusError as e:
        log_error(
            e,
            function_name="fetch_resource",
            context={
                "url": url,
                "params": params,
                "status_code": e.response.status_code,
            },
        )
        raise ExternalAPIError(
            f"SWAPI returned HTTP error {e.response.status_code}"
        ) from e

    except httpx.RequestError as e:
        log_error(
            e,
            function_name="fetch_resource",
            context={"url": url, "params": params},
        )
        raise ExternalAPIError(f"SWAPI request failed: {e}") from e

    except Exception as e:
        log_error(
            e,
            function_name="fetch_resource",
            context={"url": url, "params": params},
        )
        raise ExternalAPIError("Unknown error while fetching from SWAPI") from e


async def fetch_characters(page: int = 1) -> Dict[str, Any]:
    """
    Fetch paginated list of characters from SWAPI.

    :param page: Page number to fetch
    :return: JSON response in standard format
    :raises ExternalAPIError: On fetch failure
    """
    return await fetch_resource("people/", params={"page": page})


async def fetch_films() -> Dict[str, Any]:
    """
    Fetch all films from SWAPI.

    :return: JSON response in standard format
    :raises ExternalAPIError: On fetch failure
    """
    return await fetch_resource("films/")


async def fetch_starships(page: int = 1) -> Dict[str, Any]:
    """
    Fetch paginated list of starships from SWAPI.

    :param page: Page number to fetch
    :return: JSON response in standard format
    :raises ExternalAPIError: On fetch failure
    """
    return await fetch_resource("starships/", params={"page": page})
