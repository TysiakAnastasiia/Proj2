
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from app.services import (
    AuthService, UserService, BookService, ReviewService, 
    ExchangeService, WishlistService, ChatService, FriendshipService
)
from app.models import User, Book, Review, Exchange, WishlistItem, Message, Friendship
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.observer import EventManager, EventType, Event


class TestAuthService:
    """Test AuthService functionality."""
    
    def setup_method(self):
        """Setup test dependencies."""
        self.mock_user_repo = AsyncMock()
        self.mock_event_manager = AsyncMock()
        self.auth_service = AuthService(
            user_repository=self.mock_user_repo,
            event_manager=self.mock_event_manager
        )
    
    async def test_register_user_success(self):
        """Test successful user registration."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "pass",
            "full_name": "Test User"
        }
        
        # Mock repository response
        mock_user = User(
            id=1,
            email=user_data["email"],
            username=user_data["username"],
            hashed_password="hashed_pass",
            full_name=user_data["full_name"]
        )
        self.mock_user_repo.get_by_email.return_value = None
        self.mock_user_repo.get_by_username.return_value = None
        self.mock_user_repo.create.return_value = mock_user
        
        with patch('app.core.security.get_password_hash', return_value="hashed_pass"):
            # Execute
            result = await self.auth_service.register_user(user_data)
        
        # Assert
        assert result.email == user_data["email"]
        assert result.username == user_data["username"]
        self.mock_user_repo.create.assert_called_once()
        
        # Verify event was sent
        self.mock_event_manager.notify.assert_called_once()
        event_call = self.mock_event_manager.notify.call_args[0][0]
        assert event_call.event_type == EventType.USER_REGISTERED
    
    async def test_register_user_duplicate_email(self):
        """Test registration with duplicate email."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "pass"
        }
        
        # Mock existing user
        existing_user = User(id=1, email=user_data["email"], username="other", hashed_password="pass")
        self.mock_user_repo.get_by_email.return_value = existing_user
        
        # Execute and assert
        with pytest.raises(ValueError, match="Email already registered"):
            await self.auth_service.register_user(user_data)
    
    async def test_register_user_duplicate_username(self):
        """Test registration with duplicate username."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "pass"
        }
        
        # Mock existing user
        existing_user = User(id=1, email="other@example.com", username=user_data["username"], hashed_password="pass")
        self.mock_user_repo.get_by_email.return_value = None
        self.mock_user_repo.get_by_username.return_value = existing_user
        
        # Execute and assert
        with pytest.raises(ValueError, match="Username already taken"):
            await self.auth_service.register_user(user_data)
    
    async def test_login_success(self):
        """Test successful login."""
        login_data = {
            "email": "test@example.com",
            "password": "pass"
        }
        
        # Mock user with hashed password
        mock_user = User(
            id=1,
            email=login_data["email"],
            username="testuser",
            hashed_password="dummy_hash",
            is_active=True
        )
        self.mock_user_repo.get_by_email.return_value = mock_user
        
        # Execute
        result = await self.auth_service.login(login_data)
        
        # Assert
        assert "access_token" in result
        assert "token_type" in result
        assert result["token_type"] == "bearer"
        assert result["user"]["email"] == login_data["email"]
    
    async def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        # Mock user with different password
        hashed_password = get_password_hash("correctpassword")
        mock_user = User(
            id=1,
            email=login_data["email"],
            username="testuser",
            hashed_password=hashed_password,
            is_active=True
        )
        self.mock_user_repo.get_by_email.return_value = mock_user
        
        # Execute and assert
        with pytest.raises(ValueError, match="Invalid credentials"):
            await self.auth_service.login(login_data)
    
    async def test_login_user_not_found(self):
        """Test login with non-existent user."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password"
        }
        
        # Mock user not found
        self.mock_user_repo.get_by_email.return_value = None
        
        # Execute and assert
        with pytest.raises(ValueError, match="Invalid credentials"):
            await self.auth_service.login(login_data)
    
    async def test_login_inactive_user(self):
        """Test login with inactive user."""
        login_data = {
            "email": "test@example.com",
            "password": "pass"
        }
        
        # Mock inactive user
        hashed_password = get_password_hash(login_data["password"])
        mock_user = User(
            id=1,
            email=login_data["email"],
            username="testuser",
            hashed_password=hashed_password,
            is_active=False
        )
        self.mock_user_repo.get_by_email.return_value = mock_user
        
        # Execute and assert
        with pytest.raises(ValueError, match="Account is inactive"):
            await self.auth_service.login(login_data)
    
    async def test_get_current_user_success(self):
        """Test getting current user from token."""
        # Mock user
        mock_user = User(id=1, email="test@example.com", username="test", hashed_password="pass")
        self.mock_user_repo.get_by_id.return_value = mock_user
        
        # Execute
        result = await self.auth_service.get_current_user(1)
        
        # Assert
        assert result.id == 1
        assert result.email == "test@example.com"
        self.mock_user_repo.get_by_id.assert_called_once_with(1)
    
    async def test_get_current_user_not_found(self):
        """Test getting current user when user doesn't exist."""
        # Mock user not found
        self.mock_user_repo.get_by_id.return_value = None
        
        # Execute and assert
        with pytest.raises(ValueError, match="User not found"):
            await self.auth_service.get_current_user(999)


