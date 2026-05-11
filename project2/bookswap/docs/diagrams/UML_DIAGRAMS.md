# UML Діаграми — BookSwap

Скопіюйте код у [mermaid.live](https://mermaid.live) для перегляду.

---

## 1. Діаграма варіантів використання

```mermaid
flowchart TD
    Reader([Читач])

    Reader --> UC1[Реєстрація / Вхід]
    Reader --> UC2[Перегляд каталогу]
    Reader --> UC3[Пошук книг]
    Reader --> UC4[Переглянути деталі книги]
    Reader --> UC5[Додати книгу]
    Reader --> UC6[Написати рецензію]
    Reader --> UC7[Поставити рейтинг]
    Reader --> UC8[Додати до wishlist]
    Reader --> UC9[Запропонувати обмін]
    Reader --> UC10[Прийняти / відхилити обмін]
    Reader --> UC11[Чат для обміну]
    Reader --> UC12[AI-рекомендації]
    Reader --> UC13[Переглянути профіль]
    Reader --> UC14[Редагувати профіль]

    UC9 -->|requires| UC1
    UC6 -->|requires| UC1
    UC8 -->|requires| UC1
    UC10 -->|requires| UC1
    UC11 -->|requires| UC9
    UC13 -->|requires| UC1
    UC14 -->|requires| UC1
```

**Опис:**
- **Читач** - основний актор системи
- **UC1**: Реєстрація нового користувача або вхід до системи
- **UC2**: Перегляд повного каталогу книг з фільтрацією
- **UC3**: Пошук книг за назвою, автором, жанром
- **UC4**: Детальний перегляд інформації про книгу
- **UC5**: Додавання власної книги до каталогу
- **UC6**: Написання текстової рецензії на книгу
- **UC7**: Оцінка книги за шкалою 1-5
- **UC8**: Додавання книги до особистого списку бажань
- **UC9**: Створення запиту на обмін книгами
- **UC10**: Прийняття або відхилення пропозиції обміну
- **UC11**: Переговори через чат щодо деталей обміну
- **UC12**: Отримання персоналізованих рекомендацій від AI
- **UC13**: Перегляд власного профілю та статистики
- **UC14**: Редагування особистої інформації профілю

---

## 2. Діаграма класів

```mermaid
classDiagram
    class User {
        +int id
        +str email
        +str username
        +str hashed_password
        +str full_name
        +str bio
        +str city
        +str avatar_url
        +bool is_active
        +datetime created_at
        +datetime updated_at
        +List~Book~ books
        +List~Review~ reviews
        +List~WishlistItem~ wishlist_items
        +List~Exchange~ sent_exchanges
        +List~Exchange~ received_exchanges
        +List~Message~ sent_messages
        +List~Message~ received_messages
        +List~Friendship~ friendships
    }

    class Book {
        +int id
        +str title
        +str author
        +str isbn
        +str description
        +str genre
        +int year_published
        +int pages
        +str language
        +str cover_url
        +int owner_id
        +bool is_available
        +datetime created_at
        +datetime updated_at
        +List~Review~ reviews
        +List~Exchange~ exchanges_as_offered
        +List~Exchange~ exchanges_as_requested
        +List~WishlistItem~ wishlist_items
    }

    class Review {
        +int id
        +int book_id
        +int user_id
        +int rating
        +str title
        +str content
        +bool is_spoiler
        +datetime created_at
        +datetime updated_at
    }

    class Exchange {
        +int id
        +int requester_id
        +int requested_user_id
        +int offered_book_id
        +int requested_book_id
        +str status
        +str message
        +datetime created_at
        +datetime updated_at
        +List~Message~ messages
    }

    class WishlistItem {
        +int id
        +int user_id
        +int book_id
        +str priority
        +str notes
        +datetime created_at
    }

    class Message {
        +int id
        +int exchange_id
        +int sender_id
        +int receiver_id
        +str content
        +bool is_read
        +datetime created_at
    }

    class Friendship {
        +int id
        +int user_id
        +int friend_id
        +str status
        +datetime created_at
    }

    class Notification {
        +int id
        +int user_id
        +str type
        +str title
        +str content
        +bool is_read
        +datetime created_at
    }

    User "1" -- "N" Book : owns
    User "1" -- "N" Review : writes
    User "1" -- "N" WishlistItem : has
    User "1" -- "N" Exchange : requests
    User "1" -- "N" Exchange : receives
    User "1" -- "N" Message : sends
    User "1" -- "N" Message : receives
    User "1" -- "N" Friendship : participates
    User "1" -- "N" Notification : receives
    Book "1" -- "N" Review : has
    Book "1" -- "N" Exchange : offered_in
    Book "1" -- "N" Exchange : requested_in
    Book "1" -- "N" WishlistItem : in
    Exchange "1" -- "N" Message : contains
```

**Опис основних класів:**

- **User**: Користувач системи з особистою інформацією та статистикою
- **Book**: Книга з детальною інформацією та статусом доступності
- **Review**: Рецензія користувача на книгу з рейтингом
- **Exchange**: Запит на обмін книгами між двома користувачами
- **WishlistItem**: Елемент особистого списку бажань користувача
- **Message**: Повідомлення в чаті між користувачами
- **Friendship**: Дружні стосунки між користувачами
- **Notification**: Системні сповіщення для користувачів

---

## 3. Діаграма компонентів

```mermaid
graph TB
    subgraph Frontend["Frontend (React)"]
        Pages["Сторінки\n(HomePage, CatalogPage, ProfilePage...)"]
        Components["Компоненти\n(BookCard, ChatWindow, Modal...)"]
        Store["Zustand Store\n(authStore, bookStore...)"]
        API["API клієнт\n(Axios + React Query)"]
    end

    subgraph Backend["Backend (FastAPI)"]
        Routes["API Роути\n(auth, books, exchanges...)"]
        Services["Сервіси\n(AuthService, BookService...)"]
        Repositories["Репозиторії\n(UserRepository, BookRepository...)"]
        Models["SQLAlchemy Моделі\n(User, Book, Exchange...)"]
    end

    subgraph Database["База даних"]
        DB[(PostgreSQL)]
    end

    subgraph External["Зовнішні сервіси"]
        Claude[Anthropic Claude API]
        Email[Email сервіс]
    end

    Pages --> Components
    Components --> Store
    Components --> API
    API <-->|HTTP/WebSocket| Routes
    Routes --> Services
    Services --> Repositories
    Repositories --> Models
    Models <--> DB
    Services --> Claude
    Services --> Email
```

**Опис компонентів:**

- **Frontend**: React додаток з компонентною архітектурою
- **Pages**: Сторінки рівня застосунку
- **Components**: Повторно використовувані UI компоненти
- **Store**: Управління станом через Zustand
- **API**: Клієнт для взаємодії з backend

- **Backend**: FastAPI сервер з багатошаровою архітектурою
- **Routes**: API ендпоінти та роутинг
- **Services**: Бізнес-логіка та сервісний шар
- **Repositories**: Шар доступу до даних
- **Models**: ORM моделі бази даних

---

## 4. Діаграма послідовності - Процес обміну книгами

```mermaid
sequenceDiagram
    actor Alice as Аліса
    actor Bob as Боб
    participant FE as Frontend
    participant API as FastAPI
    participant DB as База даних
    participant Email as Email сервіс

    Alice->>FE: Натискає "Запропонувати обмін"
    FE->>API: POST /api/exchanges {offered_book_id, requested_book_id}
    API->>DB: Перевіряє книги та власників
    DB-->>API: Повертає дані книг
    API->>API: Валідує можливість обміну
    API->>DB: Створює запис обміну (status: pending)
    DB-->>API: Збережено успішно
    API->>Email: Надсилає сповіщення Бобу
    API-->>FE: Повертає 201 Created
    FE-->>Alice: Показує успішне створення

    Bob->>FE: Відкриває сповіщення
    FE->>API: GET /api/exchanges/{id}
    API->>DB: Отримує деталі обміну
    DB-->>API: Повертає дані обміну
    API-->>FE: Деталі обміну
    FE-->>Bob: Показує пропозицію обміну

    Bob->>FE: Натискає "Прийняти"
    FE->>API: PATCH /api/exchanges/{id} {status: "accepted"}
    API->>DB: Оновлює статус обміну
    API->>DB: Оновлює доступність книг
    DB-->>API: Оновлено успішно
    API->>Email: Надсилає підтвердження Алісі
    API-->>FE: Повертає 200 OK
    FE-->>Bob: Показує прийняття обміну

    Alice->>FE: Отримує сповіщення
    FE->>API: GET /api/exchanges/{id}
    API->>DB: Отримує оновлені деталі
    DB-->>API: Статус: accepted
    API-->>FE: Деталі обміну
    FE-->>Alice: Показує прийнятий обмін
```

**Опис процесу:**
1. Аліса створює запит на обмін
2. Система перевіряє доступність книг
3. Боб отримує сповіщення про пропозицію
4. Боб приймає або відхиляє обмін
5. Система оновлює статус та доступність книг
6. Обидва користувачі отримують підтвердження

---

## 5. Діаграма станів - Статус обміну

```mermaid
stateDiagram-v2
    [*] --> Створено: Користувач створює запит
    Створено --> Очікує: Запит відправлено іншому користувачу
    Очікує --> Прийнято: Інший користувач приймає обмін
    Очікує --> Відхилено: Інший користувач відхиляє обмін
    Очікує --> Скасовано: Запитувач скасовує обмін
    Прийнято --> Завершено: Обмін успішно завершено
    Прийнято --> Скасовано: Один з користувачів скасовує
    Відхилено --> [*]
    Скасовано --> [*]
    Завершено --> [*]
```

**Опис станів:**
- **Створено**: Запит обміну ініційовано
- **Очікує**: Чекає на відповідь від іншого користувача
- **Прийнято**: Обмін прийнято, очікує на завершення
- **Відхилено**: Обмін відхилено іншим користувачем
- **Скасовано**: Обмін скасовано одним з учасників
- **Завершено**: Обмін успішно завершено

---

## 6. Діаграма пакетів

```mermaid
graph TB
    subgraph Frontend["Frontend Пакет"]
        Pages["pages/"]
        Components["components/"]
        Services["services/"]
        Store["store/"]
        Utils["utils/"]
    end

    subgraph Backend["Backend Пакет"]
        API["api/"]
        Services["services/"]
        Repositories["repositories/"]
        Models["models/"]
        Core["core/"]
        Schemas["schemas/"]
    end

    subgraph Database["База даних"]
        Users["users"]
        Books["books"]
        Reviews["reviews"]
        Exchanges["exchanges"]
        Messages["messages"]
    end

    Frontend --> Backend
    Backend --> Database
```

---

## 7. Діаграма розгортання

```mermaid
graph TB
    subgraph "Production Environment"
        LB["Load Balancer"]
        
        subgraph "Frontend Servers"
            FE1["Frontend 1"]
            FE2["Frontend 2"]
        end
        
        subgraph "Backend Servers"
            BE1["Backend 1"]
            BE2["Backend 2"]
            BE3["Backend 3"]
        end
        
        subgraph "Database Cluster"
            DB1["Primary DB"]
            DB2["Replica 1"]
            DB3["Replica 2"]
        end
        
        subgraph "External Services"
            Claude["Claude API"]
            Email["Email Service"]
        end
    end

    LB --> FE1
    LB --> FE2
    FE1 --> BE1
    FE1 --> BE2
    FE2 --> BE2
    FE2 --> BE3
    BE1 --> DB1
    BE2 --> DB1
    BE3 --> DB1
    DB1 --> DB2
    DB1 --> DB3
    BE1 --> Claude
    BE2 --> Claude
    BE3 --> Claude
    BE1 --> Email
    BE2 --> Email
    BE3 --> Email
```

**Опис розгортання:**
- **Load Balancer**: Розподіл навантаження між frontend серверами
- **Frontend Servers**: Статичні файли React додатку
- **Backend Servers**: FastAPI сервери з горизонтальним масштабуванням
- **Database Cluster**: Primary-replica конфігурація для високої доступності
- **External Services**: Зовнішні API для AI та email функціональності
