"""
Strategy Pattern Implementation
Defines a family of algorithms, encapsulates each one, and makes them interchangeable.
Used for book recommendation strategies.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class RecommendationStrategy(ABC):
    """Abstract strategy interface for book recommendations."""

    @abstractmethod
    def recommend(
        self,
        favorite_genres: List[str],
        read_books: List[str],
        count: int,
    ) -> List[Dict[str, Any]]:
        """Return a list of book recommendations."""
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return the name of the strategy."""
        pass


class GenreBasedStrategy(RecommendationStrategy):
    """
    Strategy that recommends books based on user's favorite genres.
    Implements genre-matching algorithm.
    """

    GENRE_BOOKS: Dict[str, List[Dict[str, Any]]] = {
        "детектив": [
            {
                "title": "Убивство у Східному експресі",
                "author": "Агата Крісті",
                "genre": "Детектив",
                "reason": "Класичний детектив з Еркюлем Пуаро",
                "description": "Ідеальний детективний роман з несподіваним фіналом",
            },
            {
                "title": "Дівчина з татуюванням дракона",
                "author": "Стьюг Ларссон",
                "genre": "Детектив",
                "reason": "Сучасний шведський трилер з захоплюючою інтригою",
                "description": "Перша книга трилогії Міленіум",
            },
        ],
        "фентезі": [
            {
                "title": "Гаррі Поттер і філософський камінь",
                "author": "Джоан Роулінг",
                "genre": "Фентезі",
                "reason": "Класика жанру для всіх вікових груп",
                "description": "Початок магічної пригоди юного чарівника",
            },
            {
                "title": "Хоббіт",
                "author": "Дж. Р. Р. Толкін",
                "genre": "Фентезі",
                "reason": "Фундаментальний твір жанру епічного фентезі",
                "description": "Пригоди Більбо Беггінса у Середзем'ї",
            },
        ],
        "наукова фантастика": [
            {
                "title": "Дюна",
                "author": "Френк Герберт",
                "genre": "Наукова фантастика",
                "reason": "Епічна космічна опера про екологію та владу",
                "description": "Найвпливовіший науково-фантастичний роман XX ст.",
            },
        ],
        "романтика": [
            {
                "title": "Гордість і упередження",
                "author": "Джейн Остін",
                "genre": "Романтика",
                "reason": "Класична любовна історія з гумором та соціальною сатирою",
                "description": "Найвідоміший роман Джейн Остін",
            },
        ],
    }

    def recommend(
        self,
        favorite_genres: List[str],
        read_books: List[str],
        count: int,
    ) -> List[Dict[str, Any]]:
        """Recommend books based on favorite genres."""
        recommendations: List[Dict[str, Any]] = []
        used_titles: set = set(read_books)

        for genre in favorite_genres:
            self._collect_genre_books(genre.lower(), recommendations, used_titles, count)

        return recommendations[:count]

    def _collect_genre_books(
        self,
        genre_lower: str,
        recommendations: List[Dict[str, Any]],
        used_titles: set,
        count: int,
    ) -> None:
        """Collect matching books for a single genre into recommendations."""
        for key, books in self.GENRE_BOOKS.items():
            if self._genre_key_matches(key, genre_lower):
                self._add_new_books(books, recommendations, used_titles, count)

    @staticmethod
    def _genre_key_matches(key: str, genre_lower: str) -> bool:
        """Check if a genre key matches the requested genre."""
        return key in genre_lower or genre_lower in key

    @staticmethod
    def _add_new_books(
        books: List[Dict[str, Any]],
        recommendations: List[Dict[str, Any]],
        used_titles: set,
        count: int,
    ) -> None:
        """Add books not yet used and within count limit."""
        for book in books:
            if len(recommendations) >= count:
                break
            if book["title"] not in used_titles:
                recommendations.append(book)
                used_titles.add(book["title"])

    def get_strategy_name(self) -> str:
        return "GenreBasedStrategy"


