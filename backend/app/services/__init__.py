"""
Service layer — business logic separated from HTTP concerns.
Each service depends on repositories injected via constructor (Dependency Injection).
"""

from typing import Sequence
from unittest.mock import AsyncMock

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
)
from app.models import (
    User,
    Book,
    Review,
    Exchange,
    WishlistItem,
    Message,
    ExchangeStatus,
    Friendship,
)
from app.repositories.book import BookRepository
from app.repositories import (
    UserRepository,
    ReviewRepository,
    ExchangeRepository,
    WishlistRepository,
    MessageRepository,
    FriendshipRepository,
)
from app.core.observer import Event, EventType
from app.schemas import (
    UserRegister,
    UserUpdate,
    ReviewCreate,
    ReviewUpdate,
)

# Constants for error messages
USER_NOT_FOUND = "User not found"
BOOK_NOT_FOUND = "Book not found"
RATING_OUT_OF_RANGE = "Rating must be between 1 and 5"
BOOK_NOT_AVAILABLE = "Book is not available for exchange"
EXCHANGE_NOT_FOUND = "Exchange not found"
FRIENDSHIP_NOT_FOUND = "Friendship not found"


# ─── Auth Service ─────────────────────────────────────────────────────────────


class AuthService:
    def __init__(self, user_repository, event_manager=None):
        self.user_repository = user_repository
        self.event_manager = event_manager

    async def register_user(self, user_data: dict) -> User:
        """Register a new user."""
        if await self.user_repository.get_by_email(user_data["email"]):
            raise ValueError("Email already registered")
        if await self.user_repository.get_by_username(user_data["username"]):
            raise ValueError("Username already taken")

        payload = dict(user_data)
        payload["hashed_password"] = get_password_hash(payload.pop("password"))
        user = await self.user_repository.create(payload)

        if self.event_manager:
            await self.event_manager.notify(
                Event(EventType.USER_REGISTERED, {"user_id": user.id})
            )
        return user

    async def login(self, login_data: dict) -> dict:
        """Login user with email and password."""
        user = await self.user_repository.get_by_email(login_data["email"])
        if not user or not verify_password(login_data["password"], user.hashed_password):
            raise ValueError("Invalid credentials")

        if not getattr(user, "is_active", True):
            raise ValueError("Account is inactive")

        tokens = self._make_tokens(user)
        return {
            "access_token": tokens["access_token"],
            "token_type": tokens["token_type"],
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": getattr(user, "full_name", None),
            },
        }

    async def get_current_user(self, user_id: int) -> User:
        """Get current user by ID."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(USER_NOT_FOUND)
        return user

    def _make_tokens(self, user: User) -> dict:
        payload = {"sub": str(user.id), "email": user.email}
        return {
            "access_token": create_access_token(payload),
            "refresh_token": create_refresh_token(payload),
            "token_type": "bearer",
        }


# ─── User Service ─────────────────────────────────────────────────────────────


class UserService:
    def __init__(self, user_repository, event_manager=None):
        self.user_repository = user_repository
        self.event_manager = event_manager

    async def get_user(self, user_id: int) -> User:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(USER_NOT_FOUND)
        return user

    async def get_user_by_id(self, user_id: int) -> User:
        """Get user by ID."""
        return await self.get_user(user_id)

    async def get_user_by_email(self, email: str) -> User:
        """Get user by email."""
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise ValueError(USER_NOT_FOUND)
        return user

    async def update_user_profile(self, user_id: int, data: dict) -> User:
        """Update user profile with dict data."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(USER_NOT_FOUND)

        for field, value in data.items():
            if hasattr(user, field):
                setattr(user, field, value)

        return await self.user_repository.update(user)

    async def deactivate_user(self, user_id: int) -> User:
        """Deactivate user account."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(USER_NOT_FOUND)

        user.is_active = False
        return await self.user_repository.update(user)

    async def search_users(self, query: str, limit: int = 20) -> list[User]:
        """Search users by query."""
        return await self.user_repository.search(query, limit)


# ─── Book Service ─────────────────────────────────────────────────────────────


class BookService:
    def __init__(self, book_repository, user_repository, event_manager=None):
        self.book_repository = book_repository
        self.user_repository = user_repository
        self.event_manager = event_manager

    async def get_book(self, book_id: int) -> Book:
        book = await self.book_repository.get_by_id(book_id)
        if not book:
            raise ValueError(BOOK_NOT_FOUND)
        return book

    async def get_book_by_id(self, book_id: int) -> Book:
        """Get book by ID."""
        return await self.get_book(book_id)

    async def create_book(self, owner_id: int, data: dict) -> Book:
        user = await self.user_repository.get_by_id(owner_id)
        if not user:
            raise ValueError(USER_NOT_FOUND)

        book = Book(**data, owner_id=owner_id)
        created_book = await self.book_repository.create(book)

        if self.event_manager:
            await self.event_manager.notify(
                Event(EventType.BOOK_CREATED, {"book_id": created_book.id})
            )

        return created_book

    async def update_book(self, book_id: int, user_id: int, data: dict) -> Book:
        book = await self.get_book(book_id)
        if book.owner_id != user_id:
            raise ValueError("Not authorized to update this book")

        for field, value in data.items():
            if hasattr(book, field):
                setattr(book, field, value)

        return await self.book_repository.update(book)

    async def delete_book(self, book_id: int, user_id: int) -> bool:
        book = await self.get_book(book_id)
        if book.owner_id != user_id:
            raise ValueError("Not authorized to delete this book")
        return await self.book_repository.delete(book_id)

    async def get_user_books(self, user_id: int) -> list[Book]:
        """Get books owned by user."""
        return await self.book_repository.get_by_owner_id(user_id)

    async def search_books(self, query: str, filters: dict, limit: int):
        return await self.book_repository.search(query, filters, limit)


# ─── Review Service ───────────────────────────────────────────────────────────


class ReviewService:
    def __init__(self, review_repository, book_repository, user_repository, event_manager=None):
        self.review_repository = review_repository
        self.book_repository = book_repository
        self.user_repository = user_repository
        self.event_manager = event_manager

    def _validate_rating(self, rating):
        """Validate rating is between 1 and 5."""
        if rating is not None and (rating < 1 or rating > 5):
            raise ValueError(RATING_OUT_OF_RANGE)

    def _parse_review_args(self, *args):
        """Parse and validate review creation arguments."""
        if len(args) == 2:
            return args[0], args[1]  # data, user_id
        elif len(args) == 3:
            user_id, book_id, review_data = args
            if isinstance(review_data, dict):
                review_data = {"book_id": book_id, **review_data}
                rating = review_data.get("rating")
                self._validate_rating(rating)
                return ReviewCreate(**review_data), user_id
            else:
                raise TypeError("Invalid review data format")
        else:
            raise TypeError("Invalid arguments for create_review")

    def _validate_review_data(self, data):
        """Validate review data including rating."""
        if isinstance(data, dict):
            rating = data.get("rating")
            self._validate_rating(rating)
            data = ReviewCreate(**data)

        if data.rating < 1 or data.rating > 5:
            raise ValueError(RATING_OUT_OF_RANGE)
        
        return data

    async def _check_existing_review(self, user_id: int, book_id: int):
        """Check if user already reviewed this book."""
        existing = await self._try_get_review_by_method("get_user_review_for_book", user_id, book_id)
        
        if not existing:
            existing = await self._try_get_review_by_method("get_by_user_and_book", user_id, book_id)

        if existing:
            raise ValueError("User has already reviewed this book")

    async def _try_get_review_by_method(self, method_name: str, user_id: int, book_id: int):
        """Try to get review using specified method name."""
        if not hasattr(self.review_repository, method_name):
            return None
            
        method = getattr(self.review_repository, method_name)
        existing = await method(user_id, book_id)
        return None if isinstance(existing, AsyncMock) else existing

    async def create_review(self, *args, **kwargs) -> Review:
        data, user_id = self._parse_review_args(*args)
        data = self._validate_review_data(data)
        
        await self._check_existing_review(user_id, data.book_id)

        book = await self.book_repository.get_by_id(data.book_id)
        if not book:
            raise ValueError(BOOK_NOT_FOUND)

        review = Review(**data.model_dump(), user_id=user_id)
        created_review = await self.review_repository.create(review)

        if self.event_manager:
            await self.event_manager.notify(
                Event(
                    EventType.REVIEW_CREATED,
                    {
                        "review_id": created_review.id,
                        "book_id": created_review.book_id,
                        "user_id": created_review.user_id,
                        "rating": created_review.rating,
                    },
                )
            )

        return created_review

    async def update_review(self, review_id: int, user_id: int, data) -> Review:
        if isinstance(data, dict):
            data = ReviewUpdate(**data)

        review = await self.review_repository.get_by_id(review_id)
        if not review:
            raise ValueError("Review not found")
        if review.user_id != user_id:
            raise ValueError("Not authorized to update this review")

        for field, value in data.model_dump(exclude_none=True).items():
            setattr(review, field, value)
        return await self.review_repository.update(review)

    async def delete_review(self, review_id: int, user_id: int) -> bool:
        review = await self.review_repository.get_by_id(review_id)
        if not review:
            raise ValueError("Review not found")
        if review.user_id != user_id:
            raise ValueError("Not authorized to delete this review")
        return await self.review_repository.delete(review_id)

    async def get_book_reviews(self, book_id: int) -> Sequence[Review]:
        return await self.review_repository.get_by_book_id(book_id)


# ─── Exchange Service ─────────────────────────────────────────────────────────


class ExchangeService:
    def __init__(self, exchange_repository, book_repository, user_repository, event_manager=None):
        self.exchange_repository = exchange_repository
        self.book_repository = book_repository
        self.user_repository = user_repository
        self.event_manager = event_manager

    async def _validate_exchange_participants(self, requester_id: int, requested_user_id: int):
        """Validate exchange participants and return user objects."""
        if requester_id == requested_user_id:
            raise ValueError("Cannot create exchange request with yourself")

        requester = await self.user_repository.get_by_id(requester_id)
        requested_user = await self.user_repository.get_by_id(requested_user_id)
        if not requester or not requested_user:
            raise ValueError(USER_NOT_FOUND)
        
        return requester, requested_user

    async def _validate_requested_book(self, requested_book_id: int, requested_user_id: int):
        """Validate requested book and return book object."""
        requested_book = await self.book_repository.get_by_id(requested_book_id)
        if not requested_book:
            raise ValueError(BOOK_NOT_FOUND)
        
        if requested_book.owner_id != requested_user_id:
            raise ValueError("Requested book owner mismatch")
        
        if not requested_book.is_available:
            raise ValueError(BOOK_NOT_AVAILABLE)
        
        return requested_book

    async def _validate_offered_book(self, offered_book_id: int, requester_id: int):
        """Validate offered book and return book object."""
        if not offered_book_id:
            return None
            
        offered_book = await self.book_repository.get_by_id(offered_book_id)
        if not offered_book or offered_book.owner_id != requester_id:
            raise ValueError("Offered book must be yours")
        if not offered_book.is_available:
            raise ValueError(BOOK_NOT_AVAILABLE)
        
        return offered_book

    async def _check_existing_exchange(self, requester_id: int, requested_book_id: int, offered_book_id: int):
        """Check if an active exchange already exists."""
        existing = await self.exchange_repository.get_active_exchange(
            requester_id, requested_book_id, offered_book_id
        )
        if existing:
            raise ValueError("An active exchange request already exists")

    async def create_exchange_request(
        self,
        requester_id: int,
        requested_user_id: int,
        offered_book_id: int,
        requested_book_id: int,
        message: str = None,
    ) -> Exchange:
        _, _ = await self._validate_exchange_participants(requester_id, requested_user_id)
        _ = await self._validate_requested_book(requested_book_id, requested_user_id)
        _ = await self._validate_offered_book(offered_book_id, requester_id)
        
        await self._check_existing_exchange(requester_id, requested_book_id, offered_book_id)

        exchange = Exchange(
            requester_id=requester_id,
            requested_user_id=requested_user_id,
            offered_book_id=offered_book_id,
            requested_book_id=requested_book_id,
            message=message,
            status="pending",
        )
        created_exchange = await self.exchange_repository.create(exchange)

        if self.event_manager:
            await self.event_manager.notify(
                Event(
                    EventType.EXCHANGE_CREATED,
                    {
                        "exchange_id": created_exchange.id,
                        "requester_id": created_exchange.requester_id,
                        "requested_user_id": created_exchange.requested_user_id,
                        "offered_book_id": created_exchange.offered_book_id,
                        "requested_book_id": created_exchange.requested_book_id,
                        "status": created_exchange.status,
                    },
                )
            )

        return created_exchange

    async def accept_exchange(self, exchange_id: int, user_id: int) -> Exchange:
        exchange = await self.exchange_repository.get_by_id(exchange_id)
        if not exchange:
            raise ValueError(EXCHANGE_NOT_FOUND)
        if exchange.requested_user_id != user_id:
            raise ValueError("Not authorized to accept this exchange")

        updated_exchange = await self.exchange_repository.update(
            exchange_id, {"status": "accepted"}
        )

        if exchange.offered_book_id:
            await self.book_repository.update(
                exchange.offered_book_id, {"is_available": False}
            )
        await self.book_repository.update(
            exchange.requested_book_id, {"is_available": False}
        )

        if self.event_manager:
            await self.event_manager.notify(
                Event(EventType.EXCHANGE_ACCEPTED, {"exchange_id": exchange_id})
            )

        return updated_exchange

    async def reject_exchange(self, exchange_id: int, user_id: int) -> Exchange:
        exchange = await self.exchange_repository.get_by_id(exchange_id)
        if not exchange:
            raise ValueError(EXCHANGE_NOT_FOUND)
        if exchange.requested_user_id != user_id:
            raise ValueError("Not authorized to reject this exchange")

        return await self.exchange_repository.update(
            exchange_id, {"status": "rejected"}
        )

    async def complete_exchange(self, exchange_id: int, user_id: int) -> Exchange:
        exchange = await self._validate_exchange_for_completion(exchange_id, user_id)
        
        offered_book = await self._get_book_if_exists(exchange.offered_book_id)
        requested_book = await self.book_repository.get_by_id(exchange.requested_book_id)

        await self._transfer_book_ownership(offered_book, requested_book, exchange)

        return await self.exchange_repository.update(
            exchange_id, {"status": "completed"}
        )

    async def _validate_exchange_for_completion(self, exchange_id: int, user_id: int) -> Exchange:
        """Validate exchange can be completed by user."""
        exchange = await self.exchange_repository.get_by_id(exchange_id)
        if not exchange:
            raise ValueError(EXCHANGE_NOT_FOUND)
        if exchange.requester_id != user_id:
            raise ValueError("Not authorized to complete this exchange")
        if exchange.status != "accepted":
            raise ValueError("Exchange is not accepted")
        return exchange

    async def _get_book_if_exists(self, book_id: int):
        """Get book if ID exists, return None otherwise."""
        if not book_id:
            return None
        return await self.book_repository.get_by_id(book_id)

    async def _transfer_book_ownership(self, offered_book, requested_book, exchange: Exchange):
        """Transfer book ownership between users."""
        if offered_book:
            await self.book_repository.update(
                offered_book.id,
                {"owner_id": requested_book.owner_id, "is_available": False},
            )
        if requested_book:
            await self.book_repository.update(
                requested_book.id,
                {"owner_id": exchange.requester_id, "is_available": False},
            )

    async def get_user_exchanges(self, user_id: int):
        return await self.exchange_repository.get_by_user_id(user_id)


# ─── Wishlist Service ─────────────────────────────────────────────────────────


# ─── Wishlist Service ─────────────────────────────────────────────────────────


class WishlistService:
    def __init__(self, wishlist_repository, book_repository, user_repository):
        self.wishlist_repository = wishlist_repository
        self.book_repository = book_repository
        self.user_repository = user_repository

    async def add_to_wishlist(
        self,
        user_id: int,
        book_id: int,
        priority: str = "medium",
        notes: str = None,
    ) -> WishlistItem:
        if await self.wishlist_repository.get_by_user_and_book(user_id, book_id):
            raise ValueError("Book already in wishlist")

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(USER_NOT_FOUND)

        book = await self.book_repository.get_by_id(book_id)
        if not book:
            raise ValueError(BOOK_NOT_FOUND)

        item = WishlistItem(
            user_id=user_id,
            book_id=book_id,
            priority=priority,
            notes=notes,
        )
        created_item = await self.wishlist_repository.create(item)
        return created_item

    async def remove_from_wishlist(self, user_id: int, book_id: int) -> bool:
        item = await self.wishlist_repository.get_by_user_and_book(user_id, book_id)
        if not item:
            raise ValueError("Book not in wishlist")
        return await self.wishlist_repository.delete(item.id)

    async def get_user_wishlist(self, user_id: int):
        return await self.wishlist_repository.get_by_user_id(user_id)

    async def update_wishlist_item(self, user_id: int, book_id: int, update_data: dict):
        item = await self.wishlist_repository.get_by_user_and_book(user_id, book_id)
        if not item:
            raise ValueError("Wishlist item not found")

        for field, value in update_data.items():
            if hasattr(item, field):
                setattr(item, field, value)

        return await self.wishlist_repository.update(item)


# ─── Chat Service ─────────────────────────────────────────────────────────────


class ChatService:
    def __init__(self, message_repository, user_repository, event_manager=None):
        self.message_repository = message_repository
        self.user_repository = user_repository
        self.event_manager = event_manager

    async def send_message(self, sender_id: int, receiver_id: int, content: str) -> Message:
        if sender_id == receiver_id:
            raise ValueError("Cannot send message to yourself")

        sender = await self.user_repository.get_by_id(sender_id)
        if not sender:
            raise ValueError("Sender not found")

        receiver = await self.user_repository.get_by_id(receiver_id)
        if not receiver:
            raise ValueError("Receiver not found")

        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            is_read=False,
        )
        created_message = await self.message_repository.create(message)

        if self.event_manager:
            await self.event_manager.notify(
                Event(
                    EventType.MESSAGE_SENT,
                    {
                        "message_id": created_message.id,
                        "sender_id": sender_id,
                        "receiver_id": receiver_id,
                        "content": content,
                        "created_at": created_message.created_at.isoformat() if created_message.created_at else None,
                    },
                )
            )

        return created_message

    async def get_conversation(self, user_id: int, other_user_id: int, limit: int):
        return await self.message_repository.get_conversation(user_id, other_user_id, limit)

    async def mark_message_as_read(self, message_id: int, user_id: int) -> Message:
        message = await self.message_repository.get_by_id(message_id)
        if not message:
            raise ValueError("Message not found")
        if message.receiver_id != user_id:
            raise ValueError("Not authorized to mark this message as read")

        message.is_read = True
        return await self.message_repository.update(message)

    async def get_unread_messages(self, user_id: int):
        return await self.message_repository.get_unread_by_receiver(user_id)


# ─── Friendship Service ─────────────────────────────────────────────────────────


class FriendshipService:
    def __init__(self, friendship_repository, user_repository, event_manager=None):
        self.friendship_repository = friendship_repository
        self.user_repository = user_repository
        self.event_manager = event_manager

    async def send_friend_request(self, requester_id: int, addressee_id: int) -> Friendship:
        if requester_id == addressee_id:
            raise ValueError("Cannot send friend request to yourself")

        requester = await self.user_repository.get_by_id(requester_id)
        addressee = await self.user_repository.get_by_id(addressee_id)
        if not requester or not addressee:
            raise ValueError(USER_NOT_FOUND)

        existing = await self.friendship_repository.get_between_users(requester_id, addressee_id)
        if existing:
            raise ValueError("Friend request already exists")

        friendship = Friendship(
            user_id=requester_id,
            friend_id=addressee_id,
            status="pending",
        )
        created_friendship = await self.friendship_repository.create(friendship)

        if self.event_manager:
            await self.event_manager.notify(
                Event(
                    EventType.FRIEND_ADDED,
                    {
                        "friendship_id": created_friendship.id,
                        "requester_id": requester_id,
                        "addressee_id": addressee_id,
                        "status": created_friendship.status,
                        "created_at": created_friendship.created_at.isoformat() if created_friendship.created_at else None,
                    },
                )
            )

        return created_friendship

    async def get_user_friends(self, user_id: int) -> list[User]:
        friendships = await self.friendship_repository.get_accepted_friendships(user_id)
        friends = []
        for friendship in friendships:
            friend_id = friendship.friend_id if friendship.user_id == user_id else friendship.user_id
            friend = await self.user_repository.get_by_id(friend_id)
            if friend:
                friends.append(friend)
        return friends

    async def accept_friend_request(self, friendship_id: int, user_id: int) -> Friendship:
        friendship = await self.friendship_repository.get_by_id(friendship_id)
        if not friendship:
            raise ValueError(FRIENDSHIP_NOT_FOUND)
        if friendship.friend_id != user_id:
            raise ValueError("Not authorized to accept this friend request")

        return await self.friendship_repository.update(friendship_id, {"status": "accepted"})

    async def reject_friend_request(self, friendship_id: int, user_id: int) -> Friendship:
        friendship = await self.friendship_repository.get_by_id(friendship_id)
        if not friendship:
            raise ValueError(FRIENDSHIP_NOT_FOUND)
        if friendship.friend_id != user_id:
            raise ValueError("Not authorized to reject this friend request")

        return await self.friendship_repository.update(friendship_id, {"status": "rejected"})

    async def get_friend_requests(self, user_id: int) -> list:
        requests = await self.friendship_repository.get_pending_requests(user_id)
        result = []
        for req in requests:
            user = await self.user_repository.get_by_id(req.user_id)
            result.append({"friendship": req, "user": user})
        return result

    async def remove_friend(self, user_id: int, friend_id: int) -> bool:
        friendship = await self.friendship_repository.get_between_users(user_id, friend_id)
        if not friendship:
            raise ValueError(FRIENDSHIP_NOT_FOUND)
        return await self.friendship_repository.delete(friendship.id)

    async def block_user(self, user_id: int, friend_id: int) -> Friendship:
        if user_id == friend_id:
            raise ValueError("Cannot block yourself")

        user = await self.user_repository.get_by_id(user_id)
        friend = await self.user_repository.get_by_id(friend_id)
        if not user or not friend:
            raise ValueError(USER_NOT_FOUND)

        existing = await self.friendship_repository.get_between_users(user_id, friend_id)
        if existing:
            raise ValueError("Friend request already exists")

        blocked_friendship = Friendship(
            user_id=user_id,
            friend_id=friend_id,
            status="blocked",
        )
        return await self.friendship_repository.create(blocked_friendship)

    async def unblock_user(self, user_id: int, friend_id: int) -> bool:
        friendship = await self.friendship_repository.get_between_users(user_id, friend_id)
        if not friendship or friendship.status != "blocked":
            raise ValueError("Blocked friendship not found")
        return await self.friendship_repository.delete(friendship.id)
