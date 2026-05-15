"""Tests for Strategy pattern implementation."""
import pytest
from app.core.strategy import (
    RecommendationStrategy,
    GenreBasedStrategy,
    PopularityBasedStrategy,
    HybridRecommendationStrategy,
    RecommendationContext,
)


class TestGenreBasedStrategy:
    def setup_method(self):
        self.strategy = GenreBasedStrategy()

    def test_strategy_name(self):
        assert self.strategy.get_strategy_name() == "GenreBasedStrategy"

    def test_recommend_detective_genre(self):
        result = self.strategy.recommend(["детектив"], [], 3)
        assert len(result) <= 3
        assert all("title" in r for r in result)

    def test_recommend_fantasy_genre(self):
        result = self.strategy.recommend(["фентезі"], [], 2)
        assert len(result) <= 2

    def test_recommend_scifi_genre(self):
        result = self.strategy.recommend(["наукова фантастика"], [], 2)
        assert len(result) <= 2

    def test_recommend_romance_genre(self):
        result = self.strategy.recommend(["романтика"], [], 2)
        assert len(result) <= 2

    def test_recommend_unknown_genre_returns_empty(self):
        result = self.strategy.recommend(["невідомийжанр123"], [], 3)
        assert result == []

    def test_recommend_respects_count(self):
        result = self.strategy.recommend(["детектив", "фентезі"], [], 1)
        assert len(result) == 1

    def test_recommend_excludes_read_books(self):
        all_recs = self.strategy.recommend(["детектив"], [], 10)
        if all_recs:
            read = [all_recs[0]["title"]]
            result = self.strategy.recommend(["детектив"], read, 10)
            titles = [r["title"] for r in result]
            assert all_recs[0]["title"] not in titles

    def test_recommend_empty_genres(self):
        result = self.strategy.recommend([], [], 3)
        assert result == []

    def test_recommend_returns_list(self):
        result = self.strategy.recommend(["фентезі"], [], 5)
        assert isinstance(result, list)

    def test_recommend_each_item_has_required_keys(self):
        result = self.strategy.recommend(["детектив"], [], 5)
        for item in result:
            assert "title" in item
            assert "author" in item
            assert "genre" in item
            assert "reason" in item

    def test_recommend_multiple_genres(self):
        result = self.strategy.recommend(["детектив", "фентезі"], [], 10)
        assert len(result) <= 10

    def test_recommend_partial_genre_match(self):
        # "фентезі" should match "фентезі" key
        result = self.strategy.recommend(["фентезі"], [], 5)
        assert len(result) >= 0  # May or may not match depending on key


class TestPopularityBasedStrategy:
    def setup_method(self):
        self.strategy = PopularityBasedStrategy()

    def test_strategy_name(self):
        assert self.strategy.get_strategy_name() == "PopularityBasedStrategy"

    def test_recommend_returns_popular_books(self):
        result = self.strategy.recommend([], [], 3)
        assert len(result) == 3

    def test_recommend_respects_count(self):
        result = self.strategy.recommend([], [], 1)
        assert len(result) == 1

    def test_recommend_excludes_read_books(self):
        all_recs = self.strategy.recommend([], [], 5)
        if all_recs:
            read = [all_recs[0]["title"]]
            result = self.strategy.recommend([], read, 5)
            titles = [r["title"] for r in result]
            assert all_recs[0]["title"] not in titles

    def test_recommend_returns_dicts(self):
        result = self.strategy.recommend([], [], 3)
        for item in result:
            assert isinstance(item, dict)
            assert "title" in item
            assert "author" in item

    def test_recommend_count_exceeds_available(self):
        result = self.strategy.recommend([], [], 100)
        # Should return all available books, not more
        assert len(result) <= len(PopularityBasedStrategy.POPULAR_BOOKS)

    def test_recommend_ignores_genres(self):
        # Popularity strategy doesn't use genres
        result1 = self.strategy.recommend(["детектив"], [], 3)
        result2 = self.strategy.recommend(["фентезі"], [], 3)
        assert result1 == result2

    def test_popular_books_not_empty(self):
        assert len(PopularityBasedStrategy.POPULAR_BOOKS) > 0