class PopularityBasedStrategy(RecommendationStrategy):
    """
    Strategy that recommends books based on overall popularity.
    Returns globally popular books regardless of genre.
    """

    POPULAR_BOOKS: List[Dict[str, Any]] = [
        {
            "title": "Сто років самотності",
            "author": "Габрієль Гарсія Маркес",
            "genre": "Магічний реалізм",
            "reason": "Нобелівська премія, одна з найважливіших книг XX ст.",
            "description": "Сага про сім поколінь родини Буендіа",
        },
        {
            "title": "1984",
            "author": "Джордж Орвелл",
            "genre": "Антиутопія",
            "reason": "Один з найбільш читаних романів у світі",
            "description": "Класична антиутопія про тоталітарне суспільство",
        },
        {
            "title": "Майстер і Маргарита",
            "author": "Михайло Булгаков",
            "genre": "Сатира",
            "reason": "Культовий роман, визнаний шедевром світової літератури",
            "description": "Фантастична сатира на радянське суспільство",
        },
        {
            "title": "Маленький принц",
            "author": "Антуан де Сент-Екзюпері",
            "genre": "Філософська притча",
            "reason": "Найбільш перекладена французька книга у світі",
            "description": "Філософська казка для дорослих та дітей",
        },
        {
            "title": "Kobzar",
            "author": "Тарас Шевченко",
            "genre": "Поезія",
            "reason": "Фундаментальна пам'ятка української літератури",
            "description": "Найважливіша поетична збірка в історії України",
        },
    ]

    def recommend(
        self,
        favorite_genres: List[str],
        read_books: List[str],
        count: int,
    ) -> List[Dict[str, Any]]:
        """Recommend globally popular books, excluding already read ones."""
        recommendations = []
        for book in self.POPULAR_BOOKS:
            if book["title"] not in read_books and len(recommendations) < count:
                recommendations.append(book)
        return recommendations

    def get_strategy_name(self) -> str:
        return "PopularityBasedStrategy"


class HybridRecommendationStrategy(RecommendationStrategy):
    """
    Strategy that combines genre-based and popularity-based approaches.
    First fills from genres, then fills remaining slots from popular books.
    Implements the composite Strategy pattern.
    """

    def __init__(self):
        self._genre_strategy = GenreBasedStrategy()
        self._popularity_strategy = PopularityBasedStrategy()

    def recommend(
        self,
        favorite_genres: List[str],
        read_books: List[str],
        count: int,
    ) -> List[Dict[str, Any]]:
        """Combine genre and popularity strategies."""
        # First, get genre-based recommendations
        genre_recs = self._genre_strategy.recommend(favorite_genres, read_books, count)
        used_titles = {r["title"] for r in genre_recs} | set(read_books)

        # Fill remaining slots with popular books
        remaining = count - len(genre_recs)
        if remaining > 0:
            popular_recs = self._popularity_strategy.recommend(
                favorite_genres,
                list(used_titles),
                remaining,
            )
            genre_recs.extend(popular_recs)

        return genre_recs[:count]

    def get_strategy_name(self) -> str:
        return "HybridRecommendationStrategy"


class RecommendationContext:
    """
    Context class that uses a RecommendationStrategy.
    Allows swapping strategies at runtime (Strategy pattern).
    """

    def __init__(self, strategy: RecommendationStrategy = None):
        self._strategy = strategy or HybridRecommendationStrategy()

    def set_strategy(self, strategy: RecommendationStrategy) -> None:
        """Change the recommendation strategy at runtime."""
        self._strategy = strategy

    def get_strategy(self) -> RecommendationStrategy:
        """Return the current strategy."""
        return self._strategy

    def execute(
        self,
        favorite_genres: List[str],
        read_books: List[str],
        count: int = 5,
    ) -> List[Dict[str, Any]]:
        """Execute the current recommendation strategy."""
        return self._strategy.recommend(favorite_genres, read_books, count)

    def get_strategy_name(self) -> str:
        """Return the name of the current strategy."""
        return self._strategy.get_strategy_name()
