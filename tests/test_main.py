"""
tests.test_main

================================================================================
Integration Tests for FastAPI Main Application Entry Point
================================================================================

Overview
--------
Tests the FastAPI app defined in `src.main`, verifying that the application
object and key metadata variables are correctly defined. Ensures the root
endpoint (`/`) responds as expected and includes all required metadata fields.

Tested Responsibilities
------------------------
- Sanity check that the FastAPI app and metadata (name, version) are importable
- Verification of the lifespan context via TestClient
- Validation of root endpoint response structure and values
- Ensures availability and correctness of the OpenAPI documentation link

Key Characteristics
--------------------
- Simulates real HTTP requests using FastAPI's TestClient
- Verifies runtime lifecycle behavior, including lifespan startup
- Asserts complete and well-formed service metadata in the root response
- Aligns with production readiness checks for basic service health

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from fastapi.testclient import TestClient

from src import main


def test_app_importable():
    """
    Sanity test that the FastAPI app and metadata are importable.

    :return: Asserts presence of main.app, APP_NAME, and APP_VERSION
    :rtype: None
    """
    assert main.app
    assert main.APP_NAME
    assert main.APP_VERSION


def test_root_endpoint_and_lifespan():
    """
    Integration test for the root ("/") endpoint with lifespan context.

    :return: Asserts successful response with complete service metadata
    :rtype: None
    """
    with TestClient(main.app) as client:
        response = client.get("/")
        assert response.status_code == 200

        json_data = response.json()
        assert "service" in json_data
        assert "version" in json_data
        assert "status" in json_data
        assert "message" in json_data
        assert "documentation" in json_data
        assert "maintainer" in json_data
        assert "website" in json_data

        assert json_data["service"] == main.APP_NAME
        assert json_data["version"] == main.APP_VERSION
        assert json_data["status"] == "online"
        assert "/docs" in json_data["documentation"]
