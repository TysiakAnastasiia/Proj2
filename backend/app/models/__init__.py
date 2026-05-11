import enum
import re
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


# Constants for relationship cascades
CASCADE_DELETE_ORPHAN = "all, delete-orphan"

# Constants for foreign key references
USERS_ID_FK = "users.id"
BOOKS_ID_FK = "books.id"


#  User


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(200))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(String(100))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __init__(self, **kwargs):
        self._validate_id(kwargs.get('id'))
        self._validate_username(kwargs.get('username'))
        self._validate_required_fields(kwargs)
        self._validate_field_types(kwargs)
        self._set_defaults(kwargs)
        self._set_created_at(kwargs)
        super().__init__(**kwargs)

    def _validate_id(self, user_id):
        """Validate user ID."""
        if user_id is not None and (not isinstance(user_id, int) or user_id <= 0):
            raise ValueError("ID must be a positive integer")
    
    def _validate_username(self, username):
        """Validate username."""
        if username is not None:
            if not username or len(username.strip()) == 0:
                raise ValueError("Username cannot be empty")
            if len(username) > 50:
                raise ValueError("Username cannot be longer than 50 characters")
    
    def _validate_required_fields(self, kwargs):
        """Validate required fields."""
        if not kwargs.get('email'):
            raise ValueError("Email is required")
        if not kwargs.get('username'):
            raise ValueError("Username is required")
        if not kwargs.get('hashed_password'):
            raise ValueError("Hashed password is required")
    
    def _validate_field_types(self, kwargs):
        """Validate field types."""
        if kwargs.get('email') is not None and not isinstance(kwargs.get('email'), str):
            raise TypeError("Email must be a string")
        if kwargs.get('username') is not None and not isinstance(kwargs.get('username'), str):
            raise TypeError("Username must be a string")
        if kwargs.get('is_active') is not None and not isinstance(kwargs.get('is_active'), bool):
            raise TypeError("Is_active must be a boolean")
    
    def _set_defaults(self, kwargs):
        """Set default values."""
        if 'is_active' not in kwargs:
            kwargs['is_active'] = True
    
    def _set_created_at(self, kwargs):
        """Set created_at for testing purposes."""
        if 'created_at' not in kwargs:
            from datetime import datetime, timezone
            kwargs['created_at'] = datetime.now(timezone.utc)

    def __str__(self):
        return f"{self.username}@{self.email}"
    
    def __repr__(self):
        return f"<User id={self.id} email={self.email} username={self.username}>"

    books: Mapped[list["Book"]] = relationship(
        "Book", back_populates="owner", cascade=CASCADE_DELETE_ORPHAN
    )
    reviews: Mapped[list["Review"]] = relationship(
        "Review", back_populates="user", cascade=CASCADE_DELETE_ORPHAN
    )
    wishlist_items: Mapped[list["WishlistItem"]] = relationship(
        "WishlistItem", back_populates="user", cascade=CASCADE_DELETE_ORPHAN
    )
    sent_exchanges: Mapped[list["Exchange"]] = relationship(
        "Exchange", foreign_keys="Exchange.requester_id", back_populates="requester"
    )
    received_exchanges: Mapped[list["Exchange"]] = relationship(
        "Exchange", foreign_keys="Exchange.requested_user_id", back_populates="owner"
    )
    sent_messages: Mapped[list["Message"]] = relationship(
        "Message", foreign_keys="Message.sender_id", back_populates="sender"
    )
    received_messages: Mapped[list["Message"]] = relationship(
        "Message", foreign_keys="Message.receiver_id", back_populates="receiver"
    )
    friendships: Mapped[list["Friendship"]] = relationship(
        "Friendship", foreign_keys="Friendship.user_id", back_populates="requester"
    )


#  Book


class BookGenre(str, enum.Enum):
    fiction = "fiction"
    non_fiction = "non_fiction"
    fantasy = "fantasy"
    sci_fi = "sci_fi"
    mystery = "mystery"
    romance = "romance"
    thriller = "thriller"
    horror = "horror"
    biography = "biography"
    history = "history"
    science = "science"
    self_help = "self_help"
    children = "children"
    poetry = "poetry"
    other = "other"