class TestUserService:
    """Test UserService functionality."""
    
    def setup_method(self):
        """Setup test dependencies."""
        self.mock_user_repo = AsyncMock()
        self.mock_event_manager = AsyncMock()
        self.user_service = UserService(
            user_repository=self.mock_user_repo,
            event_manager=self.mock_event_manager
        )
    
    async def test_get_user_by_id_success(self):
        """Test getting user by ID."""
        # Mock user
        mock_user = User(id=1, email="test@example.com", username="test", hashed_password="pass")
        self.mock_user_repo.get_by_id.return_value = mock_user
        
        # Execute
        result = await self.user_service.get_user_by_id(1)
        
        # Assert
        assert result.id == 1
        assert result.email == "test@example.com"
        self.mock_user_repo.get_by_id.assert_called_once_with(1)
    
    async def test_get_user_by_id_not_found(self):
        """Test getting user by ID when not found."""
        # Mock user not found
        self.mock_user_repo.get_by_id.return_value = None
        
        # Execute and assert
        with pytest.raises(ValueError, match="User not found"):
            await self.user_service.get_user_by_id(999)
    
    async def test_get_user_by_email_success(self):
        """Test getting user by email."""
        # Mock user
        mock_user = User(id=1, email="test@example.com", username="test", hashed_password="pass")
        self.mock_user_repo.get_by_email.return_value = mock_user
        
        # Execute
        result = await self.user_service.get_user_by_email("test@example.com")
        
        # Assert
        assert result.email == "test@example.com"
        self.mock_user_repo.get_by_email.assert_called_once_with("test@example.com")
    
    async def test_update_user_profile_success(self):
        """Test updating user profile."""
        user_id = 1
        update_data = {
            "full_name": "Updated Name",
            "bio": "Updated bio",
            "city": "Updated City"
        }
        
        # Mock existing user
        mock_user = User(id=user_id, email="test@example.com", username="test", hashed_password="pass")
        self.mock_user_repo.get_by_id.return_value = mock_user
        
        # Mock updated user
        updated_user = User(
            id=user_id,
            email="test@example.com",
            username="test",
            hashed_password="pass",
            full_name=update_data["full_name"],
            bio=update_data["bio"],
            city=update_data["city"]
        )
        self.mock_user_repo.update.return_value = updated_user
        
        # Execute
        result = await self.user_service.update_user_profile(user_id, update_data)
        
        # Assert
        assert result.full_name == update_data["full_name"]
        assert result.bio == update_data["bio"]
        assert result.city == update_data["city"]
        self.mock_user_repo.update.assert_called_once()
    
    async def test_update_user_profile_not_found(self):
        """Test updating profile for non-existent user."""
        # Mock user not found
        self.mock_user_repo.get_by_id.return_value = None
        
        # Execute and assert
        with pytest.raises(ValueError, match="User not found"):
            await self.user_service.update_user_profile(999, {"full_name": "Test"})
    
    async def test_deactivate_user_success(self):
        """Test deactivating a user."""
        user_id = 1
        
        # Mock existing user
        mock_user = User(id=user_id, email="test@example.com", username="test", hashed_password="pass", is_active=True)
        self.mock_user_repo.get_by_id.return_value = mock_user
        
        # Mock deactivated user
        deactivated_user = User(id=user_id, email="test@example.com", username="test", hashed_password="pass", is_active=False)
        self.mock_user_repo.update.return_value = deactivated_user
        
        # Execute
        result = await self.user_service.deactivate_user(user_id)
        
        # Assert
        assert result.is_active is False
        self.mock_user_repo.update.assert_called_once()
    
    async def test_search_users_success(self):
        """Test searching users."""
        query = "test"
        limit = 10
        
        # Mock search results
        mock_users = [
            User(id=1, email="test1@example.com", username="test1", hashed_password="pass"),
            User(id=2, email="test2@example.com", username="test2", hashed_password="pass")
        ]
        self.mock_user_repo.search.return_value = mock_users
        
        # Execute
        result = await self.user_service.search_users(query, limit)
        
        # Assert
        assert len(result) == 2
        assert result[0].username == "test1"
        assert result[1].username == "test2"
        self.mock_user_repo.search.assert_called_once_with(query, limit)


