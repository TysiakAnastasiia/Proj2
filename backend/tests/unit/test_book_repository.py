"""
Tests for BookRepository to improve coverage.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Book
from app.schemas import BookGenre
from app.repositories.book import BookRepository


class TestBookRepository:
    """Test BookRepository functionality."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def book_repo(self, mock_db):
        """Create BookRepository instance."""
        return BookRepository(mock_db)

    async def test_get_with_owner_found(self, book_repo, mock_db):
        """Test getting book with owner when book exists."""
        mock_book = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_book
        mock_db.execute.return_value = mock_result

        result = await book_repo.get_with_owner(1)

        assert result == mock_book
        mock_db.execute.assert_called_once()

    async def test_get_with_owner_not_found(self, book_repo, mock_db):
        """Test getting book with owner when book doesn't exist."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await book_repo.get_with_owner(999)

        assert result is None

    async def test_search_with_all_filters(self, book_repo, mock_db):
        """Test search with all filters applied."""
        mock_books = [MagicMock(), MagicMock()]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_books
        
        # Mock total count
        mock_total_result = MagicMock()
        mock_total_result.scalar_one.return_value = 2
        mock_db.execute.side_effect = [mock_total_result, mock_result]

        books, total = await book_repo.search(
            query="test",
            genre="FICTION",
            available_only=True,
            owner_id=1,
            skip=0,
            limit=10
        )

        assert books == mock_books
        assert total == 2
        assert mock_db.execute.call_count == 2

    async def test_search_no_filters(self, book_repo, mock_db):
        """Test search with no filters."""
        mock_books = [MagicMock()]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_books
        
        mock_total_result = MagicMock()
        mock_total_result.scalar_one.return_value = 1
        mock_db.execute.side_effect = [mock_total_result, mock_result]

        books, total = await book_repo.search()

        assert books == mock_books
        assert total == 1

    async def test_get_average_rating_exists(self, book_repo, mock_db):
        """Test getting average rating when reviews exist."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = 4.5
        mock_db.execute.return_value = mock_result

        result = await book_repo.get_average_rating(1)

        assert result == 4.5

    async def test_get_average_rating_none(self, book_repo, mock_db):
        """Test getting average rating when no reviews exist."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await book_repo.get_average_rating(1)

        assert result is None

    async def test_get_review_count(self, book_repo, mock_db):
        """Test getting review count."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 5
        mock_db.execute.return_value = mock_result

        result = await book_repo.get_review_count(1)

        assert result == 5

    async def test_get_by_owner(self, book_repo, mock_db):
        """Test getting books by owner."""
        mock_books = [MagicMock(), MagicMock()]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_books
        mock_db.execute.return_value = mock_result

        result = await book_repo.get_by_owner(1)

        assert result == mock_books

    async def test_search_pagination(self, book_repo, mock_db):
        """Test search with pagination."""
        mock_books = [MagicMock()]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_books
        
        mock_total_result = MagicMock()
        mock_total_result.scalar_one.return_value = 100
        mock_db.execute.side_effect = [mock_total_result, mock_result]

        books, total = await book_repo.search(skip=10, limit=5)

        assert books == mock_books
        assert total == 100

    async def test_search_query_filter(self, book_repo, mock_db):
        """Test search with query filter."""
        mock_books = []
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_books
        
        mock_total_result = MagicMock()
        mock_total_result.scalar_one.return_value = 0
        mock_db.execute.side_effect = [mock_total_result, mock_result]

        books, total = await book_repo.search(query="harry potter")

        assert books == mock_books
        assert total == 0
