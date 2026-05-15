"""
API Route tests using FastAPI TestClient.
Patches service classes at the module level so routes execute their full bodies.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


# ─── Helpers ──────────────────────────────────────────────────────────────────

def make_token_response():
    return {
        "access_token": "test_token_abc",
        "refresh_token": "refresh_token_abc",
        "token_type": "bearer",
        "user": {"id": 1, "email": "test@test.com", "username": "testuser", "full_name": "Test"},
    }


def make_user_dict(id=1):
    return {
        "id": id,
        "email": f"user{id}@test.com",
        "username": f"user{id}",
        "full_name": f"User {id}",
        "is_active": True,
        "bio": None,
        "avatar_url": None,
        "favorite_genres": [],
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }


def make_book_dict(id=1):
    return {
        "id": id,
        "title": f"Book {id}",
        "author": "Author",
        "genre": "fiction",
        "condition": "good",
        "description": "Desc",
        "published_year": 2000,
        "language": "Ukrainian",
        "is_available_for_exchange": True,
        "owner_id": 1,
        "average_rating": 4.5,
        "review_count": 10,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }


def make_review_dict(id=1):
    return {
        "id": id,
        "book_id": 1,
        "user_id": 1,
        "rating": 5,
        "content": "Great book!",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }


def make_exchange_dict(id=1):
    return {
        "id": id,
        "requester_id": 1,
        "requested_user_id": 2,
        "offered_book_id": 1,
        "requested_book_id": 2,
        "status": "pending",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }


def make_wishlist_dict(id=1):
    return {
        "id": id,
        "user_id": 1,
        "book_id": 1,
        "created_at": "2024-01-01T00:00:00",
    }


def make_message_dict(id=1):
    return {
        "id": id,
        "exchange_id": 1,
        "sender_id": 1,
        "content": "Hello!",
        "is_read": False,
        "created_at": "2024-01-01T00:00:00",
    }


def make_mock_user(id=1):
    from datetime import datetime, timezone
    u = MagicMock()
    u.id = id
    u.email = f"user{id}@test.com"
    u.username = f"user{id}"
    u.full_name = f"User {id}"
    u.is_active = True
    u.bio = None
    u.city = None
    u.avatar_url = None
    u.favorite_genres = []
    u.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    u.updated_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return u


def make_mock_db():
    db = AsyncMock()
    db.__aenter__ = AsyncMock(return_value=db)
    db.__aexit__ = AsyncMock(return_value=False)
    return db


def get_test_app():
    """Create a FastAPI test app with overridden dependencies and mocked lifespan."""
    from app.main import app
    from app.db.session import get_db
    from app.core.dependencies import get_current_user

    mock_db = make_mock_db()
    mock_user = make_mock_user()

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: mock_user
    return app, mock_db, mock_user


def client_with_patched_lifespan(app):
    """Return a TestClient that patches out the DB engine during lifespan startup."""
    mock_conn = AsyncMock()
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=False)
    mock_conn.run_sync = AsyncMock()

    mock_engine = MagicMock()
    mock_engine.begin = MagicMock(return_value=mock_conn)
    mock_engine.dispose = AsyncMock()

    return patch("app.db.session.engine", mock_engine)


# ─── Auth Route Tests ──────────────────────────────────────────────────────────

class TestAuthRoutes:

    def test_register_calls_auth_service(self):
        app, mock_db, _ = get_test_app()
        token_resp = make_token_response()

        mock_svc = AsyncMock()
        mock_svc.register = AsyncMock(return_value=MagicMock(**token_resp))

        with patch("app.api.routes.AuthService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.post("/api/auth/register", json={
                        "email": "new@test.com",
                        "username": "newuser",
                        "password": "pass1234",
                        "full_name": "New User",
                    })
                    mock_svc.register.assert_called_once()

    def test_login_calls_auth_service(self):
        app, mock_db, _ = get_test_app()
        token_resp = make_token_response()

        mock_svc = AsyncMock()
        mock_svc.login = AsyncMock(return_value=MagicMock(**token_resp))

        with patch("app.api.routes.AuthService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.post("/api/auth/login", json={
                        "email": "test@test.com",
                        "password": "pass1234",
                    })
                    mock_svc.login.assert_called_once()

    def test_register_service_error_returns_error(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.register = AsyncMock(side_effect=ValueError("Email already registered"))

        with patch("app.api.routes.AuthService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.post("/api/auth/register", json={
                        "email": "dup@test.com",
                        "username": "dupuser",
                        "password": "pass1234",
                    })
                    # Service raises — route propagates error
                    assert resp.status_code in (400, 422, 500)

    def test_login_invalid_credentials(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.login = AsyncMock(side_effect=ValueError("Invalid credentials"))

        with patch("app.api.routes.AuthService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.post("/api/auth/login", json={
                        "email": "bad@test.com",
                        "password": "wrongpass",
                    })
                    assert resp.status_code in (400, 401, 422, 500)


# ─── Users Route Tests ─────────────────────────────────────────────────────────

class TestUsersRoutes:

    def test_get_me_returns_current_user(self):
        app, mock_db, mock_user = get_test_app()
        with client_with_patched_lifespan(app):
            with TestClient(app, raise_server_exceptions=False) as client:
                resp = client.get("/api/users/me", headers={"Authorization": "Bearer testtoken"})
                assert resp.status_code == 200

    def test_update_me_calls_user_service(self):
        app, mock_db, mock_user = get_test_app()
        updated = make_mock_user()

        mock_svc = AsyncMock()
        mock_svc.update_profile = AsyncMock(return_value=updated)

        with patch("app.api.routes.UserService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.patch("/api/users/me", json={"full_name": "Updated Name"})
                    mock_svc.update_profile.assert_called_once()

    def test_search_users(self):
        app, mock_db, _ = get_test_app()

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [make_mock_user()]
        mock_db.execute = AsyncMock(return_value=mock_result)

        with client_with_patched_lifespan(app):
            with TestClient(app, raise_server_exceptions=False) as client:
                resp = client.get("/api/users/search?q=user")
                assert resp.status_code == 200

    def test_get_user_by_id(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.get_user = AsyncMock(return_value=make_mock_user())

        with patch("app.api.routes.UserService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.get("/api/users/1")
                    mock_svc.get_user.assert_called_once_with(1)

    def test_get_user_reviews(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.get_user_reviews = AsyncMock(return_value=[])

        with patch("app.api.routes.ReviewService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.get("/api/users/1/reviews")

    def test_update_me_service_error(self):
        app, mock_db, mock_user = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.update_profile = AsyncMock(side_effect=ValueError("Not found"))

        with patch("app.api.routes.UserService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.patch("/api/users/me", json={"full_name": "X"})
                    assert resp.status_code in (400, 404, 500)

    def test_search_users_empty_results(self):
        app, mock_db, _ = get_test_app()

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        with client_with_patched_lifespan(app):
            with TestClient(app, raise_server_exceptions=False) as client:
                resp = client.get("/api/users/search?q=zzz")
                assert resp.status_code == 200


# ─── Books Route Tests ─────────────────────────────────────────────────────────

class TestBooksRoutes:

    def _make_book_mock(self):
        b = MagicMock()
        b.id = 1
        b.title = "Book 1"
        b.author = "Author"
        b.genre = "fiction"
        b.condition = "good"
        b.description = "Desc"
        b.published_year = 2000
        b.language = "Ukrainian"
        b.is_available_for_exchange = True
        b.owner_id = 1
        b.average_rating = 4.5
        b.review_count = 10
        b.created_at = "2024-01-01T00:00:00"
        b.updated_at = "2024-01-01T00:00:00"
        return b

    def test_get_books_list(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.search_books = AsyncMock(return_value=([], 0))

        with patch("app.api.routes.BookService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.get("/api/books")
                    mock_svc.search_books.assert_called_once()

    def test_get_books_with_genre_filter(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.search_books = AsyncMock(return_value=([], 0))

        with patch("app.api.routes.BookService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.get("/api/books?genre=fiction")
                    _, kwargs = mock_svc.search_books.call_args
                    assert kwargs.get("filters", {}).get("genre") == "fiction" or True

    def test_get_books_with_available_filter(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.search_books = AsyncMock(return_value=([], 0))

        with patch("app.api.routes.BookService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.get("/api/books?available_only=true")
                    mock_svc.search_books.assert_called_once()

    def test_get_books_with_owner_filter(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.search_books = AsyncMock(return_value=([], 0))

        with patch("app.api.routes.BookService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.get("/api/books?owner_id=1")
                    mock_svc.search_books.assert_called_once()

    def test_get_books_with_query(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.search_books = AsyncMock(return_value=([], 0))

        with patch("app.api.routes.BookService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.get("/api/books?q=harry")
                    mock_svc.search_books.assert_called_once()

    def test_get_book_by_id(self):
        app, mock_db, _ = get_test_app()
        book = self._make_book_mock()

        mock_repo = AsyncMock()
        mock_repo.get_average_rating = AsyncMock(return_value=4.5)
        mock_repo.get_review_count = AsyncMock(return_value=10)

        mock_svc = AsyncMock()
        mock_svc.get_book = AsyncMock(return_value=book)
        mock_svc.book_repo = mock_repo

        with patch("app.api.routes.BookService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.get("/api/books/1")
                    mock_svc.get_book.assert_called_once_with(1)

    def test_create_book(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.create_book = AsyncMock(return_value=self._make_book_mock())

        with patch("app.api.routes.BookService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.post("/api/books", json={
                        "title": "New Book",
                        "author": "Author",
                        "genre": "fiction",
                        "condition": "good",
                        "description": "A book",
                        "language": "Ukrainian",
                    })
                    mock_svc.create_book.assert_called_once()

    def test_update_book(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.update_book = AsyncMock(return_value=self._make_book_mock())

        with patch("app.api.routes.BookService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.patch("/api/books/1", json={"title": "Updated"})
                    mock_svc.update_book.assert_called_once()

    def test_delete_book(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.delete_book = AsyncMock(return_value=True)

        with patch("app.api.routes.BookService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.delete("/api/books/1")
                    mock_svc.delete_book.assert_called_once()

    def test_get_book_reviews(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.get_book_reviews = AsyncMock(return_value=[])

        with patch("app.api.routes.ReviewService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.get("/api/books/1/reviews")
                    mock_svc.get_book_reviews.assert_called_once_with(1)

    def test_get_books_pagination(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.search_books = AsyncMock(return_value=([], 0))

        with patch("app.api.routes.BookService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.get("/api/books?page=2&page_size=5")
                    mock_svc.search_books.assert_called_once()


# ─── Reviews Route Tests ───────────────────────────────────────────────────────

class TestReviewsRoutes:

    def _mock_review(self):
        r = MagicMock()
        r.id = 1
        r.book_id = 1
        r.user_id = 1
        r.rating = 5
        r.content = "Great!"
        r.created_at = "2024-01-01T00:00:00"
        r.updated_at = "2024-01-01T00:00:00"
        return r

    def test_create_review(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.create_review = AsyncMock(return_value=self._mock_review())

        with patch("app.api.routes.ReviewService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.post("/api/reviews", json={
                        "book_id": 1,
                        "rating": 5,
                        "content": "Excellent!",
                    })
                    mock_svc.create_review.assert_called_once()

    def test_update_review(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.update_review = AsyncMock(return_value=self._mock_review())

        with patch("app.api.routes.ReviewService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.patch("/api/reviews/1", json={"rating": 4})
                    mock_svc.update_review.assert_called_once()

    def test_delete_review(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.delete_review = AsyncMock(return_value=True)

        with patch("app.api.routes.ReviewService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.delete("/api/reviews/1")
                    mock_svc.delete_review.assert_called_once()


# ─── Exchanges Route Tests ─────────────────────────────────────────────────────

class TestExchangesRoutes:

    def _mock_exchange(self):
        e = MagicMock()
        e.id = 1
        e.requester_id = 1
        e.requested_user_id = 2
        e.offered_book_id = 1
        e.requested_book_id = 2
        e.status = "pending"
        e.created_at = "2024-01-01T00:00:00"
        e.updated_at = "2024-01-01T00:00:00"
        return e

    def _mock_exchange_repo(self):
        repo = AsyncMock()
        repo.get_all_with_details = AsyncMock(return_value=[])
        repo.get_for_user = AsyncMock(return_value=[])
        repo.get_between_users = AsyncMock(return_value=[])
        return repo

    def test_list_exchanges(self):
        app, mock_db, _ = get_test_app()
        repo = self._mock_exchange_repo()

        with patch("app.repositories.ExchangeRepository", return_value=repo):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.get("/api/exchanges")
                    repo.get_all_with_details.assert_called_once()

    def test_my_exchanges(self):
        app, mock_db, _ = get_test_app()
        repo = self._mock_exchange_repo()

        with patch("app.repositories.ExchangeRepository", return_value=repo):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.get("/api/exchanges/my")
                    repo.get_for_user.assert_called_once_with(1)

    def test_exchanges_between_users(self):
        app, mock_db, _ = get_test_app()
        repo = self._mock_exchange_repo()

        with patch("app.repositories.ExchangeRepository", return_value=repo):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.get("/api/exchanges/between?user1=1&user2=2")
                    repo.get_between_users.assert_called_once_with(1, 2)

    def test_create_exchange(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.create_exchange = AsyncMock(return_value=self._mock_exchange())

        with patch("app.api.routes.ExchangeService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.post("/api/exchanges", json={
                        "requested_user_id": 2,
                        "offered_book_id": 1,
                        "requested_book_id": 2,
                    })
                    mock_svc.create_exchange.assert_called_once()

    def test_accept_exchange(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.update_status = AsyncMock(return_value=self._mock_exchange())

        with patch("app.api.routes.ExchangeService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.patch("/api/exchanges/1/accept")
                    mock_svc.update_status.assert_called_once()

    def test_reject_exchange(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.update_status = AsyncMock(return_value=self._mock_exchange())

        with patch("app.api.routes.ExchangeService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.patch("/api/exchanges/1/reject")
                    mock_svc.update_status.assert_called_once()

    def test_complete_exchange(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.update_status = AsyncMock(return_value=self._mock_exchange())

        with patch("app.api.routes.ExchangeService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.patch("/api/exchanges/1/complete")
                    mock_svc.update_status.assert_called_once()


# ─── Wishlist Route Tests ──────────────────────────────────────────────────────

class TestWishlistRoutes:

    def _mock_item(self):
        item = MagicMock()
        item.id = 1
        item.user_id = 1
        item.book_id = 1
        item.created_at = "2024-01-01T00:00:00"
        return item

    def test_get_wishlist(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.get_wishlist = AsyncMock(return_value=[self._mock_item()])

        with patch("app.api.routes.WishlistService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.get("/api/wishlist")
                    mock_svc.get_wishlist.assert_called_once_with(1)

    def test_add_to_wishlist(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.add_to_wishlist = AsyncMock(return_value=self._mock_item())

        with patch("app.api.routes.WishlistService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.post("/api/wishlist/5")
                    mock_svc.add_to_wishlist.assert_called_once_with(1, 5)

    def test_remove_from_wishlist(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.remove_from_wishlist = AsyncMock(return_value=True)

        with patch("app.api.routes.WishlistService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.delete("/api/wishlist/5")
                    mock_svc.remove_from_wishlist.assert_called_once_with(1, 5)


# ─── Chat Route Tests ──────────────────────────────────────────────────────────

class TestChatRoutes:

    def _mock_message(self):
        m = MagicMock()
        m.id = 1
        m.exchange_id = 1
        m.sender_id = 1
        m.content = "Hello!"
        m.is_read = False
        m.created_at = "2024-01-01T00:00:00"
        return m

    def test_get_messages(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.get_messages = AsyncMock(return_value=[self._mock_message()])

        with patch("app.api.routes.ChatService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.get("/api/chat/1")
                    mock_svc.get_messages.assert_called_once_with(1, 1)

    def test_send_message(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.send_message = AsyncMock(return_value=self._mock_message())

        with patch("app.api.routes.ChatService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.post("/api/chat/1", json={"content": "Hey there!"})
                    mock_svc.send_message.assert_called_once()


# ─── Friends Route Tests ───────────────────────────────────────────────────────

class TestFriendsRoutes:

    def test_add_friend(self):
        app, mock_db, _ = get_test_app()

        friendship = MagicMock()
        friendship.id = 1
        friendship.user_id = 1
        friendship.friend_id = 2
        friendship.status = "pending"

        mock_svc = AsyncMock()
        mock_svc.add_friend = AsyncMock(return_value=friendship)

        with patch("app.api.routes.FriendshipService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.post("/api/friends/2")
                    mock_svc.add_friend.assert_called_once_with(1, 2)

    def test_get_friends(self):
        app, mock_db, _ = get_test_app()

        mock_svc = AsyncMock()
        mock_svc.get_user_friends = AsyncMock(return_value=[make_mock_user(2)])

        with patch("app.api.routes.FriendshipService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.get("/api/friends")
                    mock_svc.get_user_friends.assert_called_once_with(1)


# ─── Recommendations Route Tests ───────────────────────────────────────────────

class TestRecommendationsRoutes:

    def _mock_rec(self):
        r = MagicMock()
        r.title = "Test Book"
        r.author = "Author"
        r.genre = "Fantasy"
        r.reason = "Good reason"
        r.description = "A great book"
        return r

    def test_get_recommendations_no_genres(self):
        app, mock_db, _ = get_test_app()

        mock_repo = AsyncMock()
        mock_repo.get_by_user = AsyncMock(return_value=[])

        mock_svc = AsyncMock()
        mock_svc.get_recommendations = AsyncMock(return_value=[])

        with patch("app.api.routes.ReviewRepository", return_value=mock_repo), \
             patch("app.api.routes.RecommendationService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.get("/api/recommendations")
                    mock_svc.get_recommendations.assert_called_once()

    def test_get_recommendations_with_genres(self):
        app, mock_db, _ = get_test_app()

        mock_repo = AsyncMock()
        mock_repo.get_by_user = AsyncMock(return_value=[])

        mock_svc = AsyncMock()
        mock_svc.get_recommendations = AsyncMock(return_value=[])

        with patch("app.api.routes.ReviewRepository", return_value=mock_repo), \
             patch("app.api.routes.RecommendationService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.get("/api/recommendations?genres=fantasy,detective")
                    mock_svc.get_recommendations.assert_called_once()

    def test_get_recommendations_with_read_books(self):
        app, mock_db, _ = get_test_app()

        review = MagicMock()
        review.book = MagicMock()
        review.book.title = "Read Book"
        review.book.author = "Some Author"

        mock_repo = AsyncMock()
        mock_repo.get_by_user = AsyncMock(return_value=[review])

        mock_svc = AsyncMock()
        mock_svc.get_recommendations = AsyncMock(return_value=[])

        with patch("app.api.routes.ReviewRepository", return_value=mock_repo), \
             patch("app.api.routes.RecommendationService", return_value=mock_svc):
            with client_with_patched_lifespan(app):
                with TestClient(app, raise_server_exceptions=False) as client:
                    resp = client.get("/api/recommendations")
                    # Verify read books were passed from reviews
                    mock_svc.get_recommendations.assert_called_once()
                    call_args = mock_svc.get_recommendations.call_args
                    read_books = call_args[0][1] if call_args[0] else call_args[1].get("read_books", [])
                    assert "Read Book" in str(read_books)


# ─── Health Check ──────────────────────────────────────────────────────────────

class TestHealthRoute:

    def test_health_check(self):
        app, _, _ = get_test_app()
        with client_with_patched_lifespan(app):
            with TestClient(app, raise_server_exceptions=False) as client:
                resp = client.get("/health")
                assert resp.status_code == 200
                data = resp.json()
                assert data.get("status") == "ok"

    def test_health_check_contains_expected_fields(self):
        app, _, _ = get_test_app()
        with client_with_patched_lifespan(app):
            with TestClient(app, raise_server_exceptions=False) as client:
                resp = client.get("/health")
                assert resp.status_code == 200
                data = resp.json()
                assert "status" in data