class TestBookService:
    """Test BookService functionality."""
    
    def setup_method(self):
        """Setup test dependencies."""
        self.mock_book_repo = AsyncMock()
        self.mock_user_repo = AsyncMock()
        self.mock_event_manager = AsyncMock()
        self.book_service = BookService(
            book_repository=self.mock_book_repo,
            user_repository=self.mock_user_repo,
            event_manager=self.mock_event_manager
        )
    
    async def test_create_book_success(self):
        """Test creating a book."""
        user_id = 1
        book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "isbn": "978-3-16-148410-0",
            "description": "Test description",
            "genre": "Fiction",
            "year_published": 2023,
            "pages": 250,
            "language": "English"
        }
        
        # Mock user exists
        mock_user = User(id=user_id, email="test@example.com", username="test", hashed_password="pass")
        self.mock_user_repo.get_by_id.return_value = mock_user
        
        # Mock created book
        mock_book = Book(id=1, owner_id=user_id, **book_data)
        self.mock_book_repo.create.return_value = mock_book
        
        # Execute
        result = await self.book_service.create_book(user_id, book_data)
        
        # Assert
        assert result.title == book_data["title"]
        assert result.author == book_data["author"]
        assert result.owner_id == user_id
        self.mock_book_repo.create.assert_called_once()
        
        # Verify event was sent
        self.mock_event_manager.notify.assert_called_once()
        event_call = self.mock_event_manager.notify.call_args[0][0]
        assert event_call.event_type == EventType.BOOK_CREATED
    
    async def test_create_book_user_not_found(self):
        """Test creating book for non-existent user."""
        user_id = 999
        book_data = {"title": "Test Book", "author": "Test Author"}
        
        # Mock user not found
        self.mock_user_repo.get_by_id.return_value = None
        
        # Execute and assert
        with pytest.raises(ValueError, match="User not found"):
            await self.book_service.create_book(user_id, book_data)
    
    async def test_get_book_by_id_success(self):
        """Test getting book by ID."""
        # Mock book
        mock_book = Book(id=1, title="Test Book", author="Test Author", owner_id=1)
        self.mock_book_repo.get_by_id.return_value = mock_book
        
        # Execute
        result = await self.book_service.get_book_by_id(1)
        
        # Assert
        assert result.id == 1
        assert result.title == "Test Book"
        self.mock_book_repo.get_by_id.assert_called_once_with(1)
    
    async def test_get_book_by_id_not_found(self):
        """Test getting book by ID when not found."""
        # Mock book not found
        self.mock_book_repo.get_by_id.return_value = None
        
        # Execute and assert
        with pytest.raises(ValueError, match="Book not found"):
            await self.book_service.get_book_by_id(999)
    
    async def test_update_book_success(self):
        """Test updating a book."""
        book_id = 1
        user_id = 1
        update_data = {
            "title": "Updated Title",
            "description": "Updated description"
        }
        
        # Mock existing book
        mock_book = Book(id=book_id, title="Original Title", author="Test Author", owner_id=user_id)
        self.mock_book_repo.get_by_id.return_value = mock_book
        
        # Mock updated book
        updated_book = Book(
            id=book_id,
            title=update_data["title"],
            author="Test Author",
            owner_id=user_id,
            description=update_data["description"]
        )
        self.mock_book_repo.update.return_value = updated_book
        
        # Execute
        result = await self.book_service.update_book(book_id, user_id, update_data)
        
        # Assert
        assert result.title == update_data["title"]
        assert result.description == update_data["description"]
        self.mock_book_repo.update.assert_called_once()
    
    async def test_update_book_unauthorized(self):
        """Test updating book by non-owner."""
        book_id = 1
        user_id = 2  # Different user
        update_data = {"title": "Updated Title"}
        
        # Mock book owned by different user
        mock_book = Book(id=book_id, title="Test Book", author="Test Author", owner_id=1)
        self.mock_book_repo.get_by_id.return_value = mock_book
        
        # Execute and assert
        with pytest.raises(ValueError, match="Not authorized to update this book"):
            await self.book_service.update_book(book_id, user_id, update_data)
    
    async def test_delete_book_success(self):
        """Test deleting a book."""
        book_id = 1
        user_id = 1
        
        # Mock existing book
        mock_book = Book(id=book_id, title="Test Book", author="Test Author", owner_id=user_id)
        self.mock_book_repo.get_by_id.return_value = mock_book
        self.mock_book_repo.delete.return_value = True
        
        # Execute
        result = await self.book_service.delete_book(book_id, user_id)
        
        # Assert
        assert result is True
        self.mock_book_repo.delete.assert_called_once_with(book_id)
    
    async def test_delete_book_unauthorized(self):
        """Test deleting book by non-owner."""
        book_id = 1
        user_id = 2  # Different user
        
        # Mock book owned by different user
        mock_book = Book(id=book_id, title="Test Book", author="Test Author", owner_id=1)
        self.mock_book_repo.get_by_id.return_value = mock_book
        
        # Execute and assert
        with pytest.raises(ValueError, match="Not authorized to delete this book"):
            await self.book_service.delete_book(book_id, user_id)
    
    async def test_search_books_success(self):
        """Test searching books."""
        query = "test"
        filters = {"genre": "Fiction", "language": "English"}
        limit = 10
        
        # Mock search results
        mock_books = [
            Book(id=1, title="Test Book 1", author="Author 1", owner_id=1),
            Book(id=2, title="Test Book 2", author="Author 2", owner_id=2)
        ]
        self.mock_book_repo.search.return_value = mock_books
        
        # Execute
        result = await self.book_service.search_books(query, filters, limit)
        
        # Assert
        assert len(result) == 2
        assert result[0].title == "Test Book 1"
        assert result[1].title == "Test Book 2"
        self.mock_book_repo.search.assert_called_once_with(query, filters, limit)
    
    async def test_get_user_books_success(self):
        """Test getting books owned by a user."""
        user_id = 1
        
        # Mock user's books
        mock_books = [
            Book(id=1, title="Book 1", author="Author 1", owner_id=user_id),
            Book(id=2, title="Book 2", author="Author 2", owner_id=user_id)
        ]
        self.mock_book_repo.get_by_owner_id.return_value = mock_books
        
        # Execute
        result = await self.book_service.get_user_books(user_id)
        
        # Assert
        assert len(result) == 2
        assert all(book.owner_id == user_id for book in result)
        self.mock_book_repo.get_by_owner_id.assert_called_once_with(user_id)


