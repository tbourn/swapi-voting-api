"""
src.utils.date_parser_util

================================================================================
Date and Datetime Parsing Utilities for SWAPI Data
================================================================================

Overview
--------
Provides helper functions to safely parse ISO 8601 date and datetime strings
into Python `date` and `datetime` objects, with graceful error logging.

These utilities ensure strict schema compatibility when importing data from
SWAPI, preventing crashes due to format mismatches while retaining clear
traceable logs for invalid inputs.

Responsibilities
----------------
- Parse ISO-formatted date strings into datetime.date
- Parse ISO-formatted datetime strings into datetime.datetime
- Log and handle errors without disrupting bulk imports

Key Characteristics
--------------------
- Centralized date parsing logic for maintainability
- Compatible with Pydantic models expecting date/datetime fields
- Integrated with the project logging system

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from datetime import date, datetime

from src.exceptions.custom_exceptions import DataImportError
from src.utils.logger_util import log_error


def parse_iso_date(date_str: str | None) -> date | None:
    """
    Safely parse an ISO 8601 date string (YYYY-MM-DD) into a datetime.date object.

    :param date_str: ISO date string or None
    :type date_str: str | None
    :return: datetime.date or None if input is invalid or None
    :rtype: date | None
    """
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        log_error(
            DataImportError(f"Invalid date format: {date_str}"),
            function_name="parse_iso_date",
            context={"value": date_str},
        )
        return None


def parse_iso_datetime(datetime_str: str | None) -> datetime | None:
    """
    Safely parse an ISO 8601 datetime string (with optional 'Z') into a datetime.datetime object.

    :param datetime_str: ISO datetime string or None
    :type datetime_str: str | None
    :return: datetime.datetime or None if input is invalid or None
    :rtype: datetime | None
    """
    if not datetime_str:
        return None
    try:
        # Handle potential 'Z' suffix (UTC)
        return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
    except ValueError:
        log_error(
            DataImportError(f"Invalid datetime format: {datetime_str}"),
            function_name="parse_iso_datetime",
            context={"value": datetime_str},
        )
        return None