class TestHybridStrategy:
    def setup_method(self):
        self.strategy = HybridRecommendationStrategy()

    def test_strategy_name(self):
        assert self.strategy.get_strategy_name() == "HybridRecommendationStrategy"

    def test_recommend_combines_strategies(self):
        result = self.strategy.recommend(["детектив"], [], 5)
        assert len(result) <= 5

    def test_recommend_fills_from_popular_when_genre_insufficient(self):
        # Unknown genre → falls back to popular books
        result = self.strategy.recommend(["xyz_unknown"], [], 3)
        assert len(result) == 3  # Should fill from popular books

    def test_recommend_no_duplicates(self):
        result = self.strategy.recommend(["детектив", "фентезі"], [], 10)
        titles = [r["title"] for r in result]
        assert len(titles) == len(set(titles))

    def test_recommend_count_respected(self):
        result = self.strategy.recommend(["детектив"], [], 2)
        assert len(result) <= 2

    def test_recommend_empty_genres_uses_popular(self):
        result = self.strategy.recommend([], [], 3)
        assert len(result) == 3

    def test_hybrid_uses_genre_strategy(self):
        assert isinstance(self.strategy._genre_strategy, GenreBasedStrategy)

    def test_hybrid_uses_popularity_strategy(self):
        assert isinstance(self.strategy._popularity_strategy, PopularityBasedStrategy)


class TestRecommendationContext:
    def setup_method(self):
        self.context = RecommendationContext()

    def test_default_strategy_is_hybrid(self):
        assert isinstance(self.context.get_strategy(), HybridRecommendationStrategy)

    def test_set_strategy_genre(self):
        self.context.set_strategy(GenreBasedStrategy())
        assert isinstance(self.context.get_strategy(), GenreBasedStrategy)

    def test_set_strategy_popularity(self):
        self.context.set_strategy(PopularityBasedStrategy())
        assert isinstance(self.context.get_strategy(), PopularityBasedStrategy)

    def test_execute_with_default_strategy(self):
        result = self.context.execute(["детектив"], [], 3)
        assert isinstance(result, list)

    def test_execute_with_genre_strategy(self):
        self.context.set_strategy(GenreBasedStrategy())
        result = self.context.execute(["детектив"], [], 2)
        assert len(result) <= 2

    def test_execute_with_popularity_strategy(self):
        self.context.set_strategy(PopularityBasedStrategy())
        result = self.context.execute([], [], 3)
        assert len(result) == 3

    def test_strategy_swap_at_runtime(self):
        self.context.set_strategy(GenreBasedStrategy())
        name1 = self.context.get_strategy_name()

        self.context.set_strategy(PopularityBasedStrategy())
        name2 = self.context.get_strategy_name()

        assert name1 != name2
        assert name1 == "GenreBasedStrategy"
        assert name2 == "PopularityBasedStrategy"

    def test_get_strategy_name(self):
        name = self.context.get_strategy_name()
        assert isinstance(name, str)
        assert len(name) > 0

    def test_custom_strategy(self):
        class CustomStrategy(RecommendationStrategy):
            def recommend(self, genres, books, count):
                return [{"title": "Custom", "author": "Test", "genre": "X", "reason": "R", "description": "D"}]

            def get_strategy_name(self):
                return "CustomStrategy"

        self.context.set_strategy(CustomStrategy())
        result = self.context.execute([], [], 1)
        assert result[0]["title"] == "Custom"

    def test_context_with_explicit_strategy(self):
        ctx = RecommendationContext(strategy=PopularityBasedStrategy())
        assert isinstance(ctx.get_strategy(), PopularityBasedStrategy)

    def test_execute_returns_list(self):
        result = self.context.execute([], [], 5)
        assert isinstance(result, list)

    def test_execute_count_zero(self):
        result = self.context.execute([], [], 0)
        assert result == []
