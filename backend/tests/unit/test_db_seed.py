"""
Tests for database seed functionality to improve coverage.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.seed import seed


class TestDatabaseSeed:
    """Test database seed functionality."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock(spec=AsyncSession)

    async def test_seed_function_exists(self):
        """Test that seed function exists."""
        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=False)
        mock_conn.run_sync = AsyncMock()

        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()  # already seeded
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch('app.db.seed.engine') as mock_engine, \
             patch('app.db.seed.AsyncSessionLocal') as mock_sl:
            mock_engine.begin.return_value = mock_conn
            mock_sl.return_value = mock_session

            await seed()

            mock_engine.begin.assert_called_once()

    async def test_seed_creates_tables(self):
        """Test that seed creates database tables."""
        with patch('app.db.seed.engine') as mock_engine, \
             patch('app.db.seed.AsyncSessionLocal') as mock_session_local:
            
            mock_conn = AsyncMock()
            mock_engine.begin.return_value.__aenter__.return_value = mock_conn
            
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            # Mock that no users exist yet
            mock_session.execute.return_value.scalar_one_or_none.return_value = None
            
            await seed()
            
            mock_engine.begin.assert_called_once()
            mock_conn.run_sync.assert_called_once()

    async def test_seed_with_exception(self):
        """Test seed function with exception."""
        with patch('app.db.seed.engine') as mock_engine:
            mock_engine.begin.side_effect = Exception("Database error")
            
            with pytest.raises(Exception, match="Database error"):
                await seed()
