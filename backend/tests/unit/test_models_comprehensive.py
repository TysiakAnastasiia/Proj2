
import pytest
from datetime import datetime
from unittest.mock import AsyncMock
from app.models import User, Book, Review, Exchange, WishlistItem, Message, Friendship


class TestUserModel:
    """Test User model."""
    
    def setup_method(self):
        """Setup test data."""
        self.valid_user_data = {
            "email": "test@example.com",
            "username": "testuser", 
            "hashed_password": "hashed_password",
            "full_name": "Test User",
            "bio": "Test bio",
            "city": "Test City",
            "avatar_url": "https://example.com/avatar.jpg",
            "is_active": True
        }
    
    def test_user_creation_with_valid_data(self):
        """Test creating a user with valid data."""
        user = User(**self.valid_user_data)
        
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.hashed_password == "hashed_password"
        assert user.full_name == "Test User"
        assert user.bio == "Test bio"
        assert user.city == "Test City"
        assert user.avatar_url == "https://example.com/avatar.jpg"
        assert user.is_active is True
        assert user.created_at is not None
    
    def test_user_email_validation(self):
        """Test email validation in User model."""
        with pytest.raises(ValueError):
            User(email="invalid-email", username="test", hashed_password="pass")
    
    def test_user_username_validation(self):
        """Test username validation."""
        # Valid usernames
        valid_usernames = ["user123", "test_user", "user.name"]
        for username in valid_usernames:
            user = User(email="test@example.com", username=username, hashed_password="pass")
            assert user.username == username
        
        # Invalid usernames (too short)
        with pytest.raises(ValueError):
            User(email="test@example.com", username="", hashed_password="pass")
        
        # Invalid usernames (too long)
        with pytest.raises(ValueError):
            User(email="test@example.com", username="a" * 51, hashed_password="pass")
    
    def test_user_password_hashing(self):
        """Test that passwords are properly hashed."""
        user = User(email="test@example.com", username="test", hashed_password="hashed_pass")
        assert user.hashed_password != "plain_password"
        assert user.hashed_password.startswith("$2b$")  # bcrypt hash
    
    def test_user_relationships_initialization(self):
        """Test that user relationships are properly initialized."""
        user = User(email="test@example.com", username="test", hashed_password="pass")
        
        # Relationships should be empty lists initially
        assert user.books == []
        assert user.reviews == []
        assert user.wishlist_items == []
        assert user.sent_exchanges == []
        assert user.received_exchanges == []
        assert user.sent_messages == []
        assert user.received_messages == []
        assert user.friendships == []
    
    def test_user_str_representation(self):
        """Test string representation of User."""
        user = User(email="test@example.com", username="test", hashed_password="pass")
        assert str(user) == "test@test@example.com"
    
    def test_user_repr_representation(self):
        """Test repr representation of User."""
        user = User(id=1, email="test@example.com", username="test", hashed_password="pass")
        assert repr(user) == f"<User id=1 email=test@example.com username=test>"
    
    def test_user_is_active_default(self):
        """Test that users are active by default."""
        user = User(email="test@example.com", username="test", hashed_password="pass")
        assert user.is_active is True
    
    def test_user_created_at_auto_set(self):
        """Test that created_at is automatically set."""
        before = datetime.utcnow()
        user = User(email="test@example.com", username="test", hashed_password="pass")
        after = datetime.utcnow()
        
        assert before <= user.created_at <= after