class BookCondition(str, enum.Enum):
    new = "new"
    good = "good"
    fair = "fair"
    poor = "poor"


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    isbn: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    cover_url: Mapped[Optional[str]] = mapped_column(String(500))
    genre: Mapped[BookGenre] = mapped_column(Enum(BookGenre), nullable=False)
    year_published: Mapped[Optional[int]] = mapped_column(Integer)
    pages: Mapped[Optional[int]] = mapped_column(Integer)
    language: Mapped[str] = mapped_column(String(50), default="Ukrainian")
    condition: Mapped[BookCondition] = mapped_column(
        Enum(BookCondition), default=BookCondition.good
    )
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey(USERS_ID_FK), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Constants for ISBN validation
    ISBN_10_PATTERN = r'^\d{9}[\dX]$'  # 10 digits, last can be X
    ISBN_13_PATTERN = r'^\d{13}$'       # 13 digits

    def _validate_isbn_format(self, isbn: str) -> bool:
        """Validate ISBN format using simplified patterns."""
        # Remove hyphens and spaces
        clean_isbn = isbn.replace('-', '').replace(' ', '')
        
        # Check if it matches ISBN-10 or ISBN-13 pattern
        return (bool(re.match(self.ISBN_10_PATTERN, clean_isbn)) or 
                bool(re.match(self.ISBN_13_PATTERN, clean_isbn)))

    def __init__(self, **kwargs):
        # Validate ISBN
        isbn = kwargs.get('isbn')
        if isbn is not None and not self._validate_isbn_format(isbn):
            raise ValueError("Invalid ISBN format")
        
        # Validate year published
        year = kwargs.get('year_published')
        if year is not None:
            current_year = datetime.now().year
            if year < 1900 or year > current_year:
                raise ValueError(f"Year published must be between 1900 and {current_year}")
        
        # Validate pages
        pages = kwargs.get('pages')
        if pages is not None and pages <= 0:
            raise ValueError("Pages must be a positive integer")
        
        super().__init__(**kwargs)

    def __str__(self):
        return f"{self.title} by {self.author}"
    
    def __repr__(self):
        return f"<Book id={self.id} title='{self.title}' author='{self.author}'>"

    owner: Mapped["User"] = relationship("User", back_populates="books")
    reviews: Mapped[list["Review"]] = relationship(
        "Review", back_populates="book", cascade=CASCADE_DELETE_ORPHAN
    )
    wishlist_items: Mapped[list["WishlistItem"]] = relationship(
        "WishlistItem", back_populates="book"
    )
    exchange_offers: Mapped[list["Exchange"]] = relationship(
        "Exchange",
        foreign_keys="Exchange.offered_book_id",
        back_populates="offered_book",
    )
    exchange_requests: Mapped[list["Exchange"]] = relationship(
        "Exchange",
        foreign_keys="Exchange.requested_book_id",
        back_populates="requested_book",
    )


#  Review


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(200))
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    content: Mapped[Optional[str]] = mapped_column(Text)
    is_spoiler: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[int] = mapped_column(ForeignKey(USERS_ID_FK), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey(BOOKS_ID_FK), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, onupdate=func.now()
    )

    def __init__(self, **kwargs):
        # Validate rating
        rating = kwargs.get('rating')
        if rating is not None:
            if not isinstance(rating, int):
                raise ValueError("Rating must be an integer")
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
        
        # Validate title length
        title = kwargs.get('title')
        if title is not None and len(title) > 100:
            raise ValueError("Title cannot be longer than 100 characters")
        
        # Validate content length
        content = kwargs.get('content')
        if content is not None and len(content) > 2000:
            raise ValueError("Content cannot be longer than 2000 characters")
        
        super().__init__(**kwargs)

    def __str__(self):
        title_part = f": {self.title}" if self.title else ""
        return f"Review by user {self.user_id}{title_part} ({self.rating}/5)"
    
    def __repr__(self):
        return f"<Review id={self.id} user_id={self.user_id} book_id={self.book_id} rating={self.rating}>"

    user: Mapped["User"] = relationship("User", back_populates="reviews")
    book: Mapped["Book"] = relationship("Book", back_populates="reviews")


#  Exchange


class ExchangeStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    completed = "completed"
    rejected = "rejected"
    cancelled = "cancelled"


class Exchange(Base):
    __tablename__ = "exchanges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    requester_id: Mapped[int] = mapped_column(ForeignKey(USERS_ID_FK), nullable=False)
    requested_user_id: Mapped[int] = mapped_column(ForeignKey(USERS_ID_FK), nullable=False)
    offered_book_id: Mapped[int] = mapped_column(ForeignKey(BOOKS_ID_FK), nullable=False)
    requested_book_id: Mapped[int] = mapped_column(
        ForeignKey(BOOKS_ID_FK), nullable=False
    )
    status: Mapped[ExchangeStatus] = mapped_column(
        Enum(ExchangeStatus), default=ExchangeStatus.pending
    )
    message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, onupdate=func.now()
    )

    def __init__(self, **kwargs):
        # Validate status
        status = kwargs.get('status')
        if status is not None:
            valid_statuses = ["pending", "accepted", "rejected", "completed", "cancelled"]
            if status not in valid_statuses:
                raise ValueError(f"Status must be one of {valid_statuses}")
        
        # Validate users are different
        requester_id = kwargs.get('requester_id')
        requested_user_id = kwargs.get('requested_user_id')
        if requester_id is not None and requested_user_id is not None:
            if requester_id == requested_user_id:
                raise ValueError("Requester and requested user must be different")
        
        # Validate books are different
        offered_book_id = kwargs.get('offered_book_id')
        requested_book_id = kwargs.get('requested_book_id')
        if offered_book_id is not None and requested_book_id is not None:
            if offered_book_id == requested_book_id:
                raise ValueError("Offered and requested books must be different")
        
        # Validate message length
        message = kwargs.get('message')
        if message is not None and len(message) > 500:
            raise ValueError("Message cannot be longer than 500 characters")
        
        super().__init__(**kwargs)

    def __str__(self):
        return f"Exchange {self.id}: User {self.requester_id} -> User {self.requested_user_id} ({self.status})"
    
    def __repr__(self):
        return f"<Exchange id={self.id} requester={self.requester_id} requested={self.requested_user_id} status={self.status}>"

    requester: Mapped["User"] = relationship(
        "User", foreign_keys=[requester_id], back_populates="sent_exchanges"
    )
    owner: Mapped["User"] = relationship(
        "User", foreign_keys=[requested_user_id], back_populates="received_exchanges"
    )
    offered_book: Mapped["Book"] = relationship(
        "Book", foreign_keys=[offered_book_id], back_populates="exchange_offers"
    )
    requested_book: Mapped["Book"] = relationship(
        "Book", foreign_keys=[requested_book_id], back_populates="exchange_requests"
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="exchange"
    )


