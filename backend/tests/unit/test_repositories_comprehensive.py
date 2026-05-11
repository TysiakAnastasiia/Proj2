
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from app.repositories import (
    BaseRepository, UserRepository, BookRepository, ReviewRepository,
    ExchangeRepository, WishlistRepository, MessageRepository, FriendshipRepository
)
from app.models import User, Book, Review, Exchange, WishlistItem, Message, Friendship


class TestBaseRepository:
    """Test BaseRepository abstract class."""
    
    def test_base_repository_is_abstract(self):
        """Test that BaseRepository cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseRepository()
    
    def test_base_repository_methods_are_abstract(self):
        """Test that BaseRepository methods are abstract."""
        class TestRepository(BaseRepository[User]):
            async def create(self, data: dict) -> User:
                pass
            
            async def get_by_id(self, id: int) -> User:
                pass
            
            async def get_all(self, limit: int = 100) -> list[User]:
                pass
            
            async def update(self, id: int, data: dict) -> User:
                pass
            
            async def delete(self, id: int) -> bool:
                pass
        
        # Should be able to instantiate concrete implementation
        repo = TestRepository()
        assert repo is not None


class TestUserRepository:
    """Test UserRepository functionality."""
    
    def setup_method(self):
        """Setup test dependencies."""
        self.mock_session = AsyncMock()
        self.user_repo = UserRepository(self.mock_session)
    
    async def test_create_user_success(self):
        """Test creating a user successfully."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "hashed_password",
            "full_name": "Test User",
            "bio": "Test bio",
            "city": "Test City",
            "is_active": True
        }
        
        # Create user object directly
        user_obj = User(id=1, **user_data)
        
        # Mock database operations
        self.mock_session.add = AsyncMock()
        self.mock_session.flush = AsyncMock()
        self.mock_session.refresh = AsyncMock()
        
        # Create user
        result = await self.user_repo.create(user_obj)
        
        # Assert
        assert result.id == 1
        assert result.email == user_data["email"]
        assert result.username == user_data["username"]
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        self.mock_session.refresh.assert_called_once()
    
    async def test_get_user_by_id_success(self):
        """Test getting user by ID successfully."""
        user_id = 1
        mock_user = User(id=user_id, email="test@example.com", username="test", hashed_password="pass")
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.user_repo.get_by_id(user_id)
        
        # Assert
        assert result.id == user_id
        assert result.email == "test@example.com"
        self.mock_session.execute.assert_called_once()
    
    async def test_get_user_by_id_not_found(self):
        """Test getting user by ID when not found."""
        user_id = 999
        
        # Mock database query returning None
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.user_repo.get_by_id(user_id)
        
        # Assert
        assert result is None
    
    async def test_get_user_by_email_success(self):
        """Test getting user by email successfully."""
        email = "test@example.com"
        mock_user = User(id=1, email=email, username="test", hashed_password="pass")
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.user_repo.get_by_email(email)
        
        # Assert
        assert result.email == email
        self.mock_session.execute.assert_called_once()
    
    async def test_get_user_by_email_not_found(self):
        """Test getting user by email when not found."""
        email = "nonexistent@example.com"
        
        # Mock database query returning None
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.user_repo.get_by_email(email)
        
        # Assert
        assert result is None
    
    async def test_get_user_by_username_success(self):
        """Test getting user by username successfully."""
        username = "testuser"
        mock_user = User(id=1, email="test@example.com", username=username, hashed_password="pass")
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.user_repo.get_by_username(username)
        
        # Assert
        assert result.username == username
        self.mock_session.execute.assert_called_once()
    
    async def test_get_all_users_success(self):
        """Test getting all users successfully."""
        limit = 10
        mock_users = [
            User(id=1, email="user1@example.com", username="user1", hashed_password="pass"),
            User(id=2, email="user2@example.com", username="user2", hashed_password="pass")
        ]
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalars = AsyncMock(return_value=AsyncMock(all=AsyncMock(return_value=mock_users)))
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.user_repo.get_all(limit)
        
        # Assert
        assert len(result) == 2
        assert result[0].username == "user1"
        assert result[1].username == "user2"
        self.mock_session.execute.assert_called_once()
    
    async def test_update_user_success(self):
        """Test updating a user successfully."""
        user_id = 1
        update_data = {
            "full_name": "Updated Name",
            "bio": "Updated bio",
            "city": "Updated City"
        }
        
        # Mock existing user
        mock_user = User(id=user_id, email="test@example.com", username="test", hashed_password="pass")
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        self.mock_session.execute.return_value = mock_result
        
        # Mock update operations
        self.mock_session.commit.return_value = None
        self.mock_session.refresh.return_value = None
        
        # Execute
        result = await self.user_repo.update(user_id, update_data)
        
        # Assert
        assert result.full_name == update_data["full_name"]
        assert result.bio == update_data["bio"]
        assert result.city == update_data["city"]
        self.mock_session.commit.assert_called_once()
        self.mock_session.refresh.assert_called_once()
    
    async def test_update_user_not_found(self):
        """Test updating a user that doesn't exist."""
        user_id = 999
        update_data = {"full_name": "Updated Name"}
        
        # Mock database query returning None
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.user_repo.update(user_id, update_data)
        
        # Assert
        assert result is None
    
    async def test_delete_user_success(self):
        """Test deleting a user successfully."""
        user_id = 1
        mock_user = User(id=user_id, email="test@example.com", username="test", hashed_password="pass")
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        self.mock_session.execute.return_value = mock_result
        
        # Mock delete operations
        self.mock_session.delete.return_value = None
        self.mock_session.commit.return_value = None
        
        # Execute
        result = await self.user_repo.delete(user_id)
        
        # Assert
        assert result is True
        self.mock_session.delete.assert_called_once_with(mock_user)
        self.mock_session.commit.assert_called_once()
    
    async def test_delete_user_not_found(self):
        """Test deleting a user that doesn't exist."""
        user_id = 999
        
        # Mock database query returning None
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.user_repo.delete(user_id)
        
        # Assert
        assert result is False
    
    async def test_search_users_success(self):
        """Test searching users successfully."""
        query = "test"
        limit = 10
        mock_users = [
            User(id=1, email="test1@example.com", username="test1", hashed_password="pass"),
            User(id=2, email="test2@example.com", username="test2", hashed_password="pass")
        ]
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalars = AsyncMock(return_value=AsyncMock(all=AsyncMock(return_value=mock_users)))
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.user_repo.search(query, limit)
        
        # Assert
        assert len(result) == 2
        assert all(query.lower() in user.username.lower() or query.lower() in user.email.lower() for user in result)
        self.mock_session.execute.assert_called_once()