class TestReviewService:
    """Test ReviewService functionality."""
    
    def setup_method(self):
        """Setup test dependencies."""
        self.mock_review_repo = AsyncMock()
        self.mock_book_repo = AsyncMock()
        self.mock_user_repo = AsyncMock()
        self.mock_event_manager = AsyncMock()
        self.review_service = ReviewService(
            review_repository=self.mock_review_repo,
            book_repository=self.mock_book_repo,
            user_repository=self.mock_user_repo,
            event_manager=self.mock_event_manager
        )
    
    async def test_create_review_success(self):
        """Test creating a review."""
        user_id = 1
        book_id = 1
        review_data = {
            "rating": 4,
            "title": "Great Book",
            "content": "I really enjoyed this book."
        }
        
        # Mock user and book exist
        mock_user = User(id=user_id, email="test@example.com", username="test", hashed_password="pass")
        mock_book = Book(id=book_id, title="Test Book", author="Test Author", owner_id=2)
        self.mock_user_repo.get_by_id.return_value = mock_user
        self.mock_book_repo.get_by_id.return_value = mock_book
        
        # Mock no existing review by this user for this book
        self.mock_review_repo.get_user_review_for_book.return_value = None
        
        # Mock created review
        mock_review = Review(id=1, user_id=user_id, book_id=book_id, **review_data)
        self.mock_review_repo.create.return_value = mock_review
        
        # Execute
        # Create ReviewCreate object
        from app.schemas import ReviewCreate
        review_create_data = ReviewCreate(book_id=book_id, **review_data)
        result = await self.review_service.create_review(review_create_data, user_id)
        
        # Assert
        assert result.rating == review_data["rating"]
        assert result.user_id == user_id
        assert result.book_id == book_id
        self.mock_review_repo.create.assert_called_once()
        
        # Verify event was sent
        self.mock_event_manager.notify.assert_called_once()
        event_call = self.mock_event_manager.notify.call_args[0][0]
        assert event_call.event_type == EventType.REVIEW_CREATED
    
    async def test_create_review_duplicate(self):
        """Test creating duplicate review for same user and book."""
        user_id = 1
        book_id = 1
        review_data = {"rating": 4, "title": "Great Book"}
        
        # Mock existing review
        existing_review = Review(id=1, user_id=user_id, book_id=book_id, rating=3)
        self.mock_review_repo.get_by_user_and_book.return_value = existing_review
        
        # Execute and assert
        with pytest.raises(ValueError, match="User has already reviewed this book"):
            await self.review_service.create_review(user_id, book_id, review_data)
    
    async def test_create_review_invalid_rating(self):
        """Test creating review with invalid rating."""
        user_id = 1
        book_id = 1
        review_data = {"rating": 6}  # Invalid rating (> 5)
        
        # Execute and assert
        with pytest.raises(ValueError, match="Rating must be between 1 and 5"):
            await self.review_service.create_review(user_id, book_id, review_data)
    
    async def test_get_book_reviews_success(self):
        """Test getting reviews for a book."""
        book_id = 1
        
        # Mock book exists
        mock_book = Book(id=book_id, title="Test Book", author="Test Author", owner_id=1)
        self.mock_book_repo.get_by_id.return_value = mock_book
        
        # Mock reviews
        mock_reviews = [
            Review(id=1, user_id=1, book_id=book_id, rating=4),
            Review(id=2, user_id=2, book_id=book_id, rating=5)
        ]
        self.mock_review_repo.get_by_book_id.return_value = mock_reviews
        
        # Execute
        result = await self.review_service.get_book_reviews(book_id)
        
        # Assert
        assert len(result) == 2
        assert all(review.book_id == book_id for review in result)
        self.mock_review_repo.get_by_book_id.assert_called_once_with(book_id)
    
    async def test_update_review_success(self):
        """Test updating a review."""
        review_id = 1
        user_id = 1
        update_data = {
            "rating": 5,
            "title": "Updated Title",
            "content": "Updated content"
        }
        
        # Mock existing review by this user
        mock_review = Review(id=review_id, user_id=user_id, book_id=1, rating=4)
        self.mock_review_repo.get_by_id.return_value = mock_review
        
        # Mock updated review
        updated_review = Review(
            id=review_id,
            user_id=user_id,
            book_id=1,
            rating=update_data["rating"],
            title=update_data["title"],
            content=update_data["content"]
        )
        self.mock_review_repo.update.return_value = updated_review
        
        # Execute
        result = await self.review_service.update_review(review_id, user_id, update_data)
        
        # Assert
        assert result.rating == update_data["rating"]
        assert result.title == update_data["title"]
        self.mock_review_repo.update.assert_called_once()
    
    async def test_update_review_unauthorized(self):
        """Test updating review by non-owner."""
        review_id = 1
        user_id = 2  # Different user
        update_data = {"rating": 5}
        
        # Mock review owned by different user
        mock_review = Review(id=review_id, user_id=1, book_id=1, rating=4)
        self.mock_review_repo.get_by_id.return_value = mock_review
        
        # Execute and assert
        with pytest.raises(ValueError, match="Not authorized to update this review"):
            await self.review_service.update_review(review_id, user_id, update_data)
    
    async def test_delete_review_success(self):
        """Test deleting a review."""
        review_id = 1
        user_id = 1
        
        # Mock existing review by this user
        mock_review = Review(id=review_id, user_id=user_id, book_id=1, rating=4)
        self.mock_review_repo.get_by_id.return_value = mock_review
        self.mock_review_repo.delete.return_value = True
        
        # Execute
        result = await self.review_service.delete_review(review_id, user_id)
        
        # Assert
        assert result is True
        self.mock_review_repo.delete.assert_called_once_with(review_id)
    
    async def test_delete_review_unauthorized(self):
        """Test deleting review by non-owner."""
        review_id = 1
        user_id = 2  # Different user
        
        # Mock review owned by different user
        mock_review = Review(id=review_id, user_id=1, book_id=1, rating=4)
        self.mock_review_repo.get_by_id.return_value = mock_review
        
        # Execute and assert
        with pytest.raises(ValueError, match="Not authorized to delete this review"):
            await self.review_service.delete_review(review_id, user_id)


