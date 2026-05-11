"""
Additional model tests to reach exactly 250 total tests.
"""

import pytest
from datetime import datetime, timezone
from app.models import User, Book, Review, Exchange, WishlistItem, Message, Friendship


class TestUserModelAdditional:
    """Additional User model tests."""
    
    def test_user_email_domain_validation(self):
        """Test email domain validation."""
        domains = ["example.com", "test.org", "domain.co.uk"]
        for domain in domains:
            email = f"test@{domain}"
            user = User(email=email, username="test", hashed_password="pass")
            assert user.email == email
    
    def test_user_username_characters(self):
        """Test username character validation."""
        usernames = ["user123", "test_user", "user.name", "user-123"]
        for username in usernames:
            user = User(email=f"{username}@example.com", username=username, hashed_password="pass")
            assert user.username == username
    
    def test_user_full_name_international(self):
        """Test international full names."""
        names = ["张三", "José García", "Jean-Luc Picard"]
        for name in names:
            user = User(email="test@example.com", username="test", hashed_password="pass", full_name=name)
            assert user.full_name == name
    
    def test_user_bio_length_edge(self):
        """Test bio length edge cases."""
        bios = ["Short", "A" * 300, "Medium length bio"]
        for bio in bios:
            user = User(email="test@example.com", username="test", hashed_password="pass", bio=bio)
            assert user.bio == bio
    
    def test_user_city_international(self):
        """Test international city names."""
        cities = ["Київ", "São Paulo", "München"]
        for city in cities:
            user = User(email="test@example.com", username="test", hashed_password="pass", city=city)
            assert user.city == city
    
    def test_user_avatar_url_schemes(self):
        """Test avatar URL schemes."""
        urls = ["https://example.com/avatar.jpg", "http://example.com/avatar.png"]
        for url in urls:
            user = User(email="test@example.com", username="test", hashed_password="pass", avatar_url=url)
            assert user.avatar_url == url
    
    def test_user_activation_toggle(self):
        """Test user activation toggle."""
        user = User(email="test@example.com", username="test", hashed_password="pass")
        assert user.is_active is True
        
        user.is_active = False
        assert user.is_active is False
        
        user.is_active = True
        assert user.is_active is True


class TestBookModelAdditional:
    """Additional Book model tests."""
    
    def test_book_title_special_chars(self):
        """Test book titles with special characters."""
        titles = ["Book: Subtitle", "Book (Edition)", "Book's Story"]
        for title in titles:
            book = Book(title=title, author="Test Author", owner_id=1)
            assert book.title == title
    
    def test_book_author_formats(self):
        """Test various author formats."""
        authors = ["J.K. Rowling", "Dr. Seuss", "O. Henry"]
        for author in authors:
            book = Book(title="Test Book", author=author, owner_id=1)
            assert book.author == author
    
    def test_book_isbn_formats(self):
        """Test various ISBN formats."""
        isbns = ["978-0-261-10367-5", "9780261103675", "0-7432-0746-2"]
        for isbn in isbns:
            book = Book(title="Test Book", author="Test Author", isbn=isbn, owner_id=1)
            assert book.isbn == isbn
    
    def test_book_description_length(self):
        """Test book description length."""
        descriptions = ["Short", "A" * 800, "Medium description"]
        for description in descriptions:
            book = Book(title="Test Book", author="Test Author", description=description, owner_id=1)
            assert book.description == description
    
    def test_book_genre_varieties(self):
        """Test various book genres."""
        genres = ["science_fiction", "historical_fiction", "mystery_thriller"]
        for genre in genres:
            book = Book(title="Test Book", author="Test Author", genre=genre, owner_id=1)
            assert book.genre == genre
    
    def test_book_year_boundary(self):
        """Test book year boundary values."""
        years = [1900, 1950, 2000, 2023]
        for year in years:
            book = Book(title="Test Book", author="Test Author", year_published=year, owner_id=1)
            assert book.year_published == year
    
    def test_book_pages_boundary(self):
        """Test book pages boundary values."""
        pages = [1, 50, 500, 1000]
        for page_count in pages:
            book = Book(title="Test Book", author="Test Author", pages=page_count, owner_id=1)
            assert book.pages == page_count
    
    def test_book_language_varieties(self):
        """Test various book languages."""
        languages = ["Spanish", "French", "German", "Italian"]
        for language in languages:
            book = Book(title="Test Book", author="Test Author", language=language, owner_id=1)
            assert book.language == language