class TestBookRepository:
    """Test BookRepository functionality."""
    
    def setup_method(self):
        """Setup test dependencies."""
        self.mock_session = AsyncMock()
        self.book_repo = BookRepository(self.mock_session)
    
    async def test_create_book_success(self):
        """Test creating a book successfully."""
        book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "isbn": "978-3-16-148410-0",
            "description": "Test description",
            "genre": "Fiction",
            "year_published": 2023,
            "pages": 250,
            "language": "English",
            "owner_id": 1,
            "is_available": True
        }
        
        # Create book object directly
        book_obj = Book(id=1, **book_data)
        
        # Mock database operations
        self.mock_session.add = AsyncMock()
        self.mock_session.flush = AsyncMock()
        self.mock_session.refresh = AsyncMock()
        
        # Create book
        result = await self.book_repo.create(book_obj)
        
        # Assert
        assert result.id == 1
        assert result.title == book_data["title"]
        assert result.author == book_data["author"]
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        self.mock_session.refresh.assert_called_once()
    
    async def test_get_book_by_id_success(self):
        """Test getting book by ID successfully."""
        book_id = 1
        mock_book = Book(id=book_id, title="Test Book", author="Test Author", owner_id=1)
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_book
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.book_repo.get_by_id(book_id)
        
        # Assert
        assert result.id == book_id
        assert result.title == "Test Book"
        self.mock_session.execute.assert_called_once()
    
    async def test_get_book_by_id_not_found(self):
        """Test getting book by ID when not found."""
        book_id = 999
        
        # Mock database query returning None
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.book_repo.get_by_id(book_id)
        
        # Assert
        assert result is None
    
    async def test_get_books_by_owner_success(self):
        """Test getting books by owner successfully."""
        owner_id = 1
        mock_books = [
            Book(id=1, title="Book 1", author="Author 1", owner_id=owner_id),
            Book(id=2, title="Book 2", author="Author 2", owner_id=owner_id)
        ]
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalars = AsyncMock(return_value=AsyncMock(all=AsyncMock(return_value=mock_books)))
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.book_repo.get_by_owner_id(owner_id)
        
        # Assert
        assert len(result) == 2
        assert all(book.owner_id == owner_id for book in result)
        self.mock_session.execute.assert_called_once()
    
    async def test_search_books_success(self):
        """Test searching books successfully."""
        query = "test"
        filters = {"genre": "Fiction", "language": "English"}
        limit = 10
        mock_books = [
            Book(id=1, title="Test Book 1", author="Author 1", owner_id=1, genre="Fiction"),
            Book(id=2, title="Test Book 2", author="Author 2", owner_id=2, genre="Fiction")
        ]
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalars = AsyncMock(return_value=AsyncMock(all=AsyncMock(return_value=mock_books)))
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.book_repo.search(query, filters, limit)
        
        # Assert
        assert len(result) == 2
        assert all(query.lower() in book.title.lower() or query.lower() in book.author.lower() for book in result)
        self.mock_session.execute.assert_called_once()
    
    async def test_update_book_success(self):
        """Test updating a book successfully."""
        book_id = 1
        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "is_available": False
        }
        
        # Mock existing book
        mock_book = Book(id=book_id, title="Original Title", author="Test Author", owner_id=1)
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_book
        self.mock_session.execute.return_value = mock_result
        
        # Mock update operations
        self.mock_session.commit.return_value = None
        self.mock_session.refresh.return_value = None
        
        # Execute
        result = await self.book_repo.update(book_id, update_data)
        
        # Assert
        assert result.title == update_data["title"]
        assert result.description == update_data["description"]
        assert result.is_available == update_data["is_available"]
        self.mock_session.commit.assert_called_once()
        self.mock_session.refresh.assert_called_once()
    
    async def test_delete_book_success(self):
        """Test deleting a book successfully."""
        book_id = 1
        mock_book = Book(id=book_id, title="Test Book", author="Test Author", owner_id=1)
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_book
        self.mock_session.execute.return_value = mock_result
        
        # Mock delete operations
        self.mock_session.delete.return_value = None
        self.mock_session.commit.return_value = None
        
        # Execute
        result = await self.book_repo.delete(book_id)
        
        # Assert
        assert result is True
        self.mock_session.delete.assert_called_once_with(mock_book)
        self.mock_session.commit.assert_called_once()