class TestExchangeService:
    """Test ExchangeService functionality."""
    
    def setup_method(self):
        """Setup test dependencies."""
        self.mock_exchange_repo = AsyncMock()
        self.mock_book_repo = AsyncMock()
        self.mock_user_repo = AsyncMock()
        self.mock_event_manager = AsyncMock()
        self.exchange_service = ExchangeService(
            exchange_repository=self.mock_exchange_repo,
            book_repository=self.mock_book_repo,
            user_repository=self.mock_user_repo,
            event_manager=self.mock_event_manager
        )
    
    async def test_create_exchange_request_success(self):
        """Test creating an exchange request."""
        requester_id = 1
        requested_user_id = 2
        offered_book_id = 1
        requested_book_id = 2
        message = "I'd like to exchange books!"
        
        # Mock users exist
        requester = User(id=requester_id, email="requester@example.com", username="requester", hashed_password="pass")
        requested_user = User(id=requested_user_id, email="requested@example.com", username="requested", hashed_password="pass")
        self.mock_user_repo.get_by_id.side_effect = [requester, requested_user]
        
        # Mock books exist and are available
        requested_book = Book(id=requested_book_id, title="Requested Book", author="Author", owner_id=requested_user_id, is_available=True)
        offered_book = Book(id=offered_book_id, title="Offered Book", author="Author", owner_id=requester_id, is_available=True)
        self.mock_book_repo.get_by_id.side_effect = [requested_book, offered_book]
        
        # Mock no existing exchange
        self.mock_exchange_repo.get_active_exchange.return_value = None
        
        # Mock created exchange
        mock_exchange = Exchange(
            id=1,
            requester_id=requester_id,
            requested_user_id=requested_user_id,
            offered_book_id=offered_book_id,
            requested_book_id=requested_book_id,
            message=message,
            status="pending"
        )
        self.mock_exchange_repo.create.return_value = mock_exchange
        
        # Execute
        result = await self.exchange_service.create_exchange_request(
            requester_id, requested_user_id, offered_book_id, requested_book_id, message
        )
        
        # Assert
        assert result.requester_id == requester_id
        assert result.requested_user_id == requested_user_id
        assert result.status == "pending"
        self.mock_exchange_repo.create.assert_called_once()
        
        # Verify event was sent
        self.mock_event_manager.notify.assert_called_once()
        event_call = self.mock_event_manager.notify.call_args[0][0]
        assert event_call.event_type == EventType.EXCHANGE_CREATED
    
    async def test_create_exchange_request_same_user(self):
        """Test creating exchange request with same user."""
        user_id = 1
        
        # Execute and assert
        with pytest.raises(ValueError, match="Cannot create exchange request with yourself"):
            await self.exchange_service.create_exchange_request(user_id, user_id, 1, 2)
    
    async def test_create_exchange_request_book_not_available(self):
        """Test creating exchange request with unavailable book."""
        requester_id = 1
        requested_user_id = 2
        offered_book_id = 1
        requested_book_id = 2
        
        # Mock users exist
        requester = User(id=requester_id, email="requester@example.com", username="requester", hashed_password="pass")
        requested_user = User(id=requested_user_id, email="requested@example.com", username="requested", hashed_password="pass")
        self.mock_user_repo.get_by_id.side_effect = [requester, requested_user]
        
        # Mock offered book is not available
        offered_book = Book(id=offered_book_id, title="Offered Book", author="Author", owner_id=requester_id, is_available=False)
        requested_book = Book(id=requested_book_id, title="Requested Book", author="Author", owner_id=requested_user_id, is_available=True)
        
        # Mock book repository to return different books based on ID
        def mock_get_by_id(book_id):
            if book_id == offered_book_id:
                return offered_book
            elif book_id == requested_book_id:
                return requested_book
            return None
        
        self.mock_book_repo.get_by_id.side_effect = mock_get_by_id
        
        # Execute and assert
        with pytest.raises(ValueError, match="Book is not available for exchange"):
            await self.exchange_service.create_exchange_request(
                requester_id, requested_user_id, offered_book_id, requested_book_id
            )
    
    async def test_accept_exchange_success(self):
        """Test accepting an exchange."""
        exchange_id = 1
        user_id = 2  # Requested user
        
        # Mock exchange exists and is pending
        mock_exchange = Exchange(
            id=exchange_id,
            requester_id=1,
            requested_user_id=user_id,
            offered_book_id=1,
            requested_book_id=2,
            status="pending"
        )
        self.mock_exchange_repo.get_by_id.return_value = mock_exchange
        
        # Mock books
        offered_book = Book(id=1, title="Offered Book", author="Author", owner_id=1, is_available=True)
        requested_book = Book(id=2, title="Requested Book", author="Author", owner_id=user_id, is_available=True)
        self.mock_book_repo.get_by_id.side_effect = [offered_book, requested_book]
        
        # Mock updated exchange
        updated_exchange = Exchange(
            id=exchange_id,
            requester_id=1,
            requested_user_id=user_id,
            offered_book_id=1,
            requested_book_id=2,
            status="accepted"
        )
        self.mock_exchange_repo.update.return_value = updated_exchange
        
        # Execute
        result = await self.exchange_service.accept_exchange(exchange_id, user_id)
        
        # Assert
        assert result.status == "accepted"
        self.mock_exchange_repo.update.assert_called_once()
        
        # Verify books are marked as unavailable
        assert self.mock_book_repo.update.call_count == 2
        
        # Verify events were sent
        assert self.mock_event_manager.notify.call_count >= 1
    
    async def test_accept_exchange_unauthorized(self):
        """Test accepting exchange by unauthorized user."""
        exchange_id = 1
        user_id = 3  # Neither requester nor requested user
        
        # Mock exchange
        mock_exchange = Exchange(
            id=exchange_id,
            requester_id=1,
            requested_user_id=2,
            offered_book_id=1,
            requested_book_id=2,
            status="pending"
        )
        self.mock_exchange_repo.get_by_id.return_value = mock_exchange
        
        # Execute and assert
        with pytest.raises(ValueError, match="Not authorized to accept this exchange"):
            await self.exchange_service.accept_exchange(exchange_id, user_id)
    
    async def test_reject_exchange_success(self):
        """Test rejecting an exchange."""
        exchange_id = 1
        user_id = 2  # Requested user
        
        # Mock exchange exists and is pending
        mock_exchange = Exchange(
            id=exchange_id,
            requester_id=1,
            requested_user_id=user_id,
            offered_book_id=1,
            requested_book_id=2,
            status="pending"
        )
        self.mock_exchange_repo.get_by_id.return_value = mock_exchange
        
        # Mock updated exchange
        updated_exchange = Exchange(
            id=exchange_id,
            requester_id=1,
            requested_user_id=user_id,
            offered_book_id=1,
            requested_book_id=2,
            status="rejected"
        )
        self.mock_exchange_repo.update.return_value = updated_exchange
        
        # Execute
        result = await self.exchange_service.reject_exchange(exchange_id, user_id)
        
        # Assert
        assert result.status == "rejected"
        self.mock_exchange_repo.update.assert_called_once()
    
    async def test_complete_exchange_success(self):
        """Test completing an exchange."""
        exchange_id = 1
        user_id = 1  # Requester
        
        # Mock exchange exists and is accepted
        mock_exchange = Exchange(
            id=exchange_id,
            requester_id=user_id,
            requested_user_id=2,
            offered_book_id=1,
            requested_book_id=2,
            status="accepted"
        )
        self.mock_exchange_repo.get_by_id.return_value = mock_exchange
        
        # Mock books
        offered_book = Book(id=1, title="Offered Book", author="Author", owner_id=1, is_available=False)
        requested_book = Book(id=2, title="Requested Book", author="Author", owner_id=2, is_available=False)
        self.mock_book_repo.get_by_id.side_effect = [offered_book, requested_book]
        
        # Mock updated exchange
        completed_exchange = Exchange(
            id=exchange_id,
            requester_id=user_id,
            requested_user_id=2,
            offered_book_id=1,
            requested_book_id=2,
            status="completed"
        )
        self.mock_exchange_repo.update.return_value = completed_exchange
        
        # Execute
        result = await self.exchange_service.complete_exchange(exchange_id, user_id)
        
        # Assert
        assert result.status == "completed"
        self.mock_exchange_repo.update.assert_called_once()
        
        # Verify book ownership was transferred
        assert self.mock_book_repo.update.call_count == 2
    
    async def test_get_user_exchanges_success(self):
        """Test getting exchanges for a user."""
        user_id = 1
        
        # Mock exchanges
        mock_exchanges = [
            Exchange(id=1, requester_id=user_id, requested_user_id=2, offered_book_id=1, requested_book_id=2, status="pending"),
            Exchange(id=2, requester_id=2, requested_user_id=user_id, offered_book_id=3, requested_book_id=4, status="accepted")
        ]
        self.mock_exchange_repo.get_by_user_id.return_value = mock_exchanges
        
        # Execute
        result = await self.exchange_service.get_user_exchanges(user_id)
        
        # Assert
        assert len(result) == 2
        assert all(
            exchange.requester_id == user_id or exchange.requested_user_id == user_id
            for exchange in result
        )
        self.mock_exchange_repo.get_by_user_id.assert_called_once_with(user_id)