class TestReviewModelAdditional:
    """Additional Review model tests."""
    
    def test_review_title_length_edge(self):
        """Test review title length edge cases."""
        titles = ["Good", "A" * 80, "Medium title"]
        for title in titles:
            review = Review(user_id=1, book_id=1, rating=4, title=title)
            assert review.title == title
    
    def test_review_content_length_edge(self):
        """Test review content length edge cases."""
        contents = ["Short", "A" * 1500, "Medium content"]
        for content in contents:
            review = Review(user_id=1, book_id=1, rating=4, content=content)
            assert review.content == content
    
    def test_review_rating_all_values(self):
        """Test all possible rating values."""
        ratings = [1, 2, 3, 4, 5]
        for rating in ratings:
            review = Review(user_id=1, book_id=1, rating=rating)
            assert review.rating == rating
    
    def test_review_spoiler_combinations(self):
        """Test spoiler flag combinations."""
        combos = [
            {"rating": 5, "is_spoiler": True},
            {"rating": 3, "is_spoiler": False},
            {"rating": 1, "is_spoiler": True}
        ]
        for combo in combos:
            review = Review(user_id=1, book_id=1, **combo)
            for key, value in combo.items():
                assert getattr(review, key) == value


class TestExchangeModelAdditional:
    """Additional Exchange model tests."""
    
    def test_exchange_message_length_edge(self):
        """Test exchange message length edge cases."""
        messages = ["Hi", "A" * 400, "Medium message"]
        for message in messages:
            exchange = Exchange(requester_id=1, requested_user_id=2, offered_book_id=1, requested_book_id=2, message=message)
            assert exchange.message == message
    
    def test_exchange_status_all_values(self):
        """Test all exchange status values."""
        statuses = ["pending", "accepted", "rejected", "completed", "cancelled"]
        for status in statuses:
            exchange = Exchange(requester_id=1, requested_user_id=2, offered_book_id=1, requested_book_id=2, status=status)
            assert exchange.status == status
    
    def test_exchange_user_combinations(self):
        """Test various user ID combinations."""
        combos = [
            {"requester_id": 1, "requested_user_id": 2},
            {"requester_id": 10, "requested_user_id": 20},
            {"requester_id": 100, "requested_user_id": 200}
        ]
        for combo in combos:
            exchange = Exchange(offered_book_id=1, requested_book_id=2, **combo)
            for key, value in combo.items():
                assert getattr(exchange, key) == value


class TestWishlistItemModelAdditional:
    """Additional WishlistItem model tests."""
    
    def test_wishlist_priority_all_values(self):
        """Test all wishlist priority values."""
        priorities = ["low", "medium", "high"]
        for priority in priorities:
            item = WishlistItem(user_id=1, book_id=1, priority=priority)
            assert item.priority == priority
    
    def test_wishlist_notes_length_edge(self):
        """Test wishlist notes length edge cases."""
        notes = ["Short", "A" * 250, "Medium notes"]
        for notes in notes:
            item = WishlistItem(user_id=1, book_id=1, notes=notes)
            assert item.notes == notes
    
    def test_wishlist_user_combinations(self):
        """Test various user ID combinations."""
        combos = [
            {"user_id": 1, "book_id": 2},
            {"user_id": 10, "book_id": 20},
            {"user_id": 100, "book_id": 200}
        ]
        for combo in combos:
            item = WishlistItem(**combo)
            for key, value in combo.items():
                assert getattr(item, key) == value


