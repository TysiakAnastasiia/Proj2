"""Test helper functions for async mocking."""
import asyncio
from unittest.mock import AsyncMock


def create_async_mock(**kwargs):
    """Create a properly configured AsyncMock for async methods."""
    mock = AsyncMock(**kwargs)
    # Make the mock awaitable
    async def mock_coro(*args, **kwargs):
        return mock(*args, **kwargs)
    
    mock.side_effect = mock_coro
    return mock


def create_async_magic_mock(return_value=None):
    """Create a MagicMock that works with async/await."""
    mock = AsyncMock()
    mock.return_value = return_value
    return mock