class TestReviewRepository:
    """Test ReviewRepository functionality."""
    
    def setup_method(self):
        """Setup test dependencies."""
        self.mock_session = AsyncMock()
        self.review_repo = ReviewRepository(self.mock_session)
    
    async def test_create_review_success(self):
        """Test creating a review successfully."""
        review_data = {
            "user_id": 1,
            "book_id": 1,
            "rating": 4,
            "title": "Great Book",
            "content": "I really enjoyed this book.",
            "is_spoiler": False
        }
        
        # Create review object directly
        review_obj = Review(id=1, **review_data)
        
        # Mock database operations
        self.mock_session.add = AsyncMock()
        self.mock_session.flush = AsyncMock()
        self.mock_session.refresh = AsyncMock()
        
        # Create review
        result = await self.review_repo.create(review_obj)
        
        # Assert
        assert result.id == 1
        assert result.user_id == review_data["user_id"]
        assert result.book_id == review_data["book_id"]
        assert result.rating == review_data["rating"]
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        self.mock_session.refresh.assert_called_once()
    
    async def test_get_review_by_id_success(self):
        """Test getting review by ID successfully."""
        review_id = 1
        mock_review = Review(id=review_id, user_id=1, book_id=1, rating=4)
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_review
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.review_repo.get_by_id(review_id)
        
        # Assert
        assert result.id == review_id
        assert result.rating == 4
        self.mock_session.execute.assert_called_once()
    
    async def test_get_reviews_by_book_success(self):
        """Test getting reviews by book successfully."""
        book_id = 1
        mock_reviews = [
            Review(id=1, user_id=1, book_id=book_id, rating=4),
            Review(id=2, user_id=2, book_id=book_id, rating=5)
        ]
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalars = AsyncMock(return_value=AsyncMock(all=AsyncMock(return_value=mock_reviews)))
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.review_repo.get_by_book_id(book_id)
        
        # Assert
        assert len(result) == 2
        assert all(review.book_id == book_id for review in result)
        self.mock_session.execute.assert_called_once()
    
    async def test_get_review_by_user_and_book_success(self):
        """Test getting review by user and book successfully."""
        user_id = 1
        book_id = 1
        mock_review = Review(id=1, user_id=user_id, book_id=book_id, rating=4)
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_review
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.review_repo.get_by_user_and_book(user_id, book_id)
        
        # Assert
        assert result.user_id == user_id
        assert result.book_id == book_id
        self.mock_session.execute.assert_called_once()
    
    async def test_update_review_success(self):
        """Test updating a review successfully."""
        review_id = 1
        update_data = {
            "rating": 5,
            "title": "Updated Title",
            "content": "Updated content"
        }
        
        # Mock existing review
        mock_review = Review(id=review_id, user_id=1, book_id=1, rating=4)
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_review
        self.mock_session.execute.return_value = mock_result
        
        # Mock update operations
        self.mock_session.commit.return_value = None
        self.mock_session.refresh.return_value = None
        
        # Execute
        result = await self.review_repo.update(review_id, update_data)
        
        # Assert
        assert result.rating == update_data["rating"]
        assert result.title == update_data["title"]
        assert result.content == update_data["content"]
        self.mock_session.commit.assert_called_once()
        self.mock_session.refresh.assert_called_once()
    
    async def test_delete_review_success(self):
        """Test deleting a review successfully."""
        review_id = 1
        mock_review = Review(id=review_id, user_id=1, book_id=1, rating=4)
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_review
        self.mock_session.execute.return_value = mock_result
        
        # Mock delete operations
        self.mock_session.delete.return_value = None
        self.mock_session.commit.return_value = None
        
        # Execute
        result = await self.review_repo.delete(review_id)
        
        # Assert
        assert result is True
        self.mock_session.delete.assert_called_once_with(mock_review)
        self.mock_session.commit.assert_called_once()


