# Діаграма класів BookSwap

## Основні доменні моделі

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
        +List~Notification~ notifications
        +register() User
        +authenticate() bool
        +update_profile() void
        +add_book(Book) void
        +create_exchange(User, Book) Exchange
        +write_review(Book, Review) void
        +add_to_wishlist(Book) void
        +send_message(Message) void
        +add_friend(User) Friendship
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
        +set_available(bool) void
        +add_review(Review) void
        +calculate_average_rating() float
        +is_owned_by(User) bool
        +can_be_exchanged() bool
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
        +validate_rating() bool
        +update_content() void
        +mark_as_spoiler() void
        +is_helpful() bool
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
        +accept() void
        +reject() void
        +cancel() void
        +complete() void
        +add_message(Message) void
        +can_be_accepted_by(User) bool
        +get_status_text() str
    }

    class WishlistItem {
        +int id
        +int user_id
        +int book_id
        +str priority
        +str notes
        +datetime created_at
        +update_priority(str) void
        +add_notes(str) void
        +is_high_priority() bool
        +get_priority_level() int
    }

    class Message {
        +int id
        +int exchange_id
        +int sender_id
        +int receiver_id
        +str content
        +bool is_read
        +datetime created_at
        +mark_as_read() void
        +reply(str) Message
        +is_from(User) bool
        +is_for(User) bool
    }

    class Friendship {
        +int id
        +int user_id
        +int friend_id
        +str status
        +datetime created_at
        +accept() void
        +reject() void
        +block() void
        +unblock() void
        +is_accepted() bool
        +is_blocked() bool
        +is_pending() bool
    }

    class Notification {
        +int id
        +int user_id
        +str type
        +str title
        +str content
        +bool is_read
        +datetime created_at
        +mark_as_read() void
        +send_email() void
        +get_type_text() str
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

## Сервісний шар

```mermaid
classDiagram
    class UserService {
        +UserRepository user_repo
        +EventManager event_manager
        +register_user(dict) User
        +authenticate_user(str, str) dict
        +get_user_by_id(int) User
        +update_user_profile(int, dict) User
        +search_users(str, int) List~User~
        +deactivate_user(int) bool
        +send_friend_request(int, int) Friendship
    }

    class BookService {
        +BookRepository book_repo
        +UserRepository user_repo
        +EventManager event_manager
        +create_book(int, dict) Book
        +get_book_by_id(int) Book
        +update_book(int, int, dict) Book
        +delete_book(int, int) bool
        +search_books(str, dict, int) List~Book~
        +get_user_books(int) List~Book~
        +recommend_books(int, List~str~) List~Book~
    }

    class ExchangeService {
        +ExchangeRepository exchange_repo
        +BookRepository book_repo
        +UserRepository user_repo
        +EventManager event_manager
        +create_exchange_request(int, int, int, int, str) Exchange
        +accept_exchange(int, int) Exchange
        +reject_exchange(int, int) Exchange
        +complete_exchange(int, int) Exchange
        +get_user_exchanges(int) List~Exchange~
        +cancel_exchange(int, int) bool
    }

    class ReviewService {
        +ReviewRepository review_repo
        +BookRepository book_repo
        +UserRepository user_repo
        +EventManager event_manager
        +create_review(int, int, dict) Review
        +get_book_reviews(int) List~Review~
        +update_review(int, int, dict) Review
        +delete_review(int, int) bool
        +get_user_reviews(int) List~Review~
    }

    class ChatService {
        +MessageRepository message_repo
        +UserRepository user_repo
        +EventManager event_manager
        +send_message(int, int, str) Message
        +get_conversation(int, int, int) List~Message~
        +mark_message_as_read(int, int) Message
        +get_unread_messages(int) List~Message~
        +delete_message(int, int) bool
    }

    class FriendshipService {
        +FriendshipRepository friendship_repo
        +UserRepository user_repo
        +EventManager event_manager
        +send_friend_request(int, int) Friendship
        +accept_friend_request(int, int) Friendship
        +reject_friend_request(int, int) Friendship
        +get_user_friends(int) List~User~
        +remove_friend(int, int) bool
        +block_user(int, int) Friendship
        +unblock_user(int, int) bool
    }

    class WishlistService {
        +WishlistRepository wishlist_repo
        +BookRepository book_repo
        +UserRepository user_repo
        +add_to_wishlist(int, int, str, str) WishlistItem
        +remove_from_wishlist(int, int) bool
        +get_user_wishlist(int) List~WishlistItem~
        +update_wishlist_item(int, int, dict) WishlistItem
        +get_priority_books(int) List~Book~
    }

    class AuthService {
        +UserRepository user_repo
        +EventManager event_manager
        +register_user(dict) User
        +login(dict) dict
        +get_current_user(int) User
        +refresh_token(str) dict
        +logout(int) bool
        +verify_token(str) dict
        +change_password(int, str, str) bool
    }
```

## Репозиторії

```mermaid
classDiagram
    class BaseRepository~T~ {
        <<abstract>>
        +AsyncSession session
        +create(dict) T
        +get_by_id(int) T
        +get_all(int) List~T~
        +update(int, dict) T
        +delete(int) bool
    }

    class UserRepository {
        +AsyncSession session
        +create(dict) User
        +get_by_id(int) User
        +get_by_email(str) User
        +get_by_username(str) User
        +get_all(int) List~User~
        +update(int, dict) User
        +delete(int) bool
        +search(str, int) List~User~
    }

    class BookRepository {
        +AsyncSession session
        +create(dict) Book
        +get_by_id(int) Book
        +get_by_owner_id(int) List~Book~
        +get_all(int) List~Book~
        +update(int, dict) Book
        +delete(int) bool
        +search(str, dict, int) List~Book~
    }

    class ExchangeRepository {
        +AsyncSession session
        +create(dict) Exchange
        +get_by_id(int) Exchange
        +get_by_user_id(int) List~Exchange~
        +get_active_exchange(int, int, int, int) Exchange
        +get_all(int) List~Exchange~
        +update(int, dict) Exchange
        +delete(int) bool
    }

    BaseRepository <|-- UserRepository
    BaseRepository <|-- BookRepository
    BaseRepository <|-- ExchangeRepository
    BaseRepository <|-- ReviewRepository
    BaseRepository <|-- MessageRepository
    BaseRepository <|-- WishlistRepository
    BaseRepository <|-- FriendshipRepository
```

## Основні патерни

```mermaid
classDiagram
    class SingletonMeta {
        -Dict~Type, Any~ _instances
        +call(cls, *args, **kwargs) Any
    }

    class ConfigurationService {
        <<singleton>>
        -dict settings
        +load_settings() dict
        +get_setting(str) Any
        +reload_settings() void
    }

    class EventManager {
        -List~Observer~ observers
        -List~Event~ event_history
        +attach(Observer) void
        +detach(Observer) void
        +notify(Event) void
        +get_history() List~Event~
    }

    class Observer {
        <<interface>>
        +update(Event) void
    }

    class LoggingObserver {
        +update(Event) void
        +log_event(Event) void
    }

    class EmailObserver {
        +update(Event) void
        +send_notification(Event) void
    }

    class RepositoryFactory {
        +create_user_repository(AsyncSession) UserRepository
        +create_book_repository(AsyncSession) BookRepository
        +create_exchange_repository(AsyncSession) ExchangeRepository
        +create_review_repository(AsyncSession) ReviewRepository
    }

    ConfigurationService --|> SingletonMeta
    EventManager --> Observer
    LoggingObserver --|> Observer
    EmailObserver --|> Observer
```

## API Шар

```mermaid
classDiagram
    class AuthController {
        +register_user(dict) Response
        +login(dict) Response
        +refresh_token(str) Response
        +logout() Response
        +get_current_user() Response
    }

    class UserController {
        +get_user_profile(int) Response
        +update_user_profile(int, dict) Response
        +search_users(str, int) Response
        +get_user_by_id(int) Response
        +deactivate_user(int) Response
    }

    class BookController {
        +create_book(dict) Response
        +get_books(dict) Response
        +get_book(int) Response
        +update_book(int, dict) Response
        +delete_book(int) Response
        +search_books(str, dict) Response
    }

    class ExchangeController {
        +create_exchange(dict) Response
        +get_exchanges() Response
        +accept_exchange(int) Response
        +reject_exchange(int) Response
        +complete_exchange(int) Response
        +cancel_exchange(int) Response
    }

    AuthController --> AuthService
    UserController --> UserService
    BookController --> BookService
    ExchangeController --> ExchangeService
```

## Відносини між класами

```mermaid
classDiagram
    class User {
        +int id
        +str email
        +str username
        +str hashed_password
        +str full_name
        +bool is_active
        +datetime created_at
    }

    class Book {
        +int id
        +str title
        +str author
        +str isbn
        +int owner_id
        +bool is_available
        +datetime created_at
    }

    class Exchange {
        +int id
        +int requester_id
        +int requested_user_id
        +int offered_book_id
        +int requested_book_id
        +str status
        +datetime created_at
    }

    class Review {
        +int id
        +int book_id
        +int user_id
        +int rating
        +str content
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

    User ||--o{ Book : owns
    User ||--o{ Review : writes
    User ||--o{ Exchange : requests
    User ||--o{ Exchange : receives
    User ||--o{ Message : sends
    User ||--o{ Message : receives
    Book ||--o{ Review : has
    Book ||--o{ Exchange : offered
    Book ||--o{ Exchange : requested
    Exchange ||--o{ Message : contains
```

**Опис відносин:**

- **User ↔ Book**: Один користувач може володіти багатьма книгами (одна книга належить одному користувачу)
- **User ↔ Review**: Один користувач може написати багато рецензій (одна рецензія написана одним користувачем)
- **User ↔ Exchange**: Один користувач може створювати багато запитів на обмін (один обмін ініційований одним користувачем)
- **Book ↔ Review**: Одна книга може мати багато рецензій (одна рецензія належить одній книзі)
- **Exchange ↔ Message**: Один обмін може містити багато повідомлень (одне повідомлення належить одному обміну)

## Методи та операції

### User методи
- `register()` - Реєстрація нового користувача
- `authenticate()` - Автентифікація користувача
- `update_profile()` - Оновлення профілю
- `add_book()` - Додавання книги до власності
- `create_exchange()` - Створення запиту на обмін

### Book методи
- `set_available()` - Встановлення статусу доступності
- `add_review()` - Додавання рецензії
- `calculate_average_rating()` - Розрахунок середнього рейтингу
- `can_be_exchanged()` - Перевірка можливості обміну

### Exchange методи
- `accept()` - Прийняття обміну
- `reject()` - Відхилення обміну
- `complete()` - Завершення обміну
- `cancel()` - Скасування обміну

### Review методи
- `validate_rating()` - Валідація рейтингу
- `update_content()` - Оновлення вмісту рецензії
- `mark_as_spoiler()` - Позначення як спойлер

### Message методи
- `mark_as_read()` - Позначення як прочитане
- `reply()` - Відповідь на повідомлення
- `is_from()` - Перевірка відправника

### Friendship методи
- `accept()` - Прийняття дружби
- `reject()` - Відхилення дружби
- `block()` - Блокування користувача
- `unblock()` - Розблокування користувача

## Валідація та обмеження

### User валідація
- Email: унікальний, валідний формат
- Username: унікальний, 3-50 символів
- Password: мінімум 8 символів
- Full name: необов'язкове, макс 100 символів

### Book валідація
- Title: обов'язкове, макс 200 символів
- Author: обов'язкове, макс 100 символів
- ISBN: унікальний, валідний формат ISBN-10/13
- Year published: 1900-поточний рік
- Pages: позитивне число, макс 10000

### Exchange валідація
- Requester та requested user не можуть бути однією людиною
- Offered та requested книги не можуть бути однаковими
- Книги повинні бути доступні для обміну

### Review валідація
- Rating: 1-5 (ціле число)
- Content: макс 2000 символів
- Title: макс 100 символів
- Один користувач може написати лише одну рецензію на книгу

### Message валідація
- Content: обов'язкове, макс 1000 символів
- Відправник та отримувач не можуть бути однією людиною
- Повідомлення пов'язане з існуючим обміном
