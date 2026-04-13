"""
Pytest configuration and shared fixtures for FastAPI tests.
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Fixture providing a TestClient instance for testing the FastAPI app.
    """
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """
    Fixture providing a deep copy of the activities database.
    Each test gets its own clean copy to avoid state pollution between tests.
    """
    return deepcopy(activities)


@pytest.fixture
def client_with_sample_data(client, sample_activities, monkeypatch):
    """
    Fixture providing a TestClient with sample activities data.
    Uses monkeypatch to replace the app's activities dict with test data.
    """
    monkeypatch.setattr("src.app.activities", sample_activities)
    return client