class TestExchangeRepository:
    """Test ExchangeRepository functionality."""
    
    def setup_method(self):
        """Setup test dependencies."""
        self.mock_session = AsyncMock()
        self.exchange_repo = ExchangeRepository(self.mock_session)
    
    async def test_create_exchange_success(self):
        """Test creating an exchange successfully."""
        exchange_data = {
            "requester_id": 1,
            "requested_user_id": 2,
            "offered_book_id": 1,
            "requested_book_id": 2,
            "status": "pending",
            "message": "I'd like to exchange books!"
        }
        
        # Create exchange object directly
        exchange_obj = Exchange(id=1, **exchange_data)
        
        # Mock database operations
        self.mock_session.add = AsyncMock()
        self.mock_session.flush = AsyncMock()
        self.mock_session.refresh = AsyncMock()
        
        # Create exchange
        result = await self.exchange_repo.create(exchange_obj)
        
        # Assert
        assert result.id == 1
        assert result.requester_id == exchange_data["requester_id"]
        assert result.requested_user_id == exchange_data["requested_user_id"]
        assert result.status == exchange_data["status"]
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        self.mock_session.refresh.assert_called_once()
    
    async def test_get_exchange_by_id_success(self):
        """Test getting exchange by ID successfully."""
        exchange_id = 1
        mock_exchange = Exchange(
            id=exchange_id,
            requester_id=1,
            requested_user_id=2,
            offered_book_id=1,
            requested_book_id=2,
            status="pending"
        )
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_exchange
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.exchange_repo.get_by_id(exchange_id)
        
        # Assert
        assert result.id == exchange_id
        assert result.status == "pending"
        self.mock_session.execute.assert_called_once()
    
    async def test_get_exchanges_by_user_success(self):
        """Test getting exchanges by user successfully."""
        user_id = 1
        mock_exchanges = [
            Exchange(id=1, requester_id=user_id, requested_user_id=2, offered_book_id=1, requested_book_id=2, status="pending"),
            Exchange(id=2, requester_id=2, requested_user_id=user_id, offered_book_id=3, requested_book_id=4, status="accepted")
        ]
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalars = AsyncMock(return_value=AsyncMock(all=AsyncMock(return_value=mock_exchanges)))
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.exchange_repo.get_by_user_id(user_id)
        
        # Assert
        assert len(result) == 2
        assert all(
            exchange.requester_id == user_id or exchange.requested_user_id == user_id
            for exchange in result
        )
        self.mock_session.execute.assert_called_once()
    
    async def test_get_active_exchange_success(self):
        """Test getting active exchange between users and books."""
        requester_id = 1
        requested_user_id = 2
        offered_book_id = 1
        requested_book_id = 2
        mock_exchange = Exchange(
            id=1,
            requester_id=requester_id,
            requested_user_id=requested_user_id,
            offered_book_id=offered_book_id,
            requested_book_id=requested_book_id,
            status="pending"
        )
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_exchange
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.exchange_repo.get_active_exchange(
            requester_id, requested_user_id, offered_book_id, requested_book_id
        )
        
        # Assert
        assert result.requester_id == requester_id
        assert result.requested_user_id == requested_user_id
        assert result.offered_book_id == offered_book_id
        assert result.requested_book_id == requested_book_id
        self.mock_session.execute.assert_called_once()
    
    async def test_update_exchange_success(self):
        """Test updating an exchange successfully."""
        exchange_id = 1
        update_data = {
            "status": "accepted"
        }
        
        # Mock existing exchange
        mock_exchange = Exchange(
            id=exchange_id,
            requester_id=1,
            requested_user_id=2,
            offered_book_id=1,
            requested_book_id=2,
            status="pending"
        )
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_exchange
        self.mock_session.execute.return_value = mock_result
        
        # Mock update operations
        self.mock_session.commit.return_value = None
        self.mock_session.refresh.return_value = None
        
        # Execute
        result = await self.exchange_repo.update(exchange_id, update_data)
        
        # Assert
        assert result.status == update_data["status"]
        self.mock_session.commit.assert_called_once()
        self.mock_session.refresh.assert_called_once()
    
    async def test_delete_exchange_success(self):
        """Test deleting an exchange successfully."""
        exchange_id = 1
        mock_exchange = Exchange(
            id=exchange_id,
            requester_id=1,
            requested_user_id=2,
            offered_book_id=1,
            requested_book_id=2,
            status="pending"
        )
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_exchange
        self.mock_session.execute.return_value = mock_result
        
        # Mock delete operations
        self.mock_session.delete.return_value = None
        self.mock_session.commit.return_value = None
        
        # Execute
        result = await self.exchange_repo.delete(exchange_id)
        
        # Assert
        assert result is True
        self.mock_session.delete.assert_called_once_with(mock_exchange)
        self.mock_session.commit.assert_called_once()


