# Стратегія тестування BookSwap

## ОГЛЯД

Цей документ визначає комплексну стратегію тестування для проєкту BookSwap, що забезпечує високу якість коду, надійність та зручність супроводу.

## ПІРАМІДА ТЕСТУВАННЯ

### 1. Юніт-тести (Модульні) (70%)

- **Мета**: Тестування окремих функцій та методів в ізоляції
- **Ціль**: Швидке виконання, високе покриття, валідація бізнес-логіки
- **Інструменти**: `pytest`, `unittest.mock`, `pytest-asyncio`

### 2. Інтеграційні тести

- **Мета**: Тестування взаємодії між компонентами
- **Ціль**: API-ендпоінти, операції з базою даних, інтеграція сервісів
- **Інструменти**: `pytest`, `FastAPI TestClient`, тестова БД

### 3. End-to-End (E2E) тести

- **Мета**: Тестування повних користувацьких сценаріїв
- **Ціль**: Критичні шляхи користувача, системна інтеграція
- **Інструменти**: `Playwright`, `Selenium` (за потреби)

## ВИМОГИ ДО ПОКРИТТЯ

### Мінімальні цілі покриття

- **Загальне покриття**: мінімум 70%
- **Критична бізнес-логіка**: мінімум 90%
- **API Ендпоінти**: мінімум 80%
- **Рівень репозиторіїв**: мінімум 85%

### Інструменти вимірювання

```bash
# Покриття бекенду
pytest --cov=app --cov-report=html --cov-report=xml --cov-report=term-missing

# Покриття фронтенду
npm run test -- --coverage
```

### Звіти покриття

- **HTML звіти**: Генеруються автоматично в `htmlcov/`
- **XML звіти**: Сумісні з SonarQube в `coverage.xml`
- **Термінальні звіти**: Швидкий зворотний зв'язок під час розробки

## СТРУКТУРА ТЕСТІВ

### Директорна структура

```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_repositories.py
│   ├── test_services.py
│   ├── test_patterns.py
│   └── test_core_modules.py
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_database_integration.py
│   └── test_service_integration.py
├── fixtures/
│   ├── user_fixtures.py
│   ├── book_fixtures.py
│   └── exchange_fixtures.py
└── conftest.py
```

### Конвенції іменування тестів

- **Юніт-тести**: `test_[метод]_[сценарій]_[очікуваний результат]`
- **Інтеграційні тести**: `test_[функціонал]_[робочий процес]_[очікуваний результат]`
- **Тести крайніх випадків**: `test_[метод]_крайній_випадок_[умова]`

## ЮНІТ-ТЕСТУВАННЯ

### Структура тесту

```python
class TestUserService:
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.mock_repo = AsyncMock()
        self.service = UserService(self.mock_repo)

    async def test_create_user_success(self):
        """Тест успішного створення користувача"""
        # Arrange (Підготовка)
        user_data = {"email": "test@example.com", "username": "test"}
        expected_user = User(id=1, **user_data)
        self.mock_repo.create.return_value = expected_user

        # Act (Дія)
        result = await self.service.create_user(user_data)

        # Assert (Перевірка)
        assert result.email == "test@example.com"
        self.mock_repo.create.assert_called_once_with(user_data)
```

### Категорії тестів

#### 1. Тести моделей

- **Розташування**: `tests/unit/test_models.py`
- **Фокус**: Валідація даних, відносини, рядкове представлення
- **Приклади**:
  ```python
  def test_user_email_validation():
      with pytest.raises(ValidationError):
          User(email="invalid-email")
  ```

#### 2. Тести репозиторіїв

- **Розташування**: `tests/unit/test_repositories.py`
- **Фокус**: Патерни доступу до даних, CRUD операції
- **Приклади**:
  ```python
  async def test_repository_create_user():
      repo = InMemoryUserRepository()
      user = await repo.create({"email": "test@example.com"})
      assert user.email == "test@example.com"
  ```

#### 3. Тести сервісів

- **Розташування**: `tests/unit/test_services.py`
- **Фокус**: Бізнес-логіка, оркестрація робочих процесів
- **Приклади**:
  ```python
  async def test_service_user_registration():
      service = UserService(mock_repo)
      user = await service.register_user(valid_data)
      assert user.is_active is True
  ```