class TestWishlistService:
    """Test WishlistService functionality."""
    
    def setup_method(self):
        """Setup test dependencies."""
        self.mock_wishlist_repo = AsyncMock()
        self.mock_book_repo = AsyncMock()
        self.mock_user_repo = AsyncMock()
        self.wishlist_service = WishlistService(
            wishlist_repository=self.mock_wishlist_repo,
            book_repository=self.mock_book_repo,
            user_repository=self.mock_user_repo
        )
    
    async def test_add_to_wishlist_success(self):
        """Test adding book to wishlist."""
        user_id = 1
        book_id = 1
        priority = "high"
        notes = "Really want this book!"
        
        # Mock user and book exist
        mock_user = User(id=user_id, email="test@example.com", username="test", hashed_password="pass")
        mock_book = Book(id=book_id, title="Test Book", author="Test Author", owner_id=2)
        self.mock_user_repo.get_by_id.return_value = mock_user
        self.mock_book_repo.get_by_id.return_value = mock_book
        
        # Mock no existing wishlist item
        self.mock_wishlist_repo.get_by_user_and_book.return_value = None
        
        # Mock created wishlist item
        mock_item = WishlistItem(id=1, user_id=user_id, book_id=book_id, priority=priority, notes=notes)
        self.mock_wishlist_repo.create.return_value = mock_item
        
        # Execute
        result = await self.wishlist_service.add_to_wishlist(user_id, book_id, priority, notes)
        
        # Assert
        assert result.user_id == user_id
        assert result.book_id == book_id
        assert result.priority == priority
        self.mock_wishlist_repo.create.assert_called_once()
    
    async def test_add_to_wishlist_duplicate(self):
        """Test adding duplicate book to wishlist."""
        user_id = 1
        book_id = 1
        
        # Mock existing wishlist item
        existing_item = WishlistItem(id=1, user_id=user_id, book_id=book_id, priority="medium")
        self.mock_wishlist_repo.get_by_user_and_book.return_value = existing_item
        
        # Execute and assert
        with pytest.raises(ValueError, match="Book already in wishlist"):
            await self.wishlist_service.add_to_wishlist(user_id, book_id)
    
    async def test_remove_from_wishlist_success(self):
        """Test removing book from wishlist."""
        user_id = 1
        book_id = 1
        
        # Mock existing wishlist item
        mock_item = WishlistItem(id=1, user_id=user_id, book_id=book_id, priority="high")
        self.mock_wishlist_repo.get_by_user_and_book.return_value = mock_item
        self.mock_wishlist_repo.delete.return_value = True
        
        # Execute
        result = await self.wishlist_service.remove_from_wishlist(user_id, book_id)
        
        # Assert
        assert result is True
        self.mock_wishlist_repo.delete.assert_called_once_with(mock_item.id)
    
    async def test_get_user_wishlist_success(self):
        """Test getting user's wishlist."""
        user_id = 1
        
        # Mock wishlist items
        mock_items = [
            WishlistItem(id=1, user_id=user_id, book_id=1, priority="high"),
            WishlistItem(id=2, user_id=user_id, book_id=2, priority="medium"),
            WishlistItem(id=3, user_id=user_id, book_id=3, priority="low")
        ]
        self.mock_wishlist_repo.get_by_user_id.return_value = mock_items
        
        # Execute
        result = await self.wishlist_service.get_user_wishlist(user_id)
        
        # Assert
        assert len(result) == 3
        assert all(item.user_id == user_id for item in result)
        self.mock_wishlist_repo.get_by_user_id.assert_called_once_with(user_id)
    
    async def test_update_wishlist_item_success(self):
        """Test updating wishlist item."""
        user_id = 1
        book_id = 1
        update_data = {"priority": "low", "notes": "Updated notes"}
        
        # Mock existing wishlist item
        mock_item = WishlistItem(id=1, user_id=user_id, book_id=book_id, priority="high")
        self.mock_wishlist_repo.get_by_user_and_book.return_value = mock_item
        
        # Mock updated item
        updated_item = WishlistItem(
            id=1,
            user_id=user_id,
            book_id=book_id,
            priority=update_data["priority"],
            notes=update_data["notes"]
        )
        self.mock_wishlist_repo.update.return_value = updated_item
        
        # Execute
        result = await self.wishlist_service.update_wishlist_item(user_id, book_id, update_data)
        
        # Assert
        assert result.priority == update_data["priority"]
        assert result.notes == update_data["notes"]
        self.mock_wishlist_repo.update.assert_called_once()