class TestBookModel:
    """Test Book model functionality."""
    
    def test_book_creation_with_valid_data(self):
        """Test creating a book with valid data."""
        book = Book(
            title="Test Book",
            author="Test Author",
            isbn="978-3-16-148410-0",
            description="Test description",
            genre="Fiction",
            year_published=2023,
            pages=250,
            language="English",
            cover_url="http://example.com/cover.jpg",
            owner_id=1,
            is_available=True
        )
        
        assert book.title == "Test Book"
        assert book.author == "Test Author"
        assert book.is_available is True
    
    def test_book_isbn_validation(self):
        """Test ISBN validation."""
        # Valid ISBNs
        valid_isbns = ["978-3-16-148410-0", "9783161484100", "0-306-40615-2"]
        for isbn in valid_isbns:
            book = Book(title="Test", author="Test", isbn=isbn, owner_id=1)
            assert book.isbn == isbn
        
        # Invalid ISBN format
        with pytest.raises(ValueError):
            Book(title="Test", author="Test", isbn="invalid-isbn", owner_id=1)
    
    def test_book_year_validation(self):
        """Test year published validation."""
        # Valid years
        valid_years = [1900, 2000, 2023, datetime.utcnow().year]
        for year in valid_years:
            book = Book(title="Test", author="Test", year_published=year, owner_id=1)
            assert book.year_published == year
        
        # Invalid years (future)
        with pytest.raises(ValueError):
            Book(title="Test", author="Test", year_published=3000, owner_id=1)
        
        # Invalid years (too old)
        with pytest.raises(ValueError):
            Book(title="Test", author="Test", year_published=1800, owner_id=1)
    
    def test_book_pages_validation(self):
        """Test pages validation."""
        # Valid page counts
        valid_pages = [1, 100, 1000, 5000]
        for pages in valid_pages:
            book = Book(title="Test", author="Test", pages=pages, owner_id=1)
            assert book.pages == pages
        
        # Invalid page counts (negative)
        with pytest.raises(ValueError):
            Book(title="Test", author="Test", pages=-1, owner_id=1)
        
        # Invalid page counts (zero)
        with pytest.raises(ValueError):
            Book(title="Test", author="Test", pages=0, owner_id=1)
    
    def test_book_availability_toggle(self):
        """Test toggling book availability."""
        book = Book(title="Test", author="Test", owner_id=1, is_available=True)
        
        book.is_available = False
        assert book.is_available is False
        
        book.is_available = True
        assert book.is_available is True
    
    def test_book_str_representation(self):
        """Test string representation of Book."""
        book = Book(title="Test Book", author="Test Author", owner_id=1)
        assert str(book) == "Test Book by Test Author"
    
    def test_book_repr_representation(self):
        """Test repr representation of Book."""
        book = Book(id=1, title="Test Book", author="Test Author", owner_id=1)
        assert repr(book) == f"<Book id=1 title='Test Book' author='Test Author'>"
    
    def test_book_relationships_initialization(self):
        """Test that book relationships are properly initialized."""
        book = Book(title="Test", author="Test", owner_id=1)
        
        assert book.reviews == []
        assert book.exchanges_as_offered == []
        assert book.exchanges_as_requested == []
        assert book.wishlist_items == []


