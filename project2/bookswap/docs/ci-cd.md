# CI/CD та Quality Gate для BookSwap

Цей документ описує реалізацію автоматизованої перевірки якості коду, генерацію звітів та збереження артефактів.

## Мета

Налаштувати конвеєр, який автоматично:

- виконує юніт та інтеграційні тести
- генерує звіти покриття коду (HTML + XML)
- завантажує звіти як артефакти
- передає результати до SonarQube / SonarCloud
- не дозволяє мерджити PR, якщо Quality Gate провалено

## Формат репозиторію

```
.github/
└── workflows/
    └── ci-pipeline.yml
backend/
└── htmlcov/
└── coverage.xml
└── junit.xml
docs/
└── ci-cd.md
└── coverage-report.md
```

## GitHub Actions

Файл `./github/workflows/ci-pipeline.yml` виконує:

1. Клон репозиторію
2. Налаштовує Python 3.14
3. Встановлює залежності з `backend/requirements.txt`
4. Запускає тести у `backend/tests/unit` та `backend/tests/integration`
5. Генерує звіти:
   - `backend/coverage.xml`
   - `backend/htmlcov/`
   - `backend/junit.xml`
6. Завантажує звіти як артефакти GitHub Actions
7. Виконує SonarCloud/SonarQube аналіз, якщо задано секрети

## Артефакти

Після успішної збірки артефакти зберігаються у GitHub Actions і доступні для завантаження:

- `backend/coverage.xml`
- `backend/htmlcov/`
- `backend/junit.xml`

## SonarQube / SonarCloud

Для інтеграції необхідно додати секрети у GitHub репозиторій:

- `SONAR_TOKEN`
- `SONAR_HOST_URL`
- `SONAR_PROJECT_KEY`
- `SONAR_ORGANIZATION` (за потреби для SonarCloud)

## Quality Gate

Пайплайн налаштований на перевірку якості через SonarQube / SonarCloud. Якщо Quality Gate провалено, PR в GitHub не можна буде злити.

## Рекомендації

- Налаштуйте `branch protection` для `main` / `master`
- Активуйте перевірки GitHub Actions
- Додайте бейджі в `README.md`
- Підтримуйте покриття тестів вище 70%
- Уникайте `Bugs & Vulnerabilities` та Code Smells рівня `C`+ в Sonar