class TestWishlistRepository:
    """Test WishlistRepository functionality."""
    
    def setup_method(self):
        """Setup test dependencies."""
        self.mock_session = AsyncMock()
        self.wishlist_repo = WishlistRepository(self.mock_session)
    
    async def test_create_wishlist_item_success(self):
        """Test creating a wishlist item successfully."""
        item_data = {
            "user_id": 1,
            "book_id": 1,
            "priority": "high",
            "notes": "Really want this book!"
        }
        
        # Create wishlist item object directly
        item_obj = WishlistItem(id=1, **item_data)
        
        # Mock database operations
        self.mock_session.add = AsyncMock()
        self.mock_session.flush = AsyncMock()
        self.mock_session.refresh = AsyncMock()
        
        # Create wishlist item
        result = await self.wishlist_repo.create(item_obj)
        
        # Assert
        assert result.id == 1
        assert result.user_id == item_data["user_id"]
        assert result.book_id == item_data["book_id"]
        assert result.priority == item_data["priority"]
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        self.mock_session.refresh.assert_called_once()
    
    async def test_get_wishlist_item_by_id_success(self):
        """Test getting wishlist item by ID successfully."""
        item_id = 1
        mock_item = WishlistItem(id=item_id, user_id=1, book_id=1, priority="high")
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_item
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.wishlist_repo.get_by_id(item_id)
        
        # Assert
        assert result.id == item_id
        assert result.priority == "high"
        self.mock_session.execute.assert_called_once()
    
    async def test_get_wishlist_items_by_user_success(self):
        """Test getting wishlist items by user successfully."""
        user_id = 1
        mock_items = [
            WishlistItem(id=1, user_id=user_id, book_id=1, priority="high"),
            WishlistItem(id=2, user_id=user_id, book_id=2, priority="medium"),
            WishlistItem(id=3, user_id=user_id, book_id=3, priority="low")
        ]
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalars = AsyncMock(return_value=AsyncMock(all=AsyncMock(return_value=mock_items)))
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.wishlist_repo.get_by_user_id(user_id)
        
        # Assert
        assert len(result) == 3
        assert all(item.user_id == user_id for item in result)
        self.mock_session.execute.assert_called_once()
    
    async def test_get_wishlist_item_by_user_and_book_success(self):
        """Test getting wishlist item by user and book successfully."""
        user_id = 1
        book_id = 1
        mock_item = WishlistItem(id=1, user_id=user_id, book_id=book_id, priority="high")
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_item
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.wishlist_repo.get_by_user_and_book(user_id, book_id)
        
        # Assert
        assert result.user_id == user_id
        assert result.book_id == book_id
        self.mock_session.execute.assert_called_once()
    
    async def test_update_wishlist_item_success(self):
        """Test updating a wishlist item successfully."""
        item_id = 1
        update_data = {
            "priority": "low",
            "notes": "Updated notes"
        }
        
        # Mock existing item
        mock_item = WishlistItem(id=item_id, user_id=1, book_id=1, priority="high")
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_item
        self.mock_session.execute.return_value = mock_result
        
        # Mock update operations
        self.mock_session.commit.return_value = None
        self.mock_session.refresh.return_value = None
        
        # Execute
        result = await self.wishlist_repo.update(item_id, update_data)
        
        # Assert
        assert result.priority == update_data["priority"]
        assert result.notes == update_data["notes"]
        self.mock_session.commit.assert_called_once()
        self.mock_session.refresh.assert_called_once()
    
    async def test_delete_wishlist_item_success(self):
        """Test deleting a wishlist item successfully."""
        item_id = 1
        mock_item = WishlistItem(id=item_id, user_id=1, book_id=1, priority="high")
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_item
        self.mock_session.execute.return_value = mock_result
        
        # Mock delete operations
        self.mock_session.delete.return_value = None
        self.mock_session.commit.return_value = None
        
        # Execute
        result = await self.wishlist_repo.delete(item_id)
        
        # Assert
        assert result is True
        self.mock_session.delete.assert_called_once_with(mock_item)
        self.mock_session.commit.assert_called_once()