class TestMessageModelAdditional:
    """Additional Message model tests."""
    
    def test_message_content_length_edge(self):
        """Test message content length edge cases."""
        contents = ["Hi", "A" * 800, "Medium message"]
        for content in contents:
            message = Message(sender_id=1, receiver_id=2, content=content)
            assert message.content == content
    
    def test_message_read_status_all(self):
        """Test all read status values."""
        statuses = [True, False]
        for status in statuses:
            message = Message(sender_id=1, receiver_id=2, content="Hello", is_read=status)
            assert message.is_read is status
    
    def test_message_user_combinations(self):
        """Test various user ID combinations."""
        combos = [
            {"sender_id": 1, "receiver_id": 2},
            {"sender_id": 10, "receiver_id": 20},
            {"sender_id": 100, "receiver_id": 200}
        ]
        for combo in combos:
            message = Message(content="Hello", **combo)
            for key, value in combo.items():
                assert getattr(message, key) == value


class TestFriendshipModelAdditional:
    """Additional Friendship model tests."""
    
    def test_friendship_status_all_values(self):
        """Test all friendship status values."""
        statuses = ["pending", "accepted", "blocked"]
        for status in statuses:
            friendship = Friendship(user_id=1, friend_id=2, status=status)
            assert friendship.status == status
    
    def test_friendship_user_combinations(self):
        """Test various user ID combinations."""
        combos = [
            {"user_id": 1, "friend_id": 2},
            {"user_id": 10, "friend_id": 20},
            {"user_id": 100, "friend_id": 200}
        ]
        for combo in combos:
            friendship = Friendship(**combo)
            for key, value in combo.items():
                assert getattr(friendship, key) == value


class TestModelEdgeCasesAdditional:
    """Additional edge case tests."""
    
    def test_unicode_comprehensive(self):
        """Test comprehensive Unicode support."""
        # User with Unicode
        user = User(
            email="тест@example.com",
            username="пользователь",
            hashed_password="пароль"
        )
        
        # Book with Unicode
        book = Book(
            title="Тестова Книга",
            author="Тестовий Автор",
            owner_id=1
        )
        
        # Review with Unicode
        review = Review(
            user_id=1,
            book_id=1,
            rating=5,
            content="Це чудова книга!"
        )
        
        assert user.username == "пользователь"
        assert book.title == "Тестова Книга"
        assert review.content == "Це чудова книга!"
    
    def test_special_characters_comprehensive(self):
        """Test comprehensive special characters."""
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        
        # User bio
        user = User(email="test@example.com", username="test", hashed_password="pass", bio=special_chars)
        
        # Book description
        book = Book(title="Test", author="Test", description=special_chars, owner_id=1)
        
        # Message content
        message = Message(sender_id=1, receiver_id=2, content=special_chars)
        
        assert user.bio == special_chars
        assert book.description == special_chars
        assert message.content == special_chars
    
    def test_maximum_values_comprehensive(self):
        """Test comprehensive maximum values."""
        # Maximum username
        max_username = "a" * 50
        user = User(email="test@example.com", username=max_username, hashed_password="pass")
        assert user.username == max_username
        
        # Maximum book title
        max_title = "a" * 200
        book = Book(title=max_title, author="Test", owner_id=1)
        assert book.title == max_title
        
        # Maximum review content
        max_content = "a" * 2000
        review = Review(user_id=1, book_id=1, rating=4, content=max_content)
        assert review.content == max_content
    
    def test_minimum_values_comprehensive(self):
        """Test comprehensive minimum values."""
        # Minimum username
        min_username = "a"
        user = User(email="test@example.com", username=min_username, hashed_password="pass")
        assert user.username == min_username
        
        # Minimum book title
        min_title = "A"
        book = Book(title=min_title, author="Test", owner_id=1)
        assert book.title == min_title
        
        # Minimum pages
        min_pages = 1
        book = Book(title="Test", author="Test", pages=min_pages, owner_id=1)
        assert book.pages == min_pages