class TestReviewModel:
    """Test Review model functionality."""
    
    def test_review_creation_with_valid_data(self):
        """Test creating a review with valid data."""
        review = Review(
            user_id=1,
            book_id=1,
            rating=4,
            title="Great Book",
            content="I really enjoyed this book.",
            is_spoiler=False
        )
        
        assert review.user_id == 1
        assert review.book_id == 1
        assert review.rating == 4
        assert review.is_spoiler is False
    
    def test_review_rating_validation(self):
        """Test rating validation (1-5 scale)."""
        # Valid ratings
        valid_ratings = [1, 2, 3, 4, 5]
        for rating in valid_ratings:
            review = Review(user_id=1, book_id=1, rating=rating)
            assert review.rating == rating
        
        # Invalid ratings (too low)
        with pytest.raises(ValueError):
            Review(user_id=1, book_id=1, rating=0)
        
        # Invalid ratings (too high)
        with pytest.raises(ValueError):
            Review(user_id=1, book_id=1, rating=6)
        
        # Invalid ratings (non-integer)
        with pytest.raises(ValueError):
            Review(user_id=1, book_id=1, rating=3.5)
    
    def test_review_content_validation(self):
        """Test review content validation."""
        # Valid content
        valid_content = "This is a great book with good character development."
        review = Review(user_id=1, book_id=1, rating=4, content=valid_content)
        assert review.content == valid_content
        
        # Empty content should be allowed (optional field)
        review = Review(user_id=1, book_id=1, rating=4, content="")
        assert review.content == ""
        
        # Content too long
        with pytest.raises(ValueError):
            Review(user_id=1, book_id=1, rating=4, content="a" * 2001)
    
    def test_review_title_validation(self):
        """Test review title validation."""
        # Valid title
        title = "Excellent Read"
        review = Review(user_id=1, book_id=1, rating=4, title=title)
        assert review.title == title
        
        # Empty title should be allowed (optional field)
        review = Review(user_id=1, book_id=1, rating=4, title="")
        assert review.title == ""
        
        # Title too long
        with pytest.raises(ValueError):
            Review(user_id=1, book_id=1, rating=4, title="a" * 101)
    
    def test_review_spoiler_flag(self):
        """Test spoiler flag functionality."""
        review = Review(user_id=1, book_id=1, rating=4, is_spoiler=False)
        assert review.is_spoiler is False
        
        review.is_spoiler = True
        assert review.is_spoiler is True
    
    def test_review_str_representation(self):
        """Test string representation of Review."""
        review = Review(user_id=1, book_id=1, rating=4, title="Great Book")
        assert str(review) == "Review by user 1: Great Book (4/5)"
    
    def test_review_repr_representation(self):
        """Test repr representation of Review."""
        review = Review(id=1, user_id=1, book_id=1, rating=4)
        assert repr(review) == f"<Review id=1 user_id=1 book_id=1 rating=4>"


class TestExchangeModel:
    """Test Exchange model functionality."""
    
    def test_exchange_creation_with_valid_data(self):
        """Test creating an exchange with valid data."""
        exchange = Exchange(
            requester_id=1,
            requested_user_id=2,
            offered_book_id=1,
            requested_book_id=2,
            status="pending",
            message="I'd like to exchange books with you!"
        )
        
        assert exchange.requester_id == 1
        assert exchange.requested_user_id == 2
        assert exchange.status == "pending"
    
    def test_exchange_status_validation(self):
        """Test exchange status validation."""
        valid_statuses = ["pending", "accepted", "rejected", "completed", "cancelled"]
        for status in valid_statuses:
            exchange = Exchange(
                requester_id=1,
                requested_user_id=2,
                offered_book_id=1,
                requested_book_id=2,
                status=status
            )
            assert exchange.status == status
        
        # Invalid status
        with pytest.raises(ValueError):
            Exchange(
                requester_id=1,
                requested_user_id=2,
                offered_book_id=1,
                requested_book_id=2,
                status="invalid_status"
            )
    
    def test_exchange_user_validation(self):
        """Test that requester and requested user are different."""
        # Same user should not be allowed
        with pytest.raises(ValueError):
            Exchange(
                requester_id=1,
                requested_user_id=1,
                offered_book_id=1,
                requested_book_id=2
            )
        
        # Different users should be allowed
        exchange = Exchange(
            requester_id=1,
            requested_user_id=2,
            offered_book_id=1,
            requested_book_id=2
        )
        assert exchange.requester_id == 1
        assert exchange.requested_user_id == 2
    
    def test_exchange_book_validation(self):
        """Test that offered and requested books are different."""
        # Same book should not be allowed
        with pytest.raises(ValueError):
            Exchange(
                requester_id=1,
                requested_user_id=2,
                offered_book_id=1,
                requested_book_id=1
            )
        
        # Different books should be allowed
        exchange = Exchange(
            requester_id=1,
            requested_user_id=2,
            offered_book_id=1,
            requested_book_id=2
        )
        assert exchange.offered_book_id == 1
        assert exchange.requested_book_id == 2
    
    def test_exchange_message_validation(self):
        """Test exchange message validation."""
        # Valid message
        message = "I'd like to exchange books!"
        exchange = Exchange(
            requester_id=1,
            requested_user_id=2,
            offered_book_id=1,
            requested_book_id=2,
            message=message
        )
        assert exchange.message == message
        
        # Empty message should be allowed
        exchange = Exchange(
            requester_id=1,
            requested_user_id=2,
            offered_book_id=1,
            requested_book_id=2,
            message=""
        )
        assert exchange.message == ""
        
        # Message too long
        with pytest.raises(ValueError):
            Exchange(
                requester_id=1,
                requested_user_id=2,
                offered_book_id=1,
                requested_book_id=2,
                message="a" * 501
            )
    
    def test_exchange_status_transitions(self):
        """Test valid status transitions."""
        exchange = Exchange(
            requester_id=1,
            requested_user_id=2,
            offered_book_id=1,
            requested_book_id=2,
            status="pending"
        )
        
        # Valid transitions from pending
        exchange.status = "accepted"
        assert exchange.status == "accepted"
        
        exchange.status = "rejected"
        assert exchange.status == "rejected"
        
        exchange.status = "cancelled"
        assert exchange.status == "cancelled"
    
    def test_exchange_str_representation(self):
        """Test string representation of Exchange."""
        exchange = Exchange(
            id=1,
            requester_id=1,
            requested_user_id=2,
            offered_book_id=1,
            requested_book_id=2,
            status="pending"
        )
        assert str(exchange) == f"Exchange {1}: User 1 -> User 2 (pending)"
    
    def test_exchange_repr_representation(self):
        """Test repr representation of Exchange."""
        exchange = Exchange(
            id=1,
            requester_id=1,
            requested_user_id=2,
            offered_book_id=1,
            requested_book_id=2,
            status="pending"
        )
        assert repr(ex) == f"<Exchange id=1 requester=1 requested=2 status=pending>"