class TestMessageRepository:
    """Test MessageRepository functionality."""
    
    def setup_method(self):
        """Setup test dependencies."""
        self.mock_session = AsyncMock()
        self.message_repo = MessageRepository(self.mock_session)
    
    async def test_create_message_success(self):
        """Test creating a message successfully."""
        message_data = {
            "sender_id": 1,
            "receiver_id": 2,
            "content": "Hello, how are you?",
            "is_read": False
        }
        
        # Create message object directly
        message_obj = Message(id=1, **message_data)
        
        # Mock database operations
        self.mock_session.add = AsyncMock()
        self.mock_session.commit = AsyncMock()
        self.mock_session.refresh = AsyncMock()
        
        # Create message
        result = await self.message_repo.create(message_obj)
        
        # Assert
        assert result.id == 1
        assert result.sender_id == message_data["sender_id"]
        assert result.receiver_id == message_data["receiver_id"]
        assert result.content == message_data["content"]
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        self.mock_session.refresh.assert_called_once()
    
    async def test_get_message_by_id_success(self):
        """Test getting message by ID successfully."""
        message_id = 1
        mock_message = Message(id=message_id, sender_id=1, receiver_id=2, content="Hello")
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_message
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.message_repo.get_by_id(message_id)
        
        # Assert
        assert result.id == message_id
        assert result.content == "Hello"
        self.mock_session.execute.assert_called_once()
    
    async def test_get_conversation_success(self):
        """Test getting conversation between two users."""
        user_id = 1
        other_user_id = 2
        limit = 50
        mock_messages = [
            Message(id=1, sender_id=user_id, receiver_id=other_user_id, content="Hello", is_read=True),
            Message(id=2, sender_id=other_user_id, receiver_id=user_id, content="Hi there!", is_read=True),
            Message(id=3, sender_id=user_id, receiver_id=other_user_id, content="How are you?", is_read=False)
        ]
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalars = AsyncMock(return_value=AsyncMock(all=AsyncMock(return_value=mock_messages)))
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.message_repo.get_conversation(user_id, other_user_id, limit)
        
        # Assert
        assert len(result) == 3
        assert all(
            (msg.sender_id == user_id and msg.receiver_id == other_user_id) or
            (msg.sender_id == other_user_id and msg.receiver_id == user_id)
            for msg in result
        )
        self.mock_session.execute.assert_called_once()
    
    async def test_get_unread_messages_by_receiver_success(self):
        """Test getting unread messages by receiver."""
        receiver_id = 1
        mock_messages = [
            Message(id=1, sender_id=2, receiver_id=receiver_id, content="Hello", is_read=False),
            Message(id=2, sender_id=3, receiver_id=receiver_id, content="Hi", is_read=False)
        ]
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalars = AsyncMock(return_value=AsyncMock(all=AsyncMock(return_value=mock_messages)))
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.message_repo.get_unread_by_receiver(receiver_id)
        
        # Assert
        assert len(result) == 2
        assert all(msg.receiver_id == receiver_id and msg.is_read is False for msg in result)
        self.mock_session.execute.assert_called_once()
    
    async def test_update_message_success(self):
        """Test updating a message successfully."""
        message_id = 1
        update_data = {
            "is_read": True
        }
        
        # Mock existing message
        mock_message = Message(id=message_id, sender_id=1, receiver_id=2, content="Hello", is_read=False)
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_message
        self.mock_session.execute.return_value = mock_result
        
        # Mock update operations
        self.mock_session.commit.return_value = None
        self.mock_session.refresh.return_value = None
        
        # Execute
        result = await self.message_repo.update(message_id, update_data)
        
        # Assert
        assert result.is_read == update_data["is_read"]
        self.mock_session.commit.assert_called_once()
        self.mock_session.refresh.assert_called_once()
    
    async def test_delete_message_success(self):
        """Test deleting a message successfully."""
        message_id = 1
        mock_message = Message(id=message_id, sender_id=1, receiver_id=2, content="Hello", is_read=False)
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_message
        self.mock_session.execute.return_value = mock_result
        
        # Mock delete operations
        self.mock_session.delete.return_value = None
        self.mock_session.commit.return_value = None
        
        # Execute
        result = await self.message_repo.delete(message_id)
        
        # Assert
        assert result is True
        self.mock_session.delete.assert_called_once_with(mock_message)
        self.mock_session.commit.assert_called_once()