#  Wishlist


class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(USERS_ID_FK), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey(BOOKS_ID_FK), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    notes: Mapped[Optional[str]] = mapped_column(Text)
    added_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __init__(self, **kwargs):
        # Validate priority
        priority = kwargs.get('priority')
        if priority is not None:
            valid_priorities = ["low", "medium", "high"]
            if priority not in valid_priorities:
                raise ValueError(f"Priority must be one of {valid_priorities}")
        
        # Validate notes length
        notes = kwargs.get('notes')
        if notes is not None and len(notes) > 300:
            raise ValueError("Notes cannot be longer than 300 characters")
        
        super().__init__(**kwargs)

    def __str__(self):
        return f"WishlistItem {self.id}: User {self.user_id} wants Book {self.book_id} ({self.priority} priority)"
    
    def __repr__(self):
        return f"<WishlistItem id={self.id} user_id={self.user_id} book_id={self.book_id} priority={self.priority}>"

    user: Mapped["User"] = relationship("User", back_populates="wishlist_items")
    book: Mapped["Book"] = relationship("Book", back_populates="wishlist_items")


#  Message


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    exchange_id: Mapped[int] = mapped_column(ForeignKey("exchanges.id"), nullable=False)
    receiver_id: Mapped[int] = mapped_column(ForeignKey(USERS_ID_FK), nullable=False)
    sender_id: Mapped[int] = mapped_column(ForeignKey(USERS_ID_FK), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __init__(self, **kwargs):
        # Validate sender and receiver are different
        sender_id = kwargs.get('sender_id')
        receiver_id = kwargs.get('receiver_id')
        if sender_id is not None and receiver_id is not None:
            if sender_id == receiver_id:
                raise ValueError("Sender and receiver must be different")
        
        # Validate content
        content = kwargs.get('content')
        if content is not None:
            if not content or len(content.strip()) == 0:
                raise ValueError("Content cannot be empty")
            if len(content) > 1000:
                raise ValueError("Content cannot be longer than 1000 characters")
        
        # Set default values
        if 'is_read' not in kwargs:
            kwargs['is_read'] = False
        
        super().__init__(**kwargs)

    def __str__(self):
        read_status = "read" if self.is_read else "unread"
        return f"Message {self.id}: User {self.sender_id} -> User {self.receiver_id} ({read_status})"
    
    def __repr__(self):
        return f"<Message id={self.id} sender={self.sender_id} receiver={self.receiver_id} read={self.is_read}>"

    exchange: Mapped["Exchange"] = relationship("Exchange", back_populates="messages")
    receiver: Mapped["User"] = relationship("User", foreign_keys=[receiver_id])
    sender: Mapped["User"] = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")


#  Friendship


class Friendship(Base):
    __tablename__ = "friendships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(USERS_ID_FK), nullable=False)
    friend_id: Mapped[int] = mapped_column(ForeignKey(USERS_ID_FK), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending, accepted, rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, onupdate=func.now()
    )

    def __init__(self, **kwargs):
        # Validate status
        status = kwargs.get('status')
        if status is not None:
            valid_statuses = ["pending", "accepted", "blocked"]
            if status not in valid_statuses:
                raise ValueError(f"Status must be one of {valid_statuses}")
        
        # Validate users are different
        user_id = kwargs.get('user_id')
        friend_id = kwargs.get('friend_id')
        if user_id is not None and friend_id is not None:
            if user_id == friend_id:
                raise ValueError("Users in friendship must be different")
        
        super().__init__(**kwargs)

    def __str__(self):
        return f"Friendship {self.id}: User {self.user_id} <-> User {self.friend_id} ({self.status})"
    
    def __repr__(self):
        return f"<Friendship id={self.id} user_id={self.user_id} friend_id={self.friend_id} status={self.status}>"

    requester: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    friend: Mapped["User"] = relationship("User", foreign_keys=[friend_id])
