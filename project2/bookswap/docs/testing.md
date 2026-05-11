# Тестування BookSwap

## Мета

Забезпечити надійність бізнес-логіки та стабільність змін через високоякісні тести та звіти.

## Стратегія тестування

### Unit тести

- Локалізовані тести для сервісів, репозиторіїв, моделей та утиліт
- Використання `pytest` та `pytest-asyncio`
- Мокування зовнішніх залежностей через `AsyncMock`
- Ціль: критична логіка має покриття 90%+

### Integration тести

- Перевірка API-ендпоінтів та робочих процесів
- Тестування взаємодії між сервісами та репозиторіями
- Використання тестової конфігурації та in-memory/тестової БД

### Звіти

- HTML звіти в `backend/htmlcov/`
- XML звіти в `backend/coverage.xml`
- JUnit звіти в `backend/junit.xml`

## Запуск тестів

```bash
cd backend
pytest --maxfail=1 --disable-warnings --cov=app --cov-report=xml:coverage.xml --cov-report=html:htmlcov --junitxml=junit.xml tests/unit tests/integration
```

## Критерії якості

- Загальне покриття: мінімум 70%
- Тестування всіх гілок логіки у ключових сервісах
- 200+ тестів для охоплення edge case і стандартних сценаріїв
- HTML та XML звіти мають бути доступні як CI артефакти

## Структура тестів

```
backend/tests/
├── unit/
│   ├── test_core_modules.py
│   ├── test_models_comprehensive.py
│   ├── test_services_comprehensive.py
│   └── ...
└── integration/
    ├── test_simple_integration.py
    └── ...
```

## Рекомендації

- Створюйте `conftest.py` для загальних фікстур
- Пишіть тести першими для нових функцій
- Розділяйте юніт та інтеграційні тести
- Регулярно перевіряйте покриття під час розробки
