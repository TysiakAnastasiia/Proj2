# Документація архітектури BookSwap

BookSwap використовує **багатошарову архітектуру** з **in-memory зберіганням** для розробки та тестування. Система розроблена для легкої тестованості та підтримки з дотриманням принципів SOLID.

## АРХІТЕКТУРНІ ШАРИ

### 1. Шар домену (Моделі)

```
app/models/
├── __init__.py          # Всі доменні моделі
├── user.py             # Сутність Користувача
├── book.py             # Сутність Книги
├── review.py           # Сутність Рецензії
├── exchange.py         # Сутність Обміну
├── wishlist.py         # Сутність Списку бажань
└── message.py          # Сутність Повідомлення
```

**Характеристики:**

- Чисті Python класи з бізнес-логікою
- Відсутність зовнішніх залежностей
- Реалізація доменних правил та валідації
- Використання SQLAlchemy ORM для мапінгу бази даних

### 2. Шар репозиторіїв (Доступ до даних)

```
app/repositories/
├── __init__.py          # Інтерфейси репозиторіїв
├── base.py             # Базовий інтерфейс репозиторію
├── user.py             # Репозиторій користувачів
├── book.py             # Репозиторій книг
├── review.py           # Репозиторій рецензій
├── exchange.py         # Репозиторій обмінів
└── wishlist.py         # Репозиторій списків бажань
```

**Реалізація патернів:**

- Абстрактні базові класи для всіх репозиторіїв
- In-memory реалізації для тестування
- Бази даних реалізації для продакшену
- Впровадження залежностей через фабричний патерн

### 3. Шар сервісів (Бізнес-логіка)

```
app/services/
├── __init__.py          # Інтерфейси сервісів
├── auth.py             # Сервіс автентифікації
├── user.py             # Сервіс управління користувачами
├── book.py             # Сервіс книг
├── review.py           # Сервіс рецензій
├── exchange.py         # Сервіс обмінів
└── recommendation.py   # Сервіс AI-рекомендацій
```

**Відповідальності:**

- Реалізація бізнес-правил та робочих процесів
- Координація між репозиторіями
- Обробка складних операцій
- Надання меж транзакцій

### 4. API шар (Презентація)

```
app/api/
├── __init__.py          # Налаштування FastAPI роутера
├── routes/
│   ├── auth.py         # Ендпоінти автентифікації
│   ├── users.py        # Ендпоінти управління користувачами
│   ├── books.py        # Ендпоінти книг
│   ├── reviews.py      # Ендпоінти рецензій
│   └── exchanges.py    # Ендпоінти обмінів
└── dependencies.py     # Залежності FastAPI
```

**Функціональність:**

- RESTful API дизайн
- OpenAPI документація
- Валідація запитів/відповідей
- Обробка помилок та статус-кодів

### 5. Основний шар (Інфраструктура)

```
app/core/
├── config.py           # Управління конфігурацією
├── security.py         # Утиліти безпеки
├── singleton.py        # Патерн Singleton
├── factory.py          # Патерн Factory
├── observer.py         # Патерн Observer
└── dependencies.py     # Впровадження залежностей
```

## ПАТЕРНИ ПРОЄКТУВАННЯ

### 1. Патерн Singleton

**Використання:** Сервіс конфігурації, сервіс логування

```python
class ConfigurationService(metaclass=SingletonMeta):
    def __init__(self):
        self.settings = self.load_settings()
```

### 2. Патерн Factory

**Використання:** Створення репозиторіїв, інстанціювання сервісів

```python
class RepositoryFactory:
    @staticmethod
    def create_user_repository(db_session: AsyncSession) -> UserRepository:
        return UserRepository(db_session)
```

### 3. Патерн Observer

**Використання:** Система подій для сповіщень

```python
class EventManager:
    def notify(self, event: Event):
        for observer in self.observers:
            observer.update(event)
```

### 4. Патерн Repository

**Використання:** Абстракція доступу до даних

```python
class UserRepository(BaseRepository[User]):
    async def get_by_email(self, email: str) -> Optional[User]:
        # Реалізація
```

### 5. Патерн Strategy

**Використання:** Алгоритми рекомендацій книг

```python
class RecommendationStrategy(ABC):
    @abstractmethod
    def recommend(self, user: User) -> List[Book]:
        pass
```

## IN-MEMORY АРХІТЕКТУРА

### Режим розробки