class TestWishlistItemModel:
    """Test WishlistItem model functionality."""
    
    def test_wishlist_item_creation_with_valid_data(self):
        """Test creating a wishlist item with valid data."""
        wishlist_item = WishlistItem(
            user_id=1,
            book_id=1,
            priority="high",
            notes="Really want this book!"
        )
        
        assert wishlist_item.user_id == 1
        assert wishlist_item.book_id == 1
        assert wishlist_item.priority == "high"
    
    def test_wishlist_priority_validation(self):
        """Test wishlist priority validation."""
        valid_priorities = ["low", "medium", "high"]
        for priority in valid_priorities:
            item = WishlistItem(user_id=1, book_id=1, priority=priority)
            assert item.priority == priority
        
        # Invalid priority
        with pytest.raises(ValueError):
            WishlistItem(user_id=1, book_id=1, priority="urgent")
    
    def test_wishlist_notes_validation(self):
        """Test wishlist notes validation."""
        # Valid notes
        notes = "This book looks interesting"
        item = WishlistItem(user_id=1, book_id=1, notes=notes)
        assert item.notes == notes
        
        # Empty notes should be allowed
        item = WishlistItem(user_id=1, book_id=1, notes="")
        assert item.notes == ""
        
        # Notes too long
        with pytest.raises(ValueError):
            WishlistItem(user_id=1, book_id=1, notes="a" * 301)
    
    def test_wishlist_str_representation(self):
        """Test string representation of WishlistItem."""
        item = WishlistItem(id=1, user_id=1, book_id=1, priority="high")
        assert str(item) == f"WishlistItem {1}: User 1 wants Book 1 (high priority)"
    
    def test_wishlist_repr_representation(self):
        """Test repr representation of WishlistItem."""
        item = WishlistItem(id=1, user_id=1, book_id=1, priority="high")
        assert repr(item) == f"<WishlistItem id=1 user_id=1 book_id=1 priority=high>"