class TestFriendshipRepository:
    """Test FriendshipRepository functionality."""
    
    def setup_method(self):
        """Setup test dependencies."""
        self.mock_session = AsyncMock()
        self.friendship_repo = FriendshipRepository(self.mock_session)
    
    async def test_create_friendship_success(self):
        """Test creating a friendship successfully."""
        friendship_data = {
            "user_id": 1,
            "friend_id": 2,
            "status": "pending"
        }
        
        # Create friendship object directly
        friendship_obj = Friendship(id=1, **friendship_data)
        
        # Mock database operations
        self.mock_session.add = AsyncMock()
        self.mock_session.flush = AsyncMock()
        self.mock_session.refresh = AsyncMock()
        
        # Create friendship
        result = await self.friendship_repo.create(friendship_obj)
        
        # Assert
        assert result.id == 1
        assert result.user_id == friendship_data["user_id"]
        assert result.friend_id == friendship_data["friend_id"]
        assert result.status == friendship_data["status"]
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        self.mock_session.refresh.assert_called_once()
    
    async def test_get_friendship_by_id_success(self):
        """Test getting friendship by ID successfully."""
        friendship_id = 1
        mock_friendship = Friendship(id=friendship_id, user_id=1, friend_id=2, status="pending")
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_friendship
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.friendship_repo.get_by_id(friendship_id)
        
        # Assert
        assert result.id == friendship_id
        assert result.status == "pending"
        self.mock_session.execute.assert_called_once()
    
    async def test_get_friendship_between_users_success(self):
        """Test getting friendship between two users."""
        user_id = 1
        friend_id = 2
        mock_friendship = Friendship(id=1, user_id=user_id, friend_id=friend_id, status="accepted")
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_friendship
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.friendship_repo.get_between_users(user_id, friend_id)
        
        # Assert
        assert result.user_id == user_id
        assert result.friend_id == friend_id
        self.mock_session.execute.assert_called_once()
    
    async def test_get_accepted_friendships_success(self):
        """Test getting accepted friendships for a user."""
        user_id = 1
        mock_friendships = [
            Friendship(id=1, user_id=user_id, friend_id=2, status="accepted"),
            Friendship(id=2, user_id=3, friend_id=user_id, status="accepted"),
            Friendship(id=3, user_id=user_id, friend_id=4, status="accepted")
        ]
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalars = AsyncMock(return_value=AsyncMock(all=AsyncMock(return_value=mock_friendships)))
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.friendship_repo.get_accepted_friendships(user_id)
        
        # Assert
        assert len(result) == 3
        assert all(
            friendship.status == "accepted" and
            (friendship.user_id == user_id or friendship.friend_id == user_id)
            for friendship in result
        )
        self.mock_session.execute.assert_called_once()
    
    async def test_get_pending_requests_success(self):
        """Test getting pending friend requests for a user."""
        user_id = 1
        mock_requests = [
            Friendship(id=1, user_id=2, friend_id=user_id, status="pending"),
            Friendship(id=2, user_id=3, friend_id=user_id, status="pending")
        ]
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalars = AsyncMock(return_value=AsyncMock(all=AsyncMock(return_value=mock_requests)))
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.friendship_repo.get_pending_requests(user_id)
        
        # Assert
        assert len(result) == 2
        assert all(
            friendship.friend_id == user_id and friendship.status == "pending"
            for friendship in result
        )
        self.mock_session.execute.assert_called_once()
    
    async def test_update_friendship_success(self):
        """Test updating a friendship successfully."""
        friendship_id = 1
        update_data = {
            "status": "accepted"
        }
        
        # Mock existing friendship
        mock_friendship = Friendship(id=friendship_id, user_id=1, friend_id=2, status="pending")
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_friendship
        self.mock_session.execute.return_value = mock_result
        
        # Mock update operations
        self.mock_session.commit.return_value = None
        self.mock_session.refresh.return_value = None
        
        # Execute
        result = await self.friendship_repo.update(friendship_id, update_data)
        
        # Assert
        assert result.status == update_data["status"]
        self.mock_session.commit.assert_called_once()
        self.mock_session.refresh.assert_called_once()
    
    async def test_delete_friendship_success(self):
        """Test deleting a friendship successfully."""
        friendship_id = 1
        mock_friendship = Friendship(id=friendship_id, user_id=1, friend_id=2, status="accepted")
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_friendship
        self.mock_session.execute.return_value = mock_result
        
        # Mock delete operations
        self.mock_session.delete.return_value = None
        self.mock_session.commit.return_value = None
        
        # Execute
        result = await self.friendship_repo.delete(friendship_id)
        
        # Assert
        assert result is True
        self.mock_session.delete.assert_called_once_with(mock_friendship)
        self.mock_session.commit.assert_called_once()


