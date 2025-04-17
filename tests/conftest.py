"""Pytest configuration file for setting up fixtures."""

# Standard library imports
from unittest.mock import AsyncMock, MagicMock, patch

# Third-party imports
import pytest
from httpx import AsyncClient

# Local application imports
from app.api.endpoints.keys import APIKeyMetaOut
from app.core.security import get_current_user_id
from app.db.supabase_client import get_supabase_client
from app.main import app

TEST_USER_ID = "test-user-123"


# --- Fixtures ---


@pytest.fixture(scope="module")
def mock_auth():
    """Override the get_current_user_id dependency for testing."""
    app.dependency_overrides[get_current_user_id] = lambda: TEST_USER_ID
    yield
    # Clear overrides after tests
    app.dependency_overrides = {}


@pytest.fixture(scope="function")
async def client(mock_auth):
    """Provide an async test client with auth override."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# Mock specific service functions used by endpoints
@pytest.fixture
def mock_list_api_keys() -> AsyncMock:
    """Mock the key_service.list_api_keys function (used in keys endpoint)."""
    # Adjust the patch target to where list_api_keys is *used* by the endpoint
    with patch("app.api.endpoints.keys.list_api_keys", new_callable=AsyncMock) as mock:
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
    """Mock the key_service.delete_api_key function (used in keys endpoint)."""
    # Adjust the patch target to where delete_api_key is *used* by the endpoint
    with patch("app.api.endpoints.keys.delete_api_key", new_callable=AsyncMock) as mock:
        mock.return_value = None  # delete usually returns None on success
        yield mock


# Add mock for store_api_key if needed by any tests
@pytest.fixture
def mock_store_api_key() -> AsyncMock:
    """Mock the key_service.store_api_key function (used in keys endpoint)."""
    with patch("app.api.endpoints.keys.store_api_key", new_callable=AsyncMock) as mock:
        # Example: Return a simple dict or a mock object representing the stored key
        mock.return_value = {"id": "new-key-id", "key_meta": "mocked_meta"}
        yield mock


# If you need to mock the Supabase client itself (e.g., for direct service tests)
@pytest.fixture(scope="function")
def mock_supabase_client() -> AsyncMock:
    """Provide a mock async Supabase client instance."""
    mock_client = AsyncMock() # spec=SupabaseClient can be added if needed
    # Example: Mock table().select()... chain
    mock_table = AsyncMock()
    mock_select_query = AsyncMock()
    mock_execute = AsyncMock(
        return_value=MagicMock(data=[]) # Example empty data
    )

    mock_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select_query
    # Break the long line
    (mock_select_query.eq.return_value
     .order.return_value
     .execute.return_value) = mock_execute
    # Configure other methods as needed (insert, update, delete)

    # Override the dependency
    original_override = app.dependency_overrides.get(get_supabase_client)
    app.dependency_overrides[get_supabase_client] = lambda: mock_client
    yield mock_client
    # Restore original override or remove
    if original_override:
        app.dependency_overrides[get_supabase_client] = original_override
    else:
        del app.dependency_overrides[get_supabase_client]
