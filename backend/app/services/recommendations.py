import json
import urllib.request

from app.core.config import settings
from app.models import BookGenre

# Constants for duplicated genre names
FANTASY = "Фентезі"
DETECTIVE = "Детектив"
HISTORY = "Історія"
POETRY = "Поезія"
ROMANCE = "Роман"

GENRE_LABELS = {
    BookGenre.fiction: "Художня проза",
    BookGenre.non_fiction: "Нон-фікшн",
    BookGenre.fantasy: FANTASY,
    BookGenre.sci_fi: "Наукова фантастика",
    BookGenre.mystery: DETECTIVE,
    BookGenre.romance: "Романтика",
    BookGenre.thriller: "Трилер",
    BookGenre.horror: "Жахи",
    BookGenre.biography: "Біографія",
    BookGenre.history: HISTORY,
    BookGenre.science: "Наука",
    BookGenre.self_help: "Саморозвиток",
    BookGenre.children: "Дитяча",
    BookGenre.poetry: POETRY,
    BookGenre.other: "Інше",
}

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models"
    "/gemini-2.0-flash:generateContent?key={key}"
)


class RecommendationService:
    async def get_recommendations(
        self,
        favorite_genres: list[str],
        read_books: list[str],
        count: int = 3,
    ) -> list[dict]:
        prompt_data = self._build_prompt_data(favorite_genres, read_books, count)
        prompt = self._build_prompt(prompt_data, count)
        
        try:
            ai_response = await self._get_ai_recommendations(prompt)
            return self._parse_ai_response(ai_response)
        except Exception as e:
            print(f"AI recommendation error: {e}")
            return self._get_fallback_recommendations(favorite_genres, count)

    def _build_prompt_data(self, favorite_genres: list[str], read_books: list[str], count: int) -> dict:
        """Build data for the recommendation prompt."""
        return {
            "genres_str": ", ".join(favorite_genres) if favorite_genres else "різні жанри",
            "books_str": "; ".join(read_books[:10]) if read_books else "не вказано",
            "count": count
        }

    def _build_prompt(self, data: dict, count: int) -> str:
        """Build the AI prompt."""
        return f"""Ти — всесвітньо відомий книжковий експерт з величезною базою даних літератури. Порекомендуй {count} книг на основі вподобань користувача.

Улюблені жанри: {data['genres_str']}
Прочитані книги: {data['books_str']}

Рекомендації можуть включати:
- Класичні твори світової літератури
- Сучасні бестселери
- Українську та зарубіжну літературу
- Книги, перекладені українською або оригінальні
- Рідкісні та відомі шедеври

Відповідай ТІЛЬКИ валідним JSON масивом (без markdown, без зайвих пояснень):
[
  {{
    "title": "Назва книги українською (або оригінальна якщо немає перекладу)",
    "author": "Автор",
    "genre": "Жанр",
    "reason": "Чому ця книга ідеально підходить користувачу (2-3 речення)",
    "description": "Що робить цю книгу особливою (1 речення)"
  }}
]

Обирай книги з різних країн та епох, які точно зацікавлять та розширять світогляд."""

    def _get_ai_recommendations(self, prompt: str) -> str:
        """Get recommendations from AI service."""
        body = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 1000, "temperature": 0.7},
        }).encode()

        url = GEMINI_URL.format(key=settings.gemini_api_key)
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()

    def _parse_ai_response(self, raw: str) -> list[dict]:
        """Parse AI response and return recommendations."""
        cleaned = self._clean_ai_response(raw)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return []

    def _clean_ai_response(self, raw: str) -> str:
        """Clean AI response by removing markdown fences."""
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return raw.strip()

    def _get_genre_books(self) -> dict:
        """Get genre-based book pools for fallback recommendations."""
        return {
            "детектив": self._get_detective_books(),
            "поезія": self._get_poetry_books(),
            "фантастика": self._get_fantasy_books(),
            "романтика": self._get_romance_books(),
            "історія": self._get_history_books(),
        }

    def _get_detective_books(self) -> list[dict]:
        """Get detective book recommendations."""
        return [
            {
                "title": "Дівчина з татуюванням дракона",
                "author": "Стьюг Ларссон",
                "genre": DETECTIVE,
                "reason": "Сучасний шведський детектив з інтригою та несподіваними поворотами",
                "description": "Перша книга трилогії про Мікаель Блумквіст та Лісбет Саландер",
            },
            {
                "title": "Убивство у Східному експресі",
                "author": "Агата Крісті",
                "genre": DETECTIVE,
                "reason": "Класичний детектив від королеви жанру з Еркюлем Пуаро",
                "description": "Ідеальний приклад детективного роману з логічним розв'язанням",
            },
            {
                "title": "Шерлок Холмс",
                "author": "Артур Конан Дойл",
                "genre": DETECTIVE,
                "reason": "Незабутні пригоди найвідомішого детектива світу",
                "description": "Класика, яка сформувала жанр детективної літератури",
            },
        ]

    def _get_poetry_books(self) -> list[dict]:
        """Get poetry book recommendations."""
        return [
            {
                "title": "Кобзар",
                "author": "Тарас Шевченко",
                "genre": POETRY,
                "reason": "Фундаментальна збірка української поезії, що визначила національну ідентичність",
                "description": "Найважливіша поетична збірка в історії української літератури",
            },
            {
                "title": "Лірика",
                "author": "Пабло Неруда",
                "genre": POETRY,
                "reason": "Чуттєва лірика нобелівського лауреата про любов і природу",
                "description": "Вірші, які торкаються найглибших струн душі",
            },
            {
                "title": "Вірші",
                "author": "Ліна Костенко",
                "genre": POETRY,
                "reason": "Сучасна українська поезія з філософським підтекстом",
                "description": "Поезія, що поєднує традиції та сучасність",
            },
        ]

    def _get_fantasy_books(self) -> list[dict]:
        """Get fantasy/sci-fi book recommendations."""
        return [
            {
                "title": "Дюна",
                "author": "Френк Герберт",
                "genre": "Наукова фантастика",
                "reason": "Епічна космічна опера про політику, екологію та людську природу",
                "description": "Впливовий науково-фантастичний роман, що надихнув багато творів",
            },
            {
                "title": "Хранителі",
                "author": "Сергій Лук'яненко",
                "genre": FANTASY,
                "reason": "Сучасне українське фентезі про світ нічних людей",
                "description": "Унікальне поєднання міської фентезі та філософських роздумів",
            },
            {
                "title": "Метро 2033",
                "author": "Дмитро Глуховський",
                "genre": "Постапокаліпсис",
                "reason": "Постапокаліптичний світ московського метро від українського автора",
                "description": "Напружена атмосфера та глибокі роздуми про людяність",
            },
        ]

    def _get_romance_books(self) -> list[dict]:
        """Get romance book recommendations."""
        return [
            {
                "title": "Гордість і упередження",
                "author": "Джейн Остін",
                "genre": ROMANCE,
                "reason": "Класична історія кохання з британським гумором та соціальною сатирою",
                "description": "Чарівна романтична комедія звичаїв XIX століття",
            },
            {
                "title": "Тіні забутих предків",
                "author": "Михайло Коцюбинський",
                "genre": ROMANCE,
                "reason": "Лірична історія кохання на тлі карпатських пейзажів",
                "description": "Перлинка української літератури з поетичним стилем",
            },
            {
                "title": "Любов у часи холери",
                "author": "Габрієль Гарсія Маркес",
                "genre": ROMANCE,
                "reason": "Чарівна історія кохання, що витримує випробування часом",
                "description": "Магічний реалізм в інтерпретації теми вічного кохання",
            },
        ]

    def _get_history_books(self) -> list[dict]:
        """Get history book recommendations."""
        return [
            {
                "title": "Спадщина козацтва",
                "author": "В'ячеслав Липинський",
                "genre": HISTORY,
                "reason": "Фундаментальна праця про українську державність та ідентичність",
                "description": "Класичний аналіз української історії та політичної думки",
            },
            {
                "title": "Київська Русь",
                "author": "Михайло Грушевський",
                "genre": HISTORY,
                "reason": "Авторитетна історія України від заснування до XIV століття",
                "description": "Найповніша праця з ранньої історії України",
            },
            {
                "title": "Sapiens",
                "author": "Юваль Ной Харарі",
                "genre": "Нон-фікшн",
                "reason": "Захоплююча історія людства від появи Homo Sapiens до сьогодення",
                "description": "Популярна книга, що пояснює історію людства простою мовою",
            },
        ]

    def _get_default_books(self) -> list[dict]:
        """Get default book recommendations for any genre."""
        return [
            {
                "title": "Сто років самотності",
                "author": "Габрієль Гарсія Маркес",
                "genre": "Магічний реалізм",
                "reason": "Геніальний роман про історію Латинської Америки через долю сім'ї Буендіа",
                "description": "Шедевр світової літератури, що змінив уявлення про роман",
            },
            {
                "title": "1984",
                "author": "Джордж Орвелл",
                "genre": "Антиутопія",
                "reason": "Пророччий твір про тоталітаризм, який залишається актуальним досі",
                "description": "Класика, що змусить замислитися про свободу та суспільство",
            },
            {
                "title": "Маленький принц",
                "author": "Антуан де Сент-Екзюпері",
                "genre": "Філософська притча",
                "reason": "Чарівна історія про дружбу, любов і сенс життя, доступна всім вікам",
                "description": "Твір, який можна читати в будь-якому віці і знаходити новий сенс",
            },
            {
                "title": "Майстер і Маргарита",
                "author": "Михайло Булгаков",
                "genre": "Сатира",
                "reason": "Роман-міф про любов, добро та зло в радянській Москві",
                "description": "Найвідоміший роман Булгакова з багатошаровими символами",
            },
            {
                "title": "Аліса в Країні чудес",
                "author": "Льюїс Керрол",
                "genre": FANTASY,
                "reason": "Чарівна пригода, яка надихає мріяти та мислити креативно",
                "description": "Класична казка для дорослих та дітей з філософським підтекстом",
            },
        ]

    def _add_genre_books(self, recommendations: list[dict], used_titles: set, 
                        favorite_genres: list[str], genre_books: dict, count: int):
        """Add books from user's favorite genres to recommendations."""
        for genre in favorite_genres:
            matching_books = self._find_matching_books_for_genre(genre, genre_books)
            self._add_books_to_recommendations(matching_books, recommendations, used_titles, count)

    def _find_matching_books_for_genre(self, genre: str, genre_books: dict) -> list[dict]:
        """Find books that match the given genre."""
        genre_lower = genre.lower()
        matching_books = []
        
        for key, books in genre_books.items():
            if self._genre_matches(key, genre_lower):
                matching_books.extend(books)
        
        return matching_books

    def _genre_matches(self, genre_key: str, user_genre: str) -> bool:
        """Check if genre key matches user's genre."""
        return genre_key in user_genre or user_genre in genre_key

    def _add_books_to_recommendations(self, books: list[dict], recommendations: list[dict], 
                                   used_titles: set, count: int):
        """Add books to recommendations if they haven't been used and limit not reached."""
        for book in books:
            if self._should_add_book(book, used_titles, recommendations, count):
                recommendations.append(book)
                used_titles.add(book["title"])

    def _should_add_book(self, book: dict, used_titles: set, recommendations: list[dict], count: int) -> bool:
        """Check if book should be added to recommendations."""
        return book["title"] not in used_titles and len(recommendations) < count

    def _fill_with_defaults(self, recommendations: list[dict], used_titles: set, 
                          default_books: list[dict], count: int):
        """Fill remaining recommendation slots with default books."""
        for book in default_books:
            if book["title"] not in used_titles and len(recommendations) < count:
                recommendations.append(book)
                used_titles.add(book["title"])

    def _get_fallback_recommendations(
        self, favorite_genres: list[str], count: int = 3
    ) -> list[dict]:
        """Dynamic fallback recommendations based on user preferences"""
        genre_books = self._get_genre_books()
        default_books = self._get_default_books()
        
        recommendations = []
        used_titles = set()

        self._add_genre_books(recommendations, used_titles, favorite_genres, genre_books, count)
        self._fill_with_defaults(recommendations, used_titles, default_books, count)

        return recommendations[:count]