class TestMessageModel:
    """Test Message model functionality."""
    
    def test_message_creation_with_valid_data(self):
        """Test creating a message with valid data."""
        message = Message(
            sender_id=1,
            receiver_id=2,
            content="Hi, I'd like to discuss the book exchange!"
        )
        
        assert message.sender_id == 1
        assert message.receiver_id == 2
        assert message.content == "Hi, I'd like to discuss the book exchange!"
        assert message.is_read is False
    
    def test_message_sender_receiver_validation(self):
        """Test that sender and receiver are different."""
        # Same user should not be allowed
        with pytest.raises(ValueError):
            Message(sender_id=1, receiver_id=1, content="Test")
        
        # Different users should be allowed
        message = Message(sender_id=1, receiver_id=2, content="Test")
        assert message.sender_id == 1
        assert message.receiver_id == 2
    
    def test_message_content_validation(self):
        """Test message content validation."""
        # Valid content
        content = "Hello, how are you?"
        message = Message(sender_id=1, receiver_id=2, content=content)
        assert message.content == content
        
        # Empty content should not be allowed
        with pytest.raises(ValueError):
            Message(sender_id=1, receiver_id=2, content="")
        
        # Content too long
        with pytest.raises(ValueError):
            Message(sender_id=1, receiver_id=2, content="a" * 1001)
    
    def test_message_read_status(self):
        """Test message read status functionality."""
        message = Message(sender_id=1, receiver_id=2, content="Test")
        assert message.is_read is False
        
        message.is_read = True
        assert message.is_read is True
    
    def test_message_str_representation(self):
        """Test string representation of Message."""
        message = Message(id=1, sender_id=1, receiver_id=2, content="Hello")
        assert str(message) == f"Message {1}: User 1 -> User 2 (unread)"
    
    def test_message_repr_representation(self):
        """Test repr representation of Message."""
        message = Message(id=1, sender_id=1, receiver_id=2, content="Hello")
        assert repr(message) == f"<Message id=1 sender=1 receiver=2 read=False>"


class TestFriendshipModel:
    """Test Friendship model functionality."""
    
    def test_friendship_creation_with_valid_data(self):
        """Test creating a friendship with valid data."""
        friendship = Friendship(
            user_id=1,
            friend_id=2,
            status="pending"
        )
        
        assert friendship.user_id == 1
        assert friendship.friend_id == 2
        assert friendship.status == "pending"
    
    def test_friendship_status_validation(self):
        """Test friendship status validation."""
        valid_statuses = ["pending", "accepted", "blocked"]
        for status in valid_statuses:
            friendship = Friendship(user_id=1, friend_id=2, status=status)
            assert friendship.status == status
        
        # Invalid status
        with pytest.raises(ValueError):
            Friendship(user_id=1, friend_id=2, status="invalid")
    
    def test_friendship_user_validation(self):
        """Test that users in friendship are different."""
        # Same user should not be allowed
        with pytest.raises(ValueError):
            Friendship(user_id=1, friend_id=1)
        
        # Different users should be allowed
        friendship = Friendship(user_id=1, friend_id=2)
        assert friendship.user_id == 1
        assert friendship.friend_id == 2
    
    def test_friendship_str_representation(self):
        """Test string representation of Friendship."""
        friendship = Friendship(id=1, user_id=1, friend_id=2, status="accepted")
        assert str(friendship) == f"Friendship {1}: User 1 <-> User 2 (accepted)"
    
    def test_friendship_repr_representation(self):
        """Test repr representation of Friendship."""
        friendship = Friendship(id=1, user_id=1, friend_id=2, status="pending")
        assert repr(friendship) == f"<Friendship id=1 user_id=1 friend_id=2 status=pending>"


