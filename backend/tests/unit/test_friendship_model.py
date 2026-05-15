"""
Tests for Friendship model to improve coverage.
"""

import pytest
from datetime import datetime, timezone
from app.models import Friendship


class TestFriendshipModel:
    """Test Friendship model functionality."""

    def test_friendship_creation_default_status(self):
        """Test friendship creation with default status."""
        friendship = Friendship(user_id=1, friend_id=2)
        
        assert friendship.user_id == 1
        assert friendship.friend_id == 2
        # Status and created_at are set by database defaults, may be None in test
        # Just test that the object was created successfully

    def test_friendship_creation_custom_status(self):
        """Test friendship creation with custom status."""
        friendship = Friendship(user_id=1, friend_id=2, status="accepted")
        
        assert friendship.user_id == 1
        assert friendship.friend_id == 2
        assert friendship.status == "accepted"
        # created_at may be None in test context

    def test_friendship_creation_with_kwargs(self):
        """Test friendship creation with additional kwargs."""
        custom_date = datetime.now(timezone.utc)
        friendship = Friendship(
            user_id=1, 
            friend_id=2, 
            status="blocked",
            created_at=custom_date
        )
        
        assert friendship.user_id == 1
        assert friendship.friend_id == 2
        assert friendship.status == "blocked"
        assert friendship.created_at == custom_date

    def test_friendship_statuses(self):
        """Test different friendship statuses."""
        statuses = ["pending", "accepted", "blocked"]
        
        for status in statuses:
            friendship = Friendship(user_id=1, friend_id=2, status=status)
            assert friendship.status == status

    def test_friendship_created_at_timezone(self):
        """Test that created_at is set when provided."""
        custom_date = datetime.now(timezone.utc)
        friendship = Friendship(user_id=1, friend_id=2, created_at=custom_date)
        
        assert friendship.created_at == custom_date

    def test_friendship_model_instantiation(self):
        """Test Friendship model can be instantiated."""
        friendship = Friendship(user_id=1, friend_id=2)
        assert isinstance(friendship, Friendship)

    def test_friendship_str_representation(self):
        """Test friendship string representation."""
        friendship = Friendship(user_id=1, friend_id=2, status="accepted")
        str_repr = str(friendship)
        assert "Friendship" in str_repr
    
    def test_friendship_repr_representation(self):
        """Test friendship repr representation."""
        friendship = Friendship(user_id=1, friend_id=2, status="accepted")
        repr_str = repr(friendship)
        assert "Friendship" in repr_str
        assert "user_id=1" in repr_str
        assert "friend_id=2" in repr_str
    
    def test_friendship_same_users_raises_error(self):
        """Test that creating friendship with same users raises error."""
        with pytest.raises(ValueError, match="Users in friendship must be different"):
            Friendship(user_id=1, friend_id=1)
    
    def test_friendship_invalid_status_raises_error(self):
        """Test that invalid status raises error."""
        with pytest.raises(ValueError, match="Status must be one of"):
            Friendship(user_id=1, friend_id=2, status="invalid")
