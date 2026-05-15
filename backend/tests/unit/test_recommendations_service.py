"""
Tests for recommendations service to improve coverage.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.recommendations import RecommendationService
from app.models import Book, User, BookGenre


class TestRecommendationService:
    """Test RecommendationService functionality."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock(spec=AsyncSession)

    # RecommendationService is a module, not a class
    # We'll test the module functions directly

    async def test_genre_labels_exist(self):
        """Test that genre labels are defined."""
        from app.services.recommendations import GENRE_LABELS, FANTASY, DETECTIVE
        
        assert GENRE_LABELS is not None
        assert isinstance(GENRE_LABELS, dict)
        assert len(GENRE_LABELS) > 0
        assert FANTASY == "Фентезі"
        assert DETECTIVE == "Детектив"

    def test_genre_constants(self):
        """Test genre constants are properly defined."""
        from app.services.recommendations import (
            FANTASY, DETECTIVE, HISTORY, POETRY, ROMANCE
        )
        
        assert FANTASY == "Фентезі"
        assert DETECTIVE == "Детектив"
        assert HISTORY == "Історія"
        assert POETRY == "Поезія"
        assert ROMANCE == "Роман"

    def test_genre_labels_mapping(self):
        """Test genre labels mapping structure."""
        from app.services.recommendations import GENRE_LABELS
        from app.models import BookGenre
        
        # Test that all BookGenre enum values have labels
        for genre in BookGenre:
            assert genre in GENRE_LABELS
            assert isinstance(GENRE_LABELS[genre], str)
            assert len(GENRE_LABELS[genre]) > 0

    def test_recommendations_module_imports(self):
        """Test that recommendations module can be imported."""
        from app.services import recommendations
        assert recommendations is not None
        
        # Test that constants are available
        assert hasattr(recommendations, 'GENRE_LABELS')
        assert hasattr(recommendations, 'FANTASY')
        assert hasattr(recommendations, 'DETECTIVE')