class TestModelRelationships:
    """Test relationships between models."""
    
    def test_user_book_relationship(self):
        """Test User-Book relationship."""
        user = User(id=1, email="test@example.com", username="test", hashed_password="pass")
        book = Book(id=1, title="Test Book", author="Test Author", owner_id=1)
        
        # User owns the book
        assert book.owner_id == user.id
        
        # Book is in user's books
        user.books.append(book)
        assert book in user.books
        assert book.owner_id == user.id
    
    def test_user_review_relationship(self):
        """Test User-Review relationship."""
        user = User(id=1, email="test@example.com", username="test", hashed_password="pass")
        book = Book(id=1, title="Test Book", author="Test Author", owner_id=2)
        review = Review(id=1, user_id=1, book_id=1, rating=4)
        
        # Review belongs to user
        assert review.user_id == user.id
        
        # Review is in user's reviews
        user.reviews.append(review)
        assert review in user.reviews
        
        # Review belongs to book
        assert review.book_id == book.id
        
        # Review is in book's reviews
        book.reviews.append(review)
        assert review in book.reviews
    
    def test_exchange_relationships(self):
        """Test Exchange model relationships."""
        requester = User(id=1, email="requester@example.com", username="requester", hashed_password="pass")
        requested_user = User(id=2, email="requested@example.com", username="requested", hashed_password="pass")
        offered_book = Book(id=1, title="Offered Book", author="Author", owner_id=1)
        requested_book = Book(id=2, title="Requested Book", author="Author", owner_id=2)
        
        exchange = Exchange(
            id=1,
            requester_id=1,
            requested_user_id=2,
            offered_book_id=1,
            requested_book_id=2,
            status="pending"
        )
        
        # Exchange relationships
        assert exchange.requester_id == requester.id
        assert exchange.requested_user_id == requested_user.id
        assert exchange.offered_book_id == offered_book.id
        assert exchange.requested_book_id == requested_book.id
        
        # Add to user relationships
        requester.sent_exchanges.append(exchange)
        requested_user.received_exchanges.append(exchange)
        offered_book.exchanges_as_offered.append(exchange)
        requested_book.exchanges_as_requested.append(exchange)
        
        assert exchange in requester.sent_exchanges
        assert exchange in requested_user.received_exchanges
        assert exchange in offered_book.exchanges_as_offered
        assert exchange in requested_book.exchanges_as_requested


class TestModelValidation:
    """Test model validation and constraints."""
    
    def test_model_id_constraints(self):
        """Test ID field constraints."""
        # Positive IDs should be valid
        valid_ids = [1, 100, 999999]
        for model_id in valid_ids:
            user = User(id=model_id, email="test@example.com", username="test", hashed_password="pass")
            assert user.id == model_id
        
        # Zero or negative IDs should be invalid
        invalid_ids = [0, -1, -100]
        for model_id in invalid_ids:
            with pytest.raises(ValueError):
                User(id=model_id, email="test@example.com", username="test", hashed_password="pass")
    
    def test_model_required_fields(self):
        """Test required field validation."""
        # User required fields
        with pytest.raises(ValueError):
            User()  # Missing all required fields
        
        with pytest.raises(ValueError):
            User(email="test@example.com")  # Missing username and password
        
        # Book required fields
        with pytest.raises(ValueError):
            Book()  # Missing all required fields
        
        with pytest.raises(ValueError):
            Book(title="Test")  # Missing author and owner_id
    
    def test_model_field_types(self):
        """Test field type validation."""
        # Email should be string
        with pytest.raises(TypeError):
            User(email=123, username="test", hashed_password="pass")
        
        # Rating should be integer
        with pytest.raises(TypeError):
            Review(user_id=1, book_id=1, rating="4")  # String instead of int
        
        # Is_active should be boolean
        with pytest.raises(TypeError):
            User(email="test@example.com", username="test", hashed_password="pass", is_active="true")