#### 4. Тести патернів

- **Розташування**: `tests/unit/test_patterns.py`
- **Фокус**: Реалізація патернів проєктування
- **Приклади**:
  ```python
  def test_singleton_pattern():
      instance1 = ConfigurationService()
      instance2 = ConfigurationService()
      assert instance1 is instance2
  ```

## ІНТЕГРАЦІЙНЕ ТЕСТУВАННЯ

### Тестування API ендпоінтів

```python
async def test_create_user_api():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/users/", json=user_data)
        assert response.status_code == 201
        assert response.json()["email"] == user_data["email"]
```

### Тестування інтеграції з базою даних

```python
async def test_user_repository_with_database():
    async with test_db_session() as session:
        repo = UserRepository(session)
        user = await repo.create(test_user_data)
        retrieved = await repo.get_by_id(user.id)
        assert retrieved.email == user.email
```

### Тестування інтеграції сервісів

```python
async def test_exchange_workflow():
    async with test_container() as container:
        exchange_service = container.get(ExchangeService)
        result = await exchange_service.create_exchange(request_data)
        assert result.status == ExchangeStatus.PENDING
```

## УПРАВЛІННЯ ТЕСТОВИМИ ДАНИМИ

### Фабричний патерн для тестових даних

```python
class UserFactory:
    @staticmethod
    def create_user(**overrides):
        defaults = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "is_active": True
        }
        defaults.update(overrides)
        return User(**defaults)
```

### Фікстури для спільного налаштування

```python
@pytest.fixture
async def test_db_session():
    async with create_test_engine() as engine:
        async with AsyncSession(engine) as session:
            yield session

@pytest.fixture
def user_service(test_db_session):
    return UserService(UserRepository(test_db_session))
```

## МОКУВАННЯ

### Коли мокувати

- Зовнішні залежності (API, бази даних)
- Операції, що залежать від часу
- Операції з файловою системою
- Мережеві виклики

### Приклади мокування

```python
# Мокування репозиторію
mock_repo = AsyncMock()
mock_repo.get_by_email.return_value = None

# Мокування сервісу
mock_email_service = Mock()
mock_email_service.send_welcome_email.return_value = True

# Мокування часу
with patch('datetime.datetime.utcnow') as mock_time:
    mock_time.return_value = datetime(2023, 1, 1)
```

## ТЕСТУВАННЯ КРАЙНІХ ВИПАДКІВ

### Граничні умови

```python
@pytest.mark.parametrize("input_value,expected", [
    (0, "invalid"),
    (1, "valid"),
    (100, "valid"),
    (101, "invalid"),
])
def test_age_validation(input_value, expected):
    result = validate_age(input_value)
    assert result == expected
```

### Сценарії помилок

```python
async def test_duplicate_email_error():
    mock_repo.get_by_email.return_value = User(email="existing@example.com")

    with pytest.raises(DuplicateEmailError):
        await user_service.create_user({"email": "existing@example.com"})
```

### Тестування продуктивності

```python
async def test_bulk_user_creation_performance():
    start_time = time.time()
    await user_service.create_bulk_users(test_users)
    duration = time.time() - start_time

    assert duration < 1.0  # Повинно завершитися за 1 секунду
```

## ОРГАНІЗАЦІЯ ТЕСТІВ

### Директорна структура

```
tests/
├── unit/           # Ізольовані тести компонентів
├── integration/   # Тести API та сервісної інтеграції
├── fixtures/      # Тестові дані та фікстури
└── conftest.py    # Спільні налаштування pytest
```

### Конвенції іменування

- **Юніт-тести**: `test_[метод]_[сценарій]_[очікуваний результат]`
- **Інтеграційні тести**: `test_[функціонал]_[робочий процес]_[очікуваний результат]`
- **Тести крайніх випадків**: `test_[метод]_крайній_випадок_[умова]`

## НЕПЕРЕРИВНА ІНТЕГРАЦІЯ (CI/CD)

### Пайплайн тестування CI/CD

