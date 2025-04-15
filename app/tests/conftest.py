from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True, scope="session")
def patch_supabase_client():
    with patch("app.db.supabase_client.get_supabase_client") as mock_client:
        mock_supabase = MagicMock()
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        # Default mocks for CRUD operations
        mock_table.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "mock-id"}], error=None
        )
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": "mock-id"}], error=None
        )
        mock_table.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={"id": "mock-id"}, error=None
        )
        mock_table.update.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": "mock-id"}], error=None
        )
        mock_table.delete.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": "mock-id"}], error=None
        )
        mock_client.return_value = mock_supabase
        yield
