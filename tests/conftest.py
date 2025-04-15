"""Pytest configuration file for setting up fixtures."""

from unittest.mock import AsyncMock, patch  # For mocking async functions

import pytest
from fastapi.testclient import TestClient

# Placeholder for Supabase client mock
# from supabase_py_async import AsyncClient
# Import the dependency to override and the service functions to mock
from app.core.security import get_current_user_id

# Placeholder for the main FastAPI app instance
# We'll need to import it from app.main or similar
from app.main import app  # Assuming app is defined in app/main.py

# from app.services import key_service # No longer mocking whole service
from app.models.key import APIKeyMetaOut  # Import the output model

TEST_USER_ID = "test-user-123"


@pytest.fixture(scope="module")
def mock_auth():
    """Override the get_current_user_id dependency for testing."""
    app.dependency_overrides[get_current_user_id] = lambda: TEST_USER_ID
    yield
    # Clear overrides after tests
    app.dependency_overrides = {}


@pytest.fixture(scope="module")
def test_client(mock_auth) -> TestClient: # Add mock_auth dependency
    """Provide a FastAPI TestClient instance with auth override."""
    client = TestClient(app)
    return client


@pytest.fixture
def mock_store_api_key() -> AsyncMock:
    """Mock the key_service.store_api_key function."""
    with patch("app.api.endpoints.keys.store_api_key", new_callable=AsyncMock) as mock:
        yield mock

@pytest.fixture
def mock_list_api_keys() -> AsyncMock:
    """Mock the key_service.list_api_keys function."""
    with patch("app.api.endpoints.keys.list_api_keys", new_callable=AsyncMock) as mock:
        # Example return value
        mock.return_value = [
            APIKeyMetaOut(
                id="key1", service="openai", created_at="t1", last_used_at="t2"
            ),
            APIKeyMetaOut(
                id="key2", service="anthropic", created_at="t3", last_used_at="t4"
            ),
        ]
        yield mock

@pytest.fixture
def mock_delete_api_key() -> AsyncMock:
    """Mock the key_service.delete_api_key function."""
    with patch("app.api.endpoints.keys.delete_api_key", new_callable=AsyncMock) as mock:
        yield mock


# @pytest.fixture
# def mock_supabase_client() -> AsyncMock:
#     """Provide a mock async Supabase client."""
#     # mock_client = AsyncMock(spec=AsyncClient)
#     # Configure mock responses as needed, e.g.:
#     # mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = \
#     #     MagicMock(data=[...])
#     # return mock_client
#     pass # Needs Supabase client import

# Add other common fixtures here