```yaml
- name: Run unit tests
  run: pytest tests/unit/ -v --cov=app --cov-report=xml

- name: Run integration tests
  run: pytest tests/integration/ -v

- name: Upload coverage
  uses: codecov/codecov-action@v4
  with:
    file: coverage.xml
```

### Quality Gates

- Всі тести повинні проходити (100% успішності)
- Покриття має бути ≥ 70%
- Нові code smells не дозволені
- Тести продуктивності повинні бути в межах порогів

## ТЕСТОВІ ОТОЧЕННЯ

### Оточення розробки

- In-memory зберігання для швидкого виконання
- Мокування зовнішніх залежностей
- Локальна база даних для інтеграційних тестів

### Оточення тестування

- База даних SQLite для персистентності тестування
- Реальні зовнішні сервіси (staging)
- Бенчмаркінг продуктивності

### Оточення staging

- Production-like налаштування
- Повна інтеграція тестування
- Тестування навантаження

## ТЕСТУВАННЯ ФРОНТЕНДУ

### Тестування компонентів

```javascript
import { render, screen } from "@testing-library/react";
import { BookCard } from "./BookCard";

test("renders book information correctly", () => {
  const book = { title: "Test Book", author: "Test Author" };
  render(<BookCard book={book} />);

  expect(screen.getByText("Test Book")).toBeInTheDocument();
  expect(screen.getByText("Test Author")).toBeInTheDocument();
});
```

### Інтеграційне тестування

```javascript
import { renderHook, act } from "@testing-library/react-hooks";
import { useBookExchange } from "./useBookExchange";

test("creates exchange successfully", async () => {
  const { result } = renderHook(() => useBookExchange());

  await act(async () => {
    await result.current.createExchange(exchangeData);
  });

  expect(result.current.exchanges).toHaveLength(1);
});
```

## ЗВІТИ ТЕСТУВАННЯ

### HTML звіти покриття

- Генеруються автоматично в директорії `htmlcov/`
- Інтерактивна візуалізація непокритих рядків
- Аналіз покриття гілок
- Історичні тренди покриття

### XML звіти для CI/CD

- Сумісні з SonarQube
- Витяг метрик покриття
- Агрегація результатів тестування
- Інтеграція з Quality Gate

### Підсумки тестових результатів

- Формат JUnit XML для звітів
- Аналіз часу виконання тестів
- Категоризація відмов
- Метрики продуктивності

## СТРАТЕГІЯ ПІДТРИМКИ

### Процес перевірки коду

- Перегляд коду включає перевірку тестів
- Аналіз покриття в pull requests
- Виявлення регресій продуктивності
- Моніторинг нестабільних тестів

### Оновлення тестів

- Оновлення тестів при зміні вимог
- Рефакторинг тестів для кращої підтримки
- Додавання тестів для нових функцій
- Видалення застарілих тестів

### Документація

- Документування складних тестових сценаріїв
- Підтримка документації тестових даних
- Оновлення рекомендацій з тестування
- Обмін найкращими практиками

## УСУНЕННЯ ПРОБЛЕМ

### Поширені проблеми

1. **Ізоляція тестів**: Переконайтеся, що тести не діляться станом
2. **Асинхронне тестування**: Використовуйте правильні async/await патерни
3. **Налаштування моків**: Перевіряйте налаштування та очікування моків
4. **Очищення даних**: Забезпечте правильне очищення тестових даних

### Стратегії налагодження

- Використовуйте детальний вивід pytest (`-vv`)
- Додавайте налагоджувальні принти в тестові методи
- Використовуйте точки зупинки в налагоджувачі для тестів
- Аналізуйте сліди виконання тестів

## НАЙКРАЩІ ПРАКТИКИ

### Написання тестів

- Пишіть тести перед реалізацією (TDD)
- Тримайте тести простими та сфокусованими
- Використовуйте описові імена тестів
- Тестуйте одну річ за тест

### Підтримка тестів

- Регулярний рефакторинг тестів
- Видалення дублікатів тестового коду
- Оновлення тестових даних
- Моніторинг часу виконання тестів

### Безперервне покращення

- Аналіз прогалин у покритті
- Виявлення нестабільних тестів
- Оптимізація продуктивності тестів
- Збір відгуків від розробників