class TestRepositoryErrorHandling:
    """Test repository error handling scenarios."""
    
    def setup_method(self):
        """Setup test dependencies."""
        self.mock_session = AsyncMock()
        self.user_repo = UserRepository(self.mock_session)
    
    async def test_database_connection_error(self):
        """Test handling database connection errors."""
        # Mock database error
        self.mock_session.execute.side_effect = Exception("Database connection failed")
        
        # Execute and assert
        with pytest.raises(Exception, match="Database connection failed"):
            await self.user_repo.get_by_id(1)
    
    async def test_constraint_violation_error(self):
        """Test handling constraint violation errors."""
        # Mock constraint violation
        self.mock_session.commit.side_effect = Exception("UNIQUE constraint failed")
        
        # Execute and assert
        with pytest.raises(Exception, match="UNIQUE constraint failed"):
            await self.user_repo.create({"email": "test@example.com", "username": "test", "hashed_password": "pass"})
    
    async def test_transaction_rollback(self):
        """Test transaction rollback on errors."""
        # Mock error during commit
        self.mock_session.commit.side_effect = Exception("Transaction failed")
        
        try:
            await self.user_repo.create({"email": "test@example.com", "username": "test", "hashed_password": "pass"})
        except Exception:
            pass
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()


class TestRepositoryPerformance:
    """Test repository performance characteristics."""
    
    def setup_method(self):
        """Setup test dependencies."""
        self.mock_session = AsyncMock()
        self.user_repo = UserRepository(self.mock_session)
    
    async def test_query_with_limit(self):
        """Test that queries respect limit parameter."""
        limit = 5
        mock_users = [User(id=i, email=f"user{i}@example.com", username=f"user{i}", hashed_password="pass") for i in range(10)]
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalars = AsyncMock(return_value=AsyncMock(all=AsyncMock(return_value=mock_users[:limit])))
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.user_repo.get_all(limit)
        
        # Assert
        assert len(result) <= limit
        self.mock_session.execute.assert_called_once()
    
    async def test_query_ordering(self):
        """Test that queries return ordered results."""
        mock_users = [
            User(id=3, email="user3@example.com", username="user3", hashed_password="pass"),
            User(id=1, email="user1@example.com", username="user1", hashed_password="pass"),
            User(id=2, email="user2@example.com", username="user2", hashed_password="pass")
        ]
        
        # Mock database query returning ordered results
        mock_result = AsyncMock()
        mock_result.scalars = AsyncMock(return_value=AsyncMock(all=AsyncMock(return_value=sorted(mock_users, key=lambda x: x.id))))
        self.mock_session.execute.return_value = mock_result
        
        # Execute
        result = await self.user_repo.get_all()
        
        # Assert
        assert result[0].id == 1
        assert result[1].id == 2
        assert result[2].id == 3
    
    async def test_batch_operations(self):
        """Test batch operation performance."""
        user_ids = [1, 2, 3, 4, 5]
        mock_users = [User(id=i, email=f"user{i}@example.com", username=f"user{i}", hashed_password="pass") for i in user_ids]
        
        # Mock individual queries
        mock_results = []
        for user in mock_users:
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none.return_value = user
            mock_results.append(mock_result)
        
        self.mock_session.execute.side_effect = mock_results
        
        # Execute batch operations
        results = []
        for user_id in user_ids:
            user = await self.user_repo.get_by_id(user_id)
            results.append(user)
        
        # Assert
        assert len(results) == 5
        assert all(user is not None for user in results)
        assert self.mock_session.execute.call_count == 5