class TestChatService:
    """Test ChatService functionality."""
    
    def setup_method(self):
        """Setup test dependencies."""
        self.mock_message_repo = AsyncMock()
        self.mock_user_repo = AsyncMock()
        self.mock_event_manager = AsyncMock()
        self.chat_service = ChatService(
            message_repository=self.mock_message_repo,
            user_repository=self.mock_user_repo,
            event_manager=self.mock_event_manager
        )
    
    async def test_send_message_success(self):
        """Test sending a message."""
        sender_id = 1
        receiver_id = 2
        content = "Hello, I'd like to discuss the book exchange!"
        
        # Mock users exist
        sender = User(id=sender_id, email="sender@example.com", username="sender", hashed_password="pass")
        receiver = User(id=receiver_id, email="receiver@example.com", username="receiver", hashed_password="pass")
        self.mock_user_repo.get_by_id.side_effect = [sender, receiver]
        
        # Mock created message
        mock_message = Message(
            id=1,
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            is_read=False
        )
        self.mock_message_repo.create.return_value = mock_message
        
        # Execute
        result = await self.chat_service.send_message(sender_id, receiver_id, content)
        
        # Assert
        assert result.sender_id == sender_id
        assert result.receiver_id == receiver_id
        assert result.content == content
        assert result.is_read is False
        self.mock_message_repo.create.assert_called_once()
        
        # Verify event was sent
        self.mock_event_manager.notify.assert_called_once()
        event_call = self.mock_event_manager.notify.call_args[0][0]
        assert event_call.event_type == EventType.MESSAGE_SENT
    
    async def test_send_message_to_self(self):
        """Test sending message to self."""
        user_id = 1
        content = "Hello myself"
        
        # Execute and assert
        with pytest.raises(ValueError, match="Cannot send message to yourself"):
            await self.chat_service.send_message(user_id, user_id, content)
    
    async def test_send_message_user_not_found(self):
        """Test sending message to non-existent user."""
        sender_id = 1
        receiver_id = 999
        content = "Hello"
        
        # Mock sender exists but receiver doesn't
        sender = User(id=sender_id, email="sender@example.com", username="sender", hashed_password="pass")
        self.mock_user_repo.get_by_id.side_effect = [sender, None]
        
        # Execute and assert
        with pytest.raises(ValueError, match="Receiver not found"):
            await self.chat_service.send_message(sender_id, receiver_id, content)
    
    async def test_get_conversation_success(self):
        """Test getting conversation between two users."""
        user_id = 1
        other_user_id = 2
        limit = 50
        
        # Mock messages
        mock_messages = [
            Message(id=1, sender_id=user_id, receiver_id=other_user_id, content="Hello", is_read=True),
            Message(id=2, sender_id=other_user_id, receiver_id=user_id, content="Hi there!", is_read=True),
            Message(id=3, sender_id=user_id, receiver_id=other_user_id, content="How are you?", is_read=False)
        ]
        self.mock_message_repo.get_conversation.return_value = mock_messages
        
        # Execute
        result = await self.chat_service.get_conversation(user_id, other_user_id, limit)
        
        # Assert
        assert len(result) == 3
        assert all(
            (msg.sender_id == user_id and msg.receiver_id == other_user_id) or
            (msg.sender_id == other_user_id and msg.receiver_id == user_id)
            for msg in result
        )
        self.mock_message_repo.get_conversation.assert_called_once_with(user_id, other_user_id, limit)
    
    async def test_mark_message_as_read_success(self):
        """Test marking message as read."""
        message_id = 1
        user_id = 2  # Receiver
        
        # Mock message exists and user is receiver
        mock_message = Message(
            id=message_id,
            sender_id=1,
            receiver_id=user_id,
            content="Hello",
            is_read=False
        )
        self.mock_message_repo.get_by_id.return_value = mock_message
        
        # Mock updated message
        updated_message = Message(
            id=message_id,
            sender_id=1,
            receiver_id=user_id,
            content="Hello",
            is_read=True
        )
        self.mock_message_repo.update.return_value = updated_message
        
        # Execute
        result = await self.chat_service.mark_message_as_read(message_id, user_id)
        
        # Assert
        assert result.is_read is True
        self.mock_message_repo.update.assert_called_once()
    
    async def test_mark_message_as_read_unauthorized(self):
        """Test marking message as read by non-receiver."""
        message_id = 1
        user_id = 3  # Neither sender nor receiver
        
        # Mock message
        mock_message = Message(id=message_id, sender_id=1, receiver_id=2, content="Hello", is_read=False)
        self.mock_message_repo.get_by_id.return_value = mock_message
        
        # Execute and assert
        with pytest.raises(ValueError, match="Not authorized to mark this message as read"):
            await self.chat_service.mark_message_as_read(message_id, user_id)
    
    async def test_get_unread_messages_success(self):
        """Test getting unread messages for a user."""
        user_id = 1
        
        # Mock unread messages
        mock_messages = [
            Message(id=1, sender_id=2, receiver_id=user_id, content="Hello", is_read=False),
            Message(id=2, sender_id=3, receiver_id=user_id, content="Hi", is_read=False)
        ]
        self.mock_message_repo.get_unread_by_receiver.return_value = mock_messages
        
        # Execute
        result = await self.chat_service.get_unread_messages(user_id)
        
        # Assert
        assert len(result) == 2
        assert all(msg.receiver_id == user_id and msg.is_read is False for msg in result)
        self.mock_message_repo.get_unread_by_receiver.assert_called_once_with(user_id)


