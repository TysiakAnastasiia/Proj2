"""Tests for recommendations service — targeting uncovered lines."""
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.services.recommendations import (
    RecommendationService,
    GENRE_LABELS,
    FANTASY,
    DETECTIVE,
    HISTORY,
    POETRY,
    ROMANCE,
    GEMINI_URL,
)
from app.models import BookGenre


class TestGenreLabels:
    def test_all_genre_labels_present(self):
        for genre in BookGenre:
            assert genre in GENRE_LABELS

    def test_genre_labels_are_strings(self):
        for genre, label in GENRE_LABELS.items():
            assert isinstance(label, str)

    def test_constants(self):
        assert FANTASY == "Фентезі"
        assert DETECTIVE == "Детектив"
        assert HISTORY == "Історія"
        assert POETRY == "Поезія"
        assert ROMANCE == "Роман"


class TestBuildPromptData:
    def setup_method(self):
        self.service = RecommendationService()

    def test_with_genres_and_books(self):
        data = self.service._build_prompt_data(["fantasy", "sci_fi"], ["Book1", "Book2"], 3)
        assert "fantasy" in data["genres_str"]
        assert "Book1" in data["books_str"]
        assert data["count"] == 3

    def test_empty_genres(self):
        data = self.service._build_prompt_data([], [], 5)
        assert data["genres_str"] == "різні жанри"
        assert data["books_str"] == "не вказано"
        assert data["count"] == 5

    def test_many_books_truncated(self):
        books = [f"Book{i}" for i in range(20)]
        data = self.service._build_prompt_data(["genre"], books, 3)
        # Should only include first 10
        assert "Book10" not in data["books_str"]

    def test_exactly_10_books(self):
        books = [f"Book{i}" for i in range(10)]
        data = self.service._build_prompt_data(["genre"], books, 3)
        assert "Book9" in data["books_str"]


class TestBuildPrompt:
    def setup_method(self):
        self.service = RecommendationService()

    def test_prompt_contains_genre_info(self):
        data = {"genres_str": "fantasy", "books_str": "Book1", "count": 3}
        prompt = self.service._build_prompt(data, 3)
        assert "fantasy" in prompt
        assert "Book1" in prompt
        assert "3" in prompt

    def test_prompt_is_string(self):
        data = {"genres_str": "x", "books_str": "y", "count": 2}
        result = self.service._build_prompt(data, 2)
        assert isinstance(result, str)
        assert len(result) > 50


class TestCleanAiResponse:
    def setup_method(self):
        self.service = RecommendationService()

    def test_clean_response_without_markdown(self):
        raw = '[{"title": "Book"}]'
        result = self.service._clean_ai_response(raw)
        assert result == '[{"title": "Book"}]'

    def test_clean_response_with_json_fence(self):
        raw = '```json\n[{"title": "Book"}]\n```'
        result = self.service._clean_ai_response(raw)
        assert "[" in result

    def test_clean_response_with_backtick_fence(self):
        raw = '```\n[{"title": "Book"}]\n```'
        result = self.service._clean_ai_response(raw)
        assert result.strip().startswith("[")


class TestParseAiResponse:
    def setup_method(self):
        self.service = RecommendationService()

    def test_valid_json(self):
        raw = '[{"title": "Book", "author": "Author"}]'
        result = self.service._parse_ai_response(raw)
        assert isinstance(result, list)
        assert result[0]["title"] == "Book"

    def test_invalid_json_returns_empty(self):
        raw = "not valid json"
        result = self.service._parse_ai_response(raw)
        assert result == []

    def test_empty_array(self):
        raw = "[]"
        result = self.service._parse_ai_response(raw)
        assert result == []


class TestGetAiRecommendations:
    def setup_method(self):
        self.service = RecommendationService()

    def test_get_ai_recommendations_makes_request(self):
        mock_response_data = {
            "candidates": [{"content": {"parts": [{"text": '[{"title": "Test"}]'}]}}]
        }
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_response_data).encode()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            with patch("app.core.config.settings") as mock_settings:
                mock_settings.gemini_api_key = "test_key"
                result = self.service._get_ai_recommendations("test prompt")
                assert '[{"title": "Test"}]' in result

    def test_get_ai_recommendations_network_error(self):
        with patch("urllib.request.urlopen", side_effect=Exception("Network error")):
            with patch("app.core.config.settings") as mock_settings:
                mock_settings.gemini_api_key = "test_key"
                with pytest.raises(Exception):
                    self.service._get_ai_recommendations("test prompt")


class TestGetRecommendationsAsync:
    def setup_method(self):
        self.service = RecommendationService()

    @pytest.mark.asyncio
    async def test_get_recommendations_fallback_on_error(self):
        with patch.object(self.service, "_get_ai_recommendations", side_effect=Exception("Error")):
            result = await self.service.get_recommendations(["fantasy"], ["Book1"], 3)
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_recommendations_success(self):
        mock_books = [{"title": "Test Book", "author": "Author", "genre": "Fantasy", "reason": "Good", "description": "Desc"}]
        with patch.object(self.service, "_get_ai_recommendations", return_value=json.dumps(mock_books)):
            result = await self.service.get_recommendations(["fantasy"], [], 1)
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_recommendations_empty_genres(self):
        with patch.object(self.service, "_get_ai_recommendations", side_effect=Exception("err")):
            result = await self.service.get_recommendations([], [], 3)
            assert isinstance(result, list)