class TestModelBusinessLogic:
    """Test business logic in models."""
    
    def test_user_deactivation_logic(self):
        """Test user deactivation business logic."""
        user = User(email="test@example.com", username="test", hashed_password="pass", is_active=True)
        
        # Deactivate user
        user.is_active = False
        assert user.is_active is False
        
        # Reactivate user
        user.is_active = True
        assert user.is_active is True
    
    def test_book_availability_logic(self):
        """Test book availability business logic."""
        book = Book(title="Test", author="Test", owner_id=1, is_available=True)
        
        # Mark as unavailable (in exchange)
        book.is_available = False
        assert book.is_available is False
        
        # Mark as available again
        book.is_available = True
        assert book.is_available is True
    
    def test_exchange_completion_logic(self):
        """Test exchange completion business logic."""
        exchange = Exchange(
            requester_id=1,
            requested_user_id=2,
            offered_book_id=1,
            requested_book_id=2,
            status="pending"
        )
        
        # Accept exchange
        exchange.status = "accepted"
        assert exchange.status == "accepted"
        
        # Complete exchange
        exchange.status = "completed"
        assert exchange.status == "completed"
    
    def test_review_helpfulness_logic(self):
        """Test review helpfulness logic (if implemented)."""
        review = Review(user_id=1, book_id=1, rating=4)
        
        # Test helpful votes (if implemented)
        if hasattr(review, 'helpful_votes'):
            review.helpful_votes = 5
            assert review.helpful_votes == 5
    
    def test_wishlist_priority_logic(self):
        """Test wishlist priority business logic."""
        # High priority item
        high_priority = WishlistItem(user_id=1, book_id=1, priority="high")
        assert high_priority.priority == "high"
        
        # Medium priority item
        medium_priority = WishlistItem(user_id=1, book_id=2, priority="medium")
        assert medium_priority.priority == "medium"
        
        # Low priority item
        low_priority = WishlistItem(user_id=1, book_id=3, priority="low")
        assert low_priority.priority == "low"


class TestModelEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_maximum_field_lengths(self):
        """Test maximum field length constraints."""
        # Maximum username length
        max_username = "a" * 50
        user = User(email="test@example.com", username=max_username, hashed_password="pass")
        assert user.username == max_username
        
        # Maximum book title length
        max_title = "a" * 200
        book = Book(title=max_title, author="Test", owner_id=1)
        assert book.title == max_title
    
    def test_unicode_content(self):
        """Test Unicode content handling."""
        # Unicode in user data
        user = User(
            email="тест@example.com",
            username="пользователь",
            hashed_password="пароль",
            full_name="Тестовий Користувач"
        )
        assert user.username == "пользователь"
        assert user.full_name == "Тестовий Користувач"
        
        # Unicode in book data
        book = Book(
            title="Тестова Книга",
            author="Тестовий Автор",
            description="Це тестовий опис книги",
            owner_id=1
        )
        assert book.title == "Тестова Книга"
        assert book.description == "Це тестовий опис книги"
    
    def test_special_characters(self):
        """Test special characters handling."""
        # Special characters in content
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        review = Review(
            user_id=1,
            book_id=1,
            rating=4,
            content=f"Review with special chars: {special_chars}"
        )
        assert special_chars in review.content
    
    def test_null_values_handling(self):
        """Test null/None values handling."""
        # Optional fields should accept None
        user = User(
            email="test@example.com",
            username="test",
            hashed_password="pass",
            bio=None,  # Optional field
            avatar_url=None  # Optional field
        )
        assert user.bio is None
        assert user.avatar_url is None
        
        # Required fields should not accept None
        with pytest.raises(ValueError):
            User(email=None, username="test", hashed_password="pass")
    
    def test_concurrent_access_simulation(self):
        """Test simulation of concurrent access scenarios."""
        user = User(id=1, email="test@example.com", username="test", hashed_password="pass")
        
        # Simulate multiple operations
        operations = []
        for i in range(10):
            operations.append(f"operation_{i}")
        
        # Test that model can handle multiple operations
        for op in operations:
            user.username = f"test_{op}"
            assert user.username.startswith("test_")
        
        # Reset to original
        user.username = "test"
        assert user.username == "test"