class TestFriendshipService:
    """Test FriendshipService functionality."""
    
    def setup_method(self):
        """Setup test dependencies."""
        self.mock_friendship_repo = AsyncMock()
        self.mock_user_repo = AsyncMock()
        self.mock_event_manager = AsyncMock()
        self.friendship_service = FriendshipService(
            friendship_repository=self.mock_friendship_repo,
            user_repository=self.mock_user_repo,
            event_manager=self.mock_event_manager
        )
    
    async def test_send_friend_request_success(self):
        """Test sending friend request."""
        user_id = 1
        friend_id = 2
        
        # Mock users exist
        user = User(id=user_id, email="user@example.com", username="user", hashed_password="pass")
        friend = User(id=friend_id, email="friend@example.com", username="friend", hashed_password="pass")
        self.mock_user_repo.get_by_id.side_effect = [user, friend]
        
        # Mock no existing friendship
        self.mock_friendship_repo.get_between_users.return_value = None
        
        # Mock created friendship
        mock_friendship = Friendship(id=1, user_id=user_id, friend_id=friend_id, status="pending")
        self.mock_friendship_repo.create.return_value = mock_friendship
        
        # Execute
        result = await self.friendship_service.send_friend_request(user_id, friend_id)
        
        # Assert
        assert result.user_id == user_id
        assert result.friend_id == friend_id
        assert result.status == "pending"
        self.mock_friendship_repo.create.assert_called_once()
        
        # Verify event was sent
        self.mock_event_manager.notify.assert_called_once()
        event_call = self.mock_event_manager.notify.call_args[0][0]
        assert event_call.event_type == EventType.FRIEND_ADDED
    
    async def test_send_friend_request_to_self(self):
        """Test sending friend request to self."""
        user_id = 1
        
        # Execute and assert
        with pytest.raises(ValueError, match="Cannot send friend request to yourself"):
            await self.friendship_service.send_friend_request(user_id, user_id)
    
    async def test_send_friend_request_duplicate(self):
        """Test sending duplicate friend request."""
        user_id = 1
        friend_id = 2
        
        # Mock existing friendship
        existing_friendship = Friendship(id=1, user_id=user_id, friend_id=friend_id, status="pending")
        self.mock_friendship_repo.get_between_users.return_value = existing_friendship
        
        # Execute and assert
        with pytest.raises(ValueError, match="Friend request already exists"):
            await self.friendship_service.send_friend_request(user_id, friend_id)
    
    async def test_accept_friend_request_success(self):
        """Test accepting friend request."""
        friendship_id = 1
        user_id = 2  # Friend who received the request
        
        # Mock friendship exists and is pending
        mock_friendship = Friendship(id=friendship_id, user_id=1, friend_id=user_id, status="pending")
        self.mock_friendship_repo.get_by_id.return_value = mock_friendship
        
        # Mock updated friendship
        updated_friendship = Friendship(id=friendship_id, user_id=1, friend_id=user_id, status="accepted")
        self.mock_friendship_repo.update.return_value = updated_friendship
        
        # Execute
        result = await self.friendship_service.accept_friend_request(friendship_id, user_id)
        
        # Assert
        assert result.status == "accepted"
        self.mock_friendship_repo.update.assert_called_once()
    
    async def test_accept_friend_request_unauthorized(self):
        """Test accepting friend request by unauthorized user."""
        friendship_id = 1
        user_id = 3  # Neither user nor friend in the friendship
        
        # Mock friendship
        mock_friendship = Friendship(id=friendship_id, user_id=1, friend_id=2, status="pending")
        self.mock_friendship_repo.get_by_id.return_value = mock_friendship
        
        # Execute and assert
        with pytest.raises(ValueError, match="Not authorized to accept this friend request"):
            await self.friendship_service.accept_friend_request(friendship_id, user_id)
    
    async def test_reject_friend_request_success(self):
        """Test rejecting friend request."""
        friendship_id = 1
        user_id = 2  # Friend who received the request
        
        # Mock friendship exists and is pending
        mock_friendship = Friendship(id=friendship_id, user_id=1, friend_id=user_id, status="pending")
        self.mock_friendship_repo.get_by_id.return_value = mock_friendship
        
        # Mock updated friendship
        rejected_friendship = Friendship(id=friendship_id, user_id=1, friend_id=user_id, status="blocked")
        self.mock_friendship_repo.update.return_value = rejected_friendship
        
        # Execute
        result = await self.friendship_service.reject_friend_request(friendship_id, user_id)
        
        # Assert
        assert result.status == "blocked"
        self.mock_friendship_repo.update.assert_called_once()
    
    async def test_get_user_friends_success(self):
        """Test getting user's friends."""
        user_id = 1
        
        # Mock friendships (accepted)
        mock_friendships = [
            Friendship(id=1, user_id=user_id, friend_id=2, status="accepted"),
            Friendship(id=2, user_id=3, friend_id=user_id, status="accepted"),
            Friendship(id=3, user_id=user_id, friend_id=4, status="accepted")
        ]
        self.mock_friendship_repo.get_accepted_friendships.return_value = mock_friendships
        
        # Mock friend users
        friend_2 = User(id=2, email="friend2@example.com", username="friend2", hashed_password="pass")
        friend_3 = User(id=3, email="friend3@example.com", username="friend3", hashed_password="pass")
        friend_4 = User(id=4, email="friend4@example.com", username="friend4", hashed_password="pass")
        self.mock_user_repo.get_by_id.side_effect = [friend_2, friend_3, friend_4]
        
        # Execute
        result = await self.friendship_service.get_user_friends(user_id)
        
        # Assert
        assert len(result) == 3
        assert all(friend.id in [2, 3, 4] for friend in result)
        self.mock_friendship_repo.get_accepted_friendships.assert_called_once_with(user_id)
    
    async def test_get_friend_requests_success(self):
        """Test getting pending friend requests for a user."""
        user_id = 1
        
        # Mock pending friendships where user is the friend
        mock_requests = [
            Friendship(id=1, user_id=2, friend_id=user_id, status="pending"),
            Friendship(id=2, user_id=3, friend_id=user_id, status="pending")
        ]
        self.mock_friendship_repo.get_pending_requests.return_value = mock_requests
        
        # Mock requesting users
        user_2 = User(id=2, email="user2@example.com", username="user2", hashed_password="pass")
        user_3 = User(id=3, email="user3@example.com", username="user3", hashed_password="pass")
        self.mock_user_repo.get_by_id.side_effect = [user_2, user_3]
        
        # Execute
        result = await self.friendship_service.get_friend_requests(user_id)
        
        # Assert
        assert len(result) == 2
        assert all(request["friendship"].friend_id == user_id for request in result)
        assert all(request["user"].id in [2, 3] for request in result)
        self.mock_friendship_repo.get_pending_requests.assert_called_once_with(user_id)
    
    async def test_remove_friend_success(self):
        """Test removing a friend."""
        user_id = 1
        friend_id = 2
        
        # Mock existing friendship
        mock_friendship = Friendship(id=1, user_id=user_id, friend_id=friend_id, status="accepted")
        self.mock_friendship_repo.get_between_users.return_value = mock_friendship
        self.mock_friendship_repo.delete.return_value = True
        
        # Execute
        result = await self.friendship_service.remove_friend(user_id, friend_id)
        
        # Assert
        assert result is True
        self.mock_friendship_repo.delete.assert_called_once_with(mock_friendship.id)
    
    async def test_block_user_success(self):
        """Test blocking a user."""
        user_id = 1
        friend_id = 2
        
        # Mock users exist
        user = User(id=user_id, email="user@example.com", username="user", hashed_password="pass")
        friend = User(id=friend_id, email="friend@example.com", username="friend", hashed_password="pass")
        self.mock_user_repo.get_by_id.side_effect = [user, friend]
        
        # Mock no existing friendship
        self.mock_friendship_repo.get_between_users.return_value = None
        
        # Mock created blocked friendship
        mock_friendship = Friendship(id=1, user_id=user_id, friend_id=friend_id, status="blocked")
        self.mock_friendship_repo.create.return_value = mock_friendship
        
        # Execute
        result = await self.friendship_service.block_user(user_id, friend_id)
        
        # Assert
        assert result.status == "blocked"
        self.mock_friendship_repo.create.assert_called_once()
    
    async def test_unblock_user_success(self):
        """Test unblocking a user."""
        user_id = 1
        friend_id = 2
        
        # Mock existing blocked friendship
        mock_friendship = Friendship(id=1, user_id=user_id, friend_id=friend_id, status="blocked")
        self.mock_friendship_repo.get_between_users.return_value = mock_friendship
        self.mock_friendship_repo.delete.return_value = True
        
        # Execute
        result = await self.friendship_service.unblock_user(user_id, friend_id)
        
        # Assert
        assert result is True
        self.mock_friendship_repo.delete.assert_called_once_with(mock_friendship.id)