class TestFallbackRecommendations:
    def setup_method(self):
        self.service = RecommendationService()

    def test_fallback_detective(self):
        result = self.service._get_fallback_recommendations(["детектив"], 3)
        assert len(result) <= 3
        assert all("title" in r for r in result)

    def test_fallback_poetry(self):
        result = self.service._get_fallback_recommendations(["поезія"], 2)
        assert len(result) <= 2

    def test_fallback_fantasy(self):
        result = self.service._get_fallback_recommendations(["фантастика"], 3)
        assert len(result) <= 3

    def test_fallback_romance(self):
        result = self.service._get_fallback_recommendations(["романтика"], 2)
        assert len(result) <= 2

    def test_fallback_history(self):
        result = self.service._get_fallback_recommendations(["історія"], 3)
        assert len(result) <= 3

    def test_fallback_unknown_genre_uses_defaults(self):
        result = self.service._get_fallback_recommendations(["unknown_genre_xyz"], 3)
        assert len(result) <= 3

    def test_fallback_empty_genres(self):
        result = self.service._get_fallback_recommendations([], 3)
        assert len(result) == 3

    def test_fallback_count_respected(self):
        result = self.service._get_fallback_recommendations(["детектив", "поезія"], 1)
        assert len(result) == 1

    def test_fallback_no_duplicates(self):
        result = self.service._get_fallback_recommendations(["детектив", "поезія", "фантастика"], 5)
        titles = [r["title"] for r in result]
        assert len(titles) == len(set(titles))


class TestGenreBooks:
    def setup_method(self):
        self.service = RecommendationService()

    def test_get_detective_books(self):
        books = self.service._get_detective_books()
        assert len(books) > 0
        assert all("title" in b for b in books)

    def test_get_poetry_books(self):
        books = self.service._get_poetry_books()
        assert len(books) > 0

    def test_get_fantasy_books(self):
        books = self.service._get_fantasy_books()
        assert len(books) > 0

    def test_get_romance_books(self):
        books = self.service._get_romance_books()
        assert len(books) > 0

    def test_get_history_books(self):
        books = self.service._get_history_books()
        assert len(books) > 0

    def test_get_default_books(self):
        books = self.service._get_default_books()
        assert len(books) > 0

    def test_get_genre_books_dict(self):
        genre_books = self.service._get_genre_books()
        assert "детектив" in genre_books
        assert "поезія" in genre_books
        assert "фантастика" in genre_books
        assert "романтика" in genre_books
        assert "історія" in genre_books


class TestHelperMethods:
    def setup_method(self):
        self.service = RecommendationService()

    def test_genre_matches_true(self):
        assert self.service._genre_matches("детектив", "детектив") is True

    def test_genre_matches_partial(self):
        assert self.service._genre_matches("детектив", "детектив і трилер") is True

    def test_genre_matches_false(self):
        assert self.service._genre_matches("детектив", "поезія") is False

    def test_should_add_book_true(self):
        book = {"title": "New Book"}
        used = set()
        recs = []
        assert self.service._should_add_book(book, used, recs, 3) is True

    def test_should_add_book_already_used(self):
        book = {"title": "Old Book"}
        used = {"Old Book"}
        recs = [{"title": "Old Book"}]
        assert self.service._should_add_book(book, used, recs, 3) is False

    def test_should_add_book_count_reached(self):
        book = {"title": "New Book"}
        used = set()
        recs = [{"title": f"Book{i}"} for i in range(3)]
        assert self.service._should_add_book(book, used, recs, 3) is False

    def test_add_books_to_recommendations(self):
        books = [{"title": "Book1"}, {"title": "Book2"}]
        recs = []
        used = set()
        self.service._add_books_to_recommendations(books, recs, used, 5)
        assert len(recs) == 2
        assert "Book1" in used

    def test_fill_with_defaults(self):
        defaults = [{"title": "Default1"}, {"title": "Default2"}]
        recs = []
        used = set()
        self.service._fill_with_defaults(recs, used, defaults, 2)
        assert len(recs) == 2

    def test_fill_with_defaults_skips_used(self):
        defaults = [{"title": "Default1"}, {"title": "Default2"}]
        recs = []
        used = {"Default1"}
        self.service._fill_with_defaults(recs, used, defaults, 2)
        assert len(recs) == 1
        assert recs[0]["title"] == "Default2"

    def test_find_matching_books_for_genre(self):
        genre_books = self.service._get_genre_books()
        result = self.service._find_matching_books_for_genre("детектив", genre_books)
        assert len(result) > 0

    def test_find_matching_books_no_match(self):
        genre_books = self.service._get_genre_books()
        result = self.service._find_matching_books_for_genre("xyznomatch", genre_books)
        assert result == []

    def test_add_genre_books(self):
        genre_books = self.service._get_genre_books()
        recs = []
        used = set()
        self.service._add_genre_books(recs, used, ["детектив"], genre_books, 3)
        assert len(recs) > 0
