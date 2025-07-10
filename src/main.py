"""
================================================================================
src.main

================================================================================
FastAPI Application Entry Point for SWAPI Voting API
================================================================================

Overview
--------
This module defines the production-ready FastAPI application for the
**SWAPI Voting API** microservice.

It configures core middleware, routing, documentation, and lifecycle events
to deliver a secure, maintainable, and performant RESTful API for
importing, storing, and serving Star Wars data.

Purpose
-------
- Import canonical Star Wars data from [SWAPI](https://swapi.info/)
- Store normalized, relational data locally
- Serve resources via a structured, documented REST API
- Provide foundation for search, pagination, and future extensions

Responsibilities
----------------
- Instantiate the FastAPI application with environment-driven settings
- Configure CORS for controlled cross-origin access
- Register all API routes and routers
- Add global exception handlers for consistent error responses
- Integrate IP-based rate limiting and blocklist enforcement
- Enable OpenAPI and ReDoc documentation endpoints
- Handle startup and shutdown events with logging

Key Characteristics
--------------------
- ASGI-compatible for uvicorn/hypercorn deployments
- Environment-configurable settings for flexible deployments
- Redis-backed rate limiting with IP blocklist
- Clean separation of concerns via routers and middleware
- Fully typed, testable, and production-ready

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.exception_handlers import (
    data_import_error_handler,
    database_error_handler,
    external_api_error_handler,
)
from src.api.routes import router
from src.config.env import get_app_config
from src.exceptions.custom_exceptions import (
    DatabaseError,
    DataImportError,
    ExternalAPIError,
)
from src.middleware.rate_limit_middleware import RateLimitAndBlocklistMiddleware
from src.utils.logger_util import log_info

config = get_app_config()
APP_NAME = config.get("APP_NAME", "SWAPI Voting API")
APP_VERSION = config.get("APP_VERSION", "1.0.0")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log_info("SWAPI Voting API application starting up.")
    yield
    log_info("SWAPI Voting API application shutting down.")


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="""
**Overview**  
RESTful API for fetching, storing, and managing Star Wars data from the [SWAPI](https://swapi.info/).

**Purpose**  
Enable voting, exploration, and management of Star Wars characters, films, and starships via an internal tool or frontend client.

**Core Capabilities**  
- Import characters, films, and starships from SWAPI
- Store imported data in a local database
- Retrieve stored records with pagination
- Search records by name or title

**Consumers**  
- Internal management dashboards
- Web or mobile apps using SWAPI Voting API

**Security & Compliance**  
- Public endpoints (no authentication for now)
- CORS enabled (can be restricted in production)
- Intended for internal use and development
""",
    contact={
        "name": "Thomas Bournaveas",
        "url": "https://thomasbournaveas.com",
        "email": "thomas.bournaveas@gmail.com",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    RateLimitAndBlocklistMiddleware,
    max_requests=1000,
    window_seconds=3600,
)

app.include_router(router)
app.add_exception_handler(ExternalAPIError, external_api_error_handler)
app.add_exception_handler(DataImportError, data_import_error_handler)
app.add_exception_handler(DatabaseError, database_error_handler)


@app.get("/", tags=["Root"])
async def root():
    """
    Root health-check and welcome endpoint for SWAPI Voting API.

    :return: JSON response with service metadata and welcome message
    :rtype: dict
    """
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "status": "online",
        "message": (
            "Welcome to the SWAPI Voting API — a FastAPI-powered microservice "
            "for importing, storing, and exploring Star Wars characters, films, and starships. "
            "Visit /docs for interactive documentation."
        ),
        "documentation": "/docs",
        "maintainer": "Thomas Bournaveas",
        "website": "https://thomasbournaveas.com",
    }
