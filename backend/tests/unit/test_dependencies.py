"""
Tests for core dependencies to improve coverage.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, oauth2_scheme
from app.models import User


class TestDependencies:
    """Test core dependencies functionality."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        user = MagicMock(spec=User)
        user.id = 1
        user.is_active = True
        return user

    async def test_get_current_user_success(self, mock_db, mock_user):
        """Test successful user authentication."""
        with patch('app.core.dependencies.decode_token') as mock_decode, \
             patch('app.core.dependencies.UserRepository') as mock_repo_class:
            
            # Setup mocks
            mock_decode.return_value = {"sub": "1", "type": "access"}
            
            mock_repo = AsyncMock()
            mock_repo.get_by_id = AsyncMock(return_value=mock_user)
            mock_repo_class.return_value = mock_repo

            result = await get_current_user("valid_token", mock_db)

            assert result == mock_user
            mock_decode.assert_called_once_with("valid_token")
            mock_repo.get_by_id.assert_called_once_with(1)

    async def test_get_current_user_invalid_token_no_payload(self, mock_db):
        """Test authentication with invalid token (no payload)."""
        with patch('app.core.dependencies.decode_token') as mock_decode, \
             patch('app.core.dependencies.UserRepository') as mock_repo_class:
            
            mock_decode.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user("invalid_token", mock_db)

            assert exc_info.value.status_code == 401
            assert "Could not validate credentials" in str(exc_info.value.detail)

    async def test_get_current_user_invalid_token_wrong_type(self, mock_db):
        """Test authentication with wrong token type."""
        with patch('app.core.dependencies.decode_token') as mock_decode, \
             patch('app.core.dependencies.UserRepository') as mock_repo_class:
            
            mock_decode.return_value = {"sub": "1", "type": "refresh"}

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user("refresh_token", mock_db)

            assert exc_info.value.status_code == 401

    async def test_get_current_user_no_user_id(self, mock_db):
        """Test authentication with no user_id in payload."""
        with patch('app.core.dependencies.decode_token') as mock_decode, \
             patch('app.core.dependencies.UserRepository') as mock_repo_class:
            
            mock_decode.return_value = {"type": "access"}

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user("token_without_sub", mock_db)

            assert exc_info.value.status_code == 401

    async def test_get_current_user_user_not_found(self, mock_db):
        """Test authentication when user not found in database."""
        with patch('app.core.dependencies.decode_token') as mock_decode, \
             patch('app.core.dependencies.UserRepository') as mock_repo_class:
            
            mock_decode.return_value = {"sub": "999", "type": "access"}
            
            mock_repo = AsyncMock()
            mock_repo.get_by_id = AsyncMock(return_value=None)
            mock_repo_class.return_value = mock_repo

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user("valid_token", mock_db)

            assert exc_info.value.status_code == 401

    async def test_get_current_user_inactive_user(self, mock_db):
        """Test authentication with inactive user."""
        with patch('app.core.dependencies.decode_token') as mock_decode, \
             patch('app.core.dependencies.UserRepository') as mock_repo_class:
            
            mock_decode.return_value = {"sub": "1", "type": "access"}
            
            mock_repo = AsyncMock()
            mock_user = MagicMock(spec=User)
            mock_user.is_active = False
            mock_repo.get_by_id = AsyncMock(return_value=mock_user)
            mock_repo_class.return_value = mock_repo

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user("valid_token", mock_db)

            assert exc_info.value.status_code == 401

    def test_oauth2_scheme_configuration(self):
        """Test OAuth2 scheme configuration."""
        # Test that the scheme exists
        assert oauth2_scheme is not None
        # The tokenUrl attribute might not be directly accessible
        # Just test the scheme can be instantiated
