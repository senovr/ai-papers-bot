

# План реализации (Implementation Plan): AI-Papers-Bot

## 1. Роль и контекст для AI-Агента (System Directive)
**Цель:** Разработать production-ready Telegram-бота на Python для агрегации, фильтрации и дистилляции научных статей с arXiv. 
**Критерии успеха:** Код должен быть чистым, модульным (Domain-Driven Design), асинхронным и легко расширяемым. Исключить хардкод. Все запросы к БД использовать через SQLAlchemy 2.0 (PostgreSQL).

## 2. Бизнес-логика и предметная область
Продукт отслеживает 3 тематики (Topics):
1. `llm_general` — Промпт-инжиниринг, архитектура LLM, новые методы reasoning'а.
2. `llm_oil_gas` — LLM в геологии, геофизике, петрофизике, бурении, ГРП.
3. `ai_oil_gas` — Любые применения ИИ/ML (прогнозирование, компьютерное зрение, графы знаний) в нефтегазе.

**Форматы выдачи (Reports):**
1. **Daily Digest:** Свежие статьи (рейтинг 80+). Под каждой статьей 3 кнопки (Callback-кнопки в Telegram):
   - *Дайджест* (суть, принцип, применение).
   - *Простыми словами* (упрощенное объяснение).
   - *Концепты* (атомы метода: проблема, тезис, метод).
2. **Weekly Summary:** Обзор трендов недели (выжимка).
3. **Monthly Narrative Essay:** Связный лонгрид о том, что произошло за месяц, плюс карта концептов.

## 3. Технологический стек
- **Язык:** Python 3.12+
- **БД:** PostgreSQL + SQLAlchemy 2.0
- **Telegram API:** Aiogram 3.x
- **LLM Integration:** 
  - `zai glm-5` первичная быстрая фильтрация.
  - `zai glm-5` — глубокий скоринг и экстракция концептов.
- **Scraping:** `arxiv` API, `beautifulsoup4`, `lxml`.
- **Task Scheduling:** `APScheduler` (AsyncIOScheduler) / `Celery` (опционально для масштабирования).
- **Инфраструктура:** Docker, Docker Compose, uv (управление зависимостями).

## 4. Архитектура данных (Database Schema)
Агент должен создать следующие модели (ORM):
- `User`: `telegram_id`, `created_at`, `settings` (JSON), `subscriptions` (Array/Enum).
- `Paper`: `arxiv_id`, `title`, `abstract`, `url`, `published_date`, `full_text_local_path`.
- `Analysis`: `paper_id` (FK), `rating` (0-100), `topic` (Enum), `digest_text`, `simple_text`.
- `Concept`: `analysis_id` (FK), `type` (problem/thesis/method), `title`, `explanation`.

## 5. 8-Ступенчатый конвейер данных (The Pipeline)
Реализовать в `src/pipeline/`:
1. **Fetch:** Парсинг новых статей с arXiv по ключевым словам.
2. **Pre-filter:** Отсев явного мусора через легкие эвристики и Gemini 3.0 Flash (остается ~10% статей).
3. **Deep Score:** Передача полного текста (Markdown) в Claude 4.5 Sonnet. Скоринг (0-100) по практической применимости.
4. **Summarize:** Генерация текстов "Дайджест" и "Простыми словами".
5. **Categorize & Extract Concepts:** Извлечение атомарных концептов (Проблема, Тезис, Метод) через structured JSON output от LLM.
6. **Store:** Транзакционное сохранение Paper + Analysis + Concepts в PostgreSQL.
7. **Schedule:** Формирование Daily/Weekly/Monthly агрегаций.
8. **Notify:** Асинхронная рассылка пользователям через Aiogram с учетом rate limits Telegram (не более 30 сообщений/сек).

## 6. Структура проекта (Directory Layout)
Создать следующую структуру перед началом написания логики:
```text
ai-papers-bot/
├── src/
│   ├── bot/                 # Aiogram логика (handlers, keyboards, middlewares)
│   ├── database/            # SQLAlchemy models, sessions, CRUD repositories
│   ├── llm/                 # Клиенты Anthropic, Gemini, промпты
│   ├── pipeline/            # Скрипты парсинга arXiv и конвейер обработки
│   ├── scheduler/           # APScheduler джобы
│   ├── core/                # Конфиг (pydantic-settings), логгер, exceptions
│   └── main.py              # Точка входа (Application bootstrap)
├── migrations/              # Alembic
├── prompts/                 # Текстовые шаблоны .md/.txt для LLM
├── tests/                   # Pytest coverage
├── docker-compose.yml
├── Dockerfile
├── requirements.txt (или pyproject.toml / uv.lock)
└── .env.example
7. Пошаговый Roadmap для Агента (Execution Phases)
Phase 1: Foundation & Database (Шаг 1)
 Инициализировать проект, настроить pyproject.toml (или uv).
 Создать core/config.py используя pydantic-settings для чтения .env.
 Настроить SQLAlchemy 2.0 engine (asyncpg) и базовые модели (User, Paper, Analysis, Concept).
 Настроить Alembic и создать первичную миграцию.
Phase 2: ArXiv Fetcher & Pre-filter (Шаг 2)
 Написать arxiv_client.py для выгрузки статей.
 Интегрировать Gemini API.
 Создать функцию для быстрой оценки: async def is_relevant_flash(abstract: str) -> bool.
Phase 3: Deep LLM Processing (Шаг 3)
 Интегрировать Anthropic API. Обязательно включить поддержку параметров thinking (Extended Thinking).
 Написать четкие, концентрированные (clear and concise) системные промпты, ориентированные на выявление:
Специфики работы LLM (например, limits of attention).
Улучшений для сейсмики/петрофизики.
 Реализовать парсер JSON-ответа от LLM для извлечения массива концептов.
Phase 4: Telegram Bot UI/UX (Шаг 4)
 Инициализировать Aiogram bot & dispatcher.
 Сделать команду /start с приветствием и настройкой подписок (Inline Keyboard с 3 темами).
 Реализовать форматирование карточки статьи: Заголовок, Рейтинг, Краткая суть.
 Сделать CallbackHandlers для кнопок: [Дайджест], [Простыми словами], [Концепты]. Нажатие должно изменять сообщение (edit_message_text), а не слать новое.
Phase 5: Schedulers & Reporting (Шаг 5)
 Настроить APScheduler.
 Создать daily_job: сбор статей за 24 часа, фильтрация тех, у которых рейтинг > 80, отправка подписчикам.
 Создать weekly_job: агрегация лучших статей за 7 дней, прогон через LLM для создания Summary, рассылка.
 Создать monthly_job: создание "карты концептов" и Narrative Essay. При превышении 4096 символов Telegram — отправлять через Telegraph-форматирование или разбивать на части.
Phase 6: Error Handling, DevOps & Docker (Шаг 6)
 Настроить структурированное логирование (structlog или loguru).
 Внедрить exponential backoff (tenacity) для вызовов LLM API и парсинга arXiv во избежание падений при rate limits.
 Написать Dockerfile (multi-stage) и docker-compose.yml (App + PostgreSQL + Redis для стейт-машины Aiogram, если нужно).
8. Definition of Done (DoD) для Агента
Агент должен завершить работу только когда:
- Выполнены все 6 фаз.
- Проект запускается одной командой docker-compose up -d.
- Код строго типизирован (type hints).
- Промпты для LLM вынесены в отдельные файлы в папке prompts/, чтобы владелец продукта мог их легко редактировать.

9. Фокус - на максимальную автономность, никаких вопросов пользователю.

10. После каждого существенного этапа- выполняй заливку кода в репозиторий github.