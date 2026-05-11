"""
Comprehensive API tests - combines multiple API route tests.
"""

import pytest


class TestAPIComprehensive:
    """Comprehensive tests for API routes and functionality."""

    def test_api_routes_import(self):
        """Test that api routes module can be imported."""
        from app.api import routes
        assert routes is not None

    def test_router_import(self):
        """Test that main router can be imported."""
        from app.api.routes import router
        assert router is not None

    def test_auth_router_import(self):
        """Test that auth router can be imported."""
        from app.api.routes import auth_router
        assert auth_router is not None

    def test_users_router_import(self):
        """Test that users router can be imported."""
        from app.api.routes import users_router
        assert users_router is not None

    def test_books_router_import(self):
        """Test that books router can be imported."""
        from app.api.routes import books_router
        assert books_router is not None

    def test_reviews_router_import(self):
        """Test that reviews router can be imported."""
        from app.api.routes import reviews_router
        assert reviews_router is not None

    def test_exchanges_router_import(self):
        """Test that exchanges router can be imported."""
        from app.api.routes import exchanges_router
        assert exchanges_router is not None

    def test_wishlist_router_import(self):
        """Test that wishlist router can be imported."""
        from app.api.routes import wishlist_router
        assert wishlist_router is not None

    def test_chat_router_import(self):
        """Test that chat router can be imported."""
        from app.api.routes import chat_router
        assert chat_router is not None

    def test_friends_router_import(self):
        """Test that friends router can be imported."""
        from app.api.routes import friends_router
        assert friends_router is not None

    def test_recs_router_import(self):
        """Test that recommendations router can be imported."""
        from app.api.routes import recs_router
        assert recs_router is not None

    def test_api_routes_structure(self):
        """Test that api routes has required components."""
        from app.api import routes
        assert hasattr(routes, 'router')
        assert hasattr(routes, 'auth_router')
        assert hasattr(routes, 'users_router')
        assert hasattr(routes, 'books_router')
        assert hasattr(routes, 'reviews_router')
        assert hasattr(routes, 'exchanges_router')
        assert hasattr(routes, 'wishlist_router')
        assert hasattr(routes, 'chat_router')
        assert hasattr(routes, 'friends_router')
        assert hasattr(routes, 'recs_router')

    def test_router_objects_are_not_none(self):
        """Test that all router objects are not None."""
        from app.api.routes import (
            router, auth_router, users_router, books_router,
            reviews_router, exchanges_router, wishlist_router,
            chat_router, friends_router, recs_router
        )
        
        assert router is not None
        assert auth_router is not None
        assert users_router is not None
        assert books_router is not None
        assert reviews_router is not None
        assert exchanges_router is not None
        assert wishlist_router is not None
        assert chat_router is not None
        assert friends_router is not None
        assert recs_router is not None

    def test_router_prefixes(self):
        """Test that routers have proper prefixes."""
        from app.api.routes import (
            auth_router, users_router, books_router,
            reviews_router, exchanges_router, wishlist_router,
            chat_router, friends_router, recs_router
        )
        
        assert auth_router.prefix == "/auth"
        assert users_router.prefix == "/users"
        assert books_router.prefix == "/books"
        assert reviews_router.prefix == "/reviews"
        assert exchanges_router.prefix == "/exchanges"
        assert wishlist_router.prefix == "/wishlist"
        assert chat_router.prefix == "/chat"
        assert friends_router.prefix == "/friends"
        assert recs_router.prefix == "/recommendations"

    def test_router_tags(self):
        """Test that routers have proper tags."""
        from app.api.routes import (
            auth_router, users_router, books_router,
            reviews_router, exchanges_router, wishlist_router,
            chat_router, friends_router, recs_router
        )
        
        assert "Auth" in auth_router.tags
        assert "Users" in users_router.tags
        assert "Books" in books_router.tags
        assert "Reviews" in reviews_router.tags
        assert "Exchanges" in exchanges_router.tags
        assert "Wishlist" in wishlist_router.tags
        assert "Chat" in chat_router.tags
        assert "Friends" in friends_router.tags
        assert "Recommendations" in recs_router.tags

    def test_router_routes_exist(self):
        """Test that routers have routes attribute."""
        from app.api.routes import (
            router, auth_router, users_router, books_router,
            reviews_router, exchanges_router, wishlist_router,
            chat_router, friends_router, recs_router
        )
        
        assert hasattr(router, 'routes')
        assert hasattr(auth_router, 'routes')
        assert hasattr(users_router, 'routes')
        assert hasattr(books_router, 'routes')
        assert hasattr(reviews_router, 'routes')
        assert hasattr(exchanges_router, 'routes')
        assert hasattr(wishlist_router, 'routes')
        assert hasattr(chat_router, 'routes')
        assert hasattr(friends_router, 'routes')
        assert hasattr(recs_router, 'routes')

    def test_get_db_import(self):
        """Test that get_db can be imported from routes."""
        from app.api.routes import get_db
        assert get_db is not None
        assert callable(get_db)

    def test_get_current_user_import(self):
        """Test that get_current_user can be imported from routes."""
        from app.api.routes import get_current_user
        assert get_current_user is not None
        assert callable(get_current_user)

    def test_models_import(self):
        """Test that models can be imported from routes."""
        from app.api.routes import User, BookGenre, ExchangeStatus
        assert User is not None
        assert BookGenre is not None
        assert ExchangeStatus is not None

    def test_services_import(self):
        """Test that services can be imported from routes."""
        from app.api.routes import (
            AuthService, UserService, BookService, ReviewService,
            ExchangeService, WishlistService, ChatService, FriendshipService
        )
        assert AuthService is not None
        assert UserService is not None
        assert BookService is not None
        assert ReviewService is not None
        assert ExchangeService is not None
        assert WishlistService is not None
        assert ChatService is not None
        assert FriendshipService is not None

    def test_user_schemas_import(self):
        """Test that user schemas can be imported from routes."""
        from app.api.routes import (
            UserRegister, UserLogin, TokenResponse, UserBase, UserUpdate, UserPublic
        )
        assert UserRegister is not None
        assert UserLogin is not None
        assert TokenResponse is not None
        assert UserBase is not None
        assert UserUpdate is not None
        assert UserPublic is not None

    def test_book_schemas_import(self):
        """Test that book schemas can be imported from routes."""
        from app.api.routes import BookCreate, BookUpdate, BookResponse, BookListResponse
        assert BookCreate is not None
        assert BookUpdate is not None
        assert BookResponse is not None
        assert BookListResponse is not None

    def test_review_schemas_import(self):
        """Test that review schemas can be imported from routes."""
        from app.api.routes import ReviewCreate, ReviewUpdate, ReviewResponse
        assert ReviewCreate is not None
        assert ReviewUpdate is not None
        assert ReviewResponse is not None

    def test_exchange_schemas_import(self):
        """Test that exchange schemas can be imported from routes."""
        from app.api.routes import ExchangeCreate, ExchangeResponse
        assert ExchangeCreate is not None
        assert ExchangeResponse is not None

    def test_other_schemas_import(self):
        """Test that other schemas can be imported from routes."""
        from app.api.routes import (
            WishlistItemResponse, MessageCreate, MessageResponse, RecommendationResponse
        )
        assert WishlistItemResponse is not None
        assert MessageCreate is not None
        assert MessageResponse is not None
        assert RecommendationResponse is not None

    def test_optional_import(self):
        """Test that Optional can be imported from routes."""
        from app.api.routes import Optional
        assert Optional is not None

    def test_query_import(self):
        """Test that Query can be imported from routes."""
        from app.api.routes import Query
        assert Query is not None

    def test_async_session_import(self):
        """Test that AsyncSession can be imported from routes."""
        from app.api.routes import AsyncSession
        assert AsyncSession is not None

    def test_api_router_import(self):
        """Test that APIRouter can be imported from routes."""
        from app.api.routes import APIRouter
        assert APIRouter is not None

    def test_depends_import(self):
        """Test that Depends can be imported from routes."""
        from app.api.routes import Depends
        assert Depends is not None