- Використовує Python словники та списки для зберігання
- Відсутність зовнішніх залежностей бази даних
- Швидкий старт та тестування
- Збереження стану через сесію

### Конфігурація

```python
# Перемикання на основі оточення
if os.getenv("USE_IN_MEMORY_STORAGE", "true").lower() == "true":
    storage_type = "in_memory"
else:
    storage_type = "database"
```

### Реалізація репозиторію

```python
class InMemoryUserRepository(BaseRepository[User]):
    def __init__(self):
        self._users: Dict[int, User] = {}
        self._next_id = 1

    async def create(self, user_data: dict) -> User:
        user = User(id=self._next_id, **user_data)
        self._users[self._next_id] = user
        self._next_id += 1
        return user
```

## ВПРОВАДЖЕННЯ ЗАЛЕЖНОСТЕЙ

### Контейнер сервісів

```python
class ServiceContainer:
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}

    def register(self, name: str, factory: Callable):
        self._factories[name] = factory

    def get(self, name: str) -> Any:
        if name not in self._services:
            self._services[name] = self._factories[name]()
        return self._services[name]
```

### Інтеграція з FastAPI

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int, user_service: UserService = Depends(get_user_service)):
    return await user_service.get_user(user_id)
```

## СИСТЕМА ПОДІЙ

### Типи подій

- USER_REGISTERED
- BOOK_CREATED
- EXCHANGE_REQUESTED
- EXCHANGE_ACCEPTED
- EXCHANGE_COMPLETED
- MESSAGE_SENT
- FRIEND_ADDED
- REVIEW_CREATED

### Реалізація Observer

```python
class EmailObserver(Observer):
    def update(self, event: Event):
        if event.type == EventType.EXCHANGE_ACCEPTED:
            self.send_exchange_notification(event.data)
```

## АРХІТЕКТУРА БЕЗПЕКИ

### Автентифікація

- JWT токени з терміном дії
- Механізм оновлення токенів
- Рольова система доступу
- Валідація вхідних даних

### Авторизація

- Ресурсні дозволи
- Захист API ендпоінтів
- Валідація та санітизація вводу

## ВИМОГИ ДО ПРОДУКТИВНОСТІ

### Асинхронні операції

- Всі I/O операції є асинхронними
- Пулінг з'єднень з базою даних
- Конкурентна обробка запитів
- Кешування часто доступних даних

### Стратегія кешування

- In-memory кеш для часто доступних даних
- Інвалідація кешу при зміні даних
- TTL-базована термінологія кешування

### Оптимізація бази даних

- Правильна стратегія індексації
- Оптимізація запитів
- Пакетні операції для великих обсягів даних

## ТЕСТУВАННЯ АРХІТЕКТУРИ

### Unit тестування

- Ізольоване тестування компонентів
- Мокування зовнішніх залежностей
- Швидке виконання з in-memory зберіганням

### Інтеграційне тестування

- Тестування API ендпоінтів
- Тестування інтеграції з базою даних
- Тестування сквозних робочих процесів

### Управління тестовими даними

- Фабричний патерн для тестових даних
- Автоматичне очищення між тестами
- Генерація реалістичних тестових даних

## АРХІТЕКТУРА РОЗГОРТАННЯ

### Стратегія контейнеризації

- Багатоетапні Docker збірки
- Окремі контейнери для backend та frontend
- Docker Compose для локальної розробки

### Конфігурація оточення

- Роздільні конфігурації для dev, test, prod
- Використання змінних оточення для всіх налаштувань
- Ніколи не зберігати секрети в репозиторії
- Надання .env.example файлів

### Масштабування

- Stateless API дизайн
- Підтримка горизонтального масштабування
- Сумісність з балансувальниками навантаження

## МОНИТОРИНГ ТА ЛОГУВАННЯ

### Стратегія логування

- Структуроване логування з контекстом
- Різні рівні логування для різних оточень
- Централізована агрегація логів

### Перевірки стану

- Перевірка підключення до бази даних
- Перевірка залежностей зовнішніх сервісів
- Перевірка готовності застосунку

## МАЙБУТНІ РОШИРЕННЯ

### Готовність до мікросервісів

- Чітко визначені межі сервісів
- Встановлені API контракти
- Готовність до event-driven комунікації

### Плагінна архітектура

- Патерн стратегії для розширюваності
- Механізм відкриття плагінів
- Перемикання функціональності через конфігурацію
