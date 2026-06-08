# EventManager AI — Architecture

> Technical architecture reference for the EventManager AI platform.  
> Stack: Flask · SQLite · Bootstrap 5 · Google Gemini

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Presentation Layer](#3-presentation-layer)
4. [Routing Layer](#4-routing-layer)
5. [Service Layer](#5-service-layer)
6. [Factory Layer](#6-factory-layer)
7. [Validation Layer](#7-validation-layer)
8. [Data Layer](#8-data-layer)
9. [Database Architecture](#9-database-architecture)
10. [AI Integration Architecture](#10-ai-integration-architecture)
11. [Kanban Workflow](#11-kanban-workflow)
12. [Project Structure](#12-project-structure)
13. [Testing Strategy](#13-testing-strategy)
14. [Refactoring Improvements](#14-refactoring-improvements)
15. [Future Enhancements](#15-future-enhancements)
16. [Conclusion](#16-conclusion)

---

## 1. Introduction

**EventManager AI** is a web application for planning and managing events. It combines:

- Full **event CRUD** (create, read, update, delete)
- A **Kanban board** with drag-and-drop status management
- **AI-generated descriptions** powered by Google Gemini
- A **premium marketing landing page** and a responsive Bootstrap 5 management UI

The backend is built with **Flask** and persists data in **SQLite** via **SQLAlchemy**. Business logic is deliberately separated from HTTP handling through a **service layer**, while object construction is delegated to a **factory pattern**. Input validation lives in a dedicated validator module.

Design goals:

| Goal | Approach |
|------|----------|
| **Separation of concerns** | Routes → Services → Factories / Validators → Models |
| **Testability** | In-memory SQLite, pytest fixtures, mocked Gemini |
| **Maintainability** | Shared constants, DRY form handling, small focused modules |
| **Security** | Secrets in `.env`, never in source control |
| **Code quality** | Refactoring passes and SonarLint-driven cleanups |

---

## 2. High-Level Architecture

EventManager AI follows a **layered architecture** inspired by clean architecture principles. Each layer has a single responsibility and depends inward — outer layers orchestrate, inner layers persist.

```
┌──────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                            │
│   templates/ · static/ (CSS, JS) · Bootstrap 5 · Jinja2              │
├──────────────────────────────────────────────────────────────────────┤
│                          ROUTING LAYER                               │
│   routes/event_routes.py · routes/landing_routes.py                  │
│   routes/ai_handlers.py                                              │
├──────────────────────────────────────────────────────────────────────┤
│                          SERVICE LAYER                               │
│   services/event_service.py · services/ai_service.py                 │
│   services/messages.py                                               │
├──────────────────────────────────────────────────────────────────────┤
│                    FACTORY · VALIDATION · UTILS                      │
│   factories/event_factory.py · validators/event_validator.py         │
│   constants/event_form.py · utils/dates.py                           │
├──────────────────────────────────────────────────────────────────────┤
│                           DATA LAYER                                 │
│   models/event.py · models/event_status.py · models/db_schema.py     │
├──────────────────────────────────────────────────────────────────────┤
│                        INFRASTRUCTURE                                │
│   config.py · SQLite (instance/events.db) · Google Gemini API      │
└──────────────────────────────────────────────────────────────────────┘
```

### Application bootstrap

`app.py` implements the **application factory pattern**:

1. Load configuration from `config.py` (`DevelopmentConfig`, `ProductionConfig`, `TestingConfig`)
2. Apply environment variables via `apply_env_to_app()`
3. Initialize Flask-SQLAlchemy (`db.init_app`)
4. Ensure database schema (`ensure_database_schema()`)
5. Register blueprints (`landing_bp`, `event_bp`)
6. Inject template globals (`ai_configured`)

### Primary request flows

**Event CRUD (HTML form):**

```
Browser POST → event_routes._handle_event_form()
            → EventService.create_from_form() / update_from_form()
            → EventValidator.validate()
            → EventFactory.from_form() / apply_update()
            → db.session.commit()
            → redirect to Kanban board
```

**Kanban status update (JSON API):**

```
Browser drag-drop → kanban.js fetch PATCH
                 → event_routes.update_status()
                 → EventService.update_status()
                 → db.session.commit()
                 → JSON { success, status, status_label }
```

**AI description generation (JSON API):**

```
Browser click → ai-generate.js fetch POST
             → event_routes.ai_generate_description()
             → ai_handlers.generate_description_response()
             → AIService.generate_event_description()
             → Google Gemini API
             → JSON { success, description }
```

---

## 3. Presentation Layer

The presentation layer delivers all user-facing content: marketing pages, the Kanban board, event forms, and client-side interactivity.

### Template organization

| Path | Purpose |
|------|---------|
| `templates/landing.html` | Premium marketing homepage |
| `templates/index.html` | Kanban board |
| `templates/add_event.html` | Create event form |
| `templates/edit_event.html` | Edit event form |
| `templates/layouts/app.html` | Management platform layout |
| `templates/layouts/premium.html` | Landing page layout |
| `templates/partials/event_form_fields.html` | Shared form fields (DRY) |
| `templates/partials/kanban_card.html` | Reusable Kanban event card |
| `templates/partials/ai_description_block.html` | AI generate button block |
| `templates/macros/forms.html` | Jinja form helpers |

Templates extend base layouts and receive context from routes (events, errors, form data, `ai_configured`).

### Static assets

| Asset | Role |
|-------|------|
| `static/css/premium.css` | Landing page styling |
| `static/css/app.css` | Platform shell styling |
| `static/css/kanban.css` | Kanban board layout and cards |
| `static/css/style.css` | Shared utilities |
| `static/js/kanban.js` | Drag-and-drop + status API |
| `static/js/ai-generate.js` | Gemini description fetch |
| `static/js/landing.js` | Landing animations and scroll |
| `static/js/main.js` | Shared client utilities |

### UI framework

- **Bootstrap 5** for grid, forms, buttons, toasts, and responsive breakpoints
- **Bootstrap Icons** for visual affordances
- French copy throughout the management UI (flash messages, labels, Kanban header)

### Context injection

`app.py` registers a context processor that exposes `ai_configured` to all templates. Forms and the AI block use this flag to enable or disable the **Générer la description** button when `GEMINI_API_KEY` is missing.

---

## 4. Routing Layer

HTTP concerns are isolated in Flask **blueprints**. Routes are thin: they parse requests, delegate to services, and return templates or JSON responses.

### Blueprints

| Blueprint | Module | Prefix | Responsibility |
|-----------|--------|--------|----------------|
| `landing` | `routes/landing_routes.py` | `/` (via `app.home`) | Contact form handling |
| `events` | `routes/event_routes.py` | `/events` | CRUD, Kanban, AI endpoints |

### Event routes

| Method | Path | Handler | Response |
|--------|------|---------|----------|
| `GET` | `/events/` | `index` | Kanban board HTML |
| `GET` / `POST` | `/events/add` | `add_event` | Create form / redirect |
| `GET` / `POST` | `/events/<id>/edit` | `edit_event` | Edit form / redirect |
| `POST` | `/events/<id>/delete` | `delete_event` | Redirect after delete |
| `PATCH` / `POST` | `/events/<id>/status` | `update_status` | JSON status update |
| `POST` | `/events/ai/generate-description` | `ai_generate_description` | JSON AI response |
| `POST` | `/events/<id>/generate-description` | `generate_description` | JSON AI + DB save |

### Shared form handler

`_handle_event_form()` centralizes the GET/POST cycle for create and edit:

1. On **POST**: call `EventService.create_from_form()` or `update_from_form()`
2. On success: flash message and redirect to Kanban
3. On validation failure: re-render template with errors and normalized form data
4. On **GET**: render empty or pre-filled form

### AI handlers

`routes/ai_handlers.py` extracts JSON response logic from route functions:

- `parse_ai_payload()` — reads JSON or form body
- `generate_description_response()` — generate without DB write (forms)
- `generate_and_save_description_response()` — generate and persist (existing event)
- `_run_ai_generation()` — shared try/except and HTTP status mapping

This keeps `event_routes.py` focused on routing while AI error handling (502, 503) lives in one place.

---

## 5. Service Layer

Services implement **use cases** — the application's business operations. They coordinate validators, factories, and the database without knowing about HTTP.

### EventService (`services/event_service.py`)

| Method | Responsibility |
|--------|----------------|
| `list_events_ordered()` | Fetch all events (date desc, id desc) |
| `get_event_or_404()` | Load event or abort 404 |
| `kanban_column_definitions()` | Status columns for templates |
| `group_by_status()` | Partition events into Kanban columns |
| `create_from_form()` | Validate → factory → persist new event |
| `update_from_form()` | Validate → factory → persist update |
| `event_to_form()` | Map ORM entity → form dict |
| `update_status()` | Validate status key → commit |
| `delete()` | Remove event, return title for flash |
| `save_description()` | Persist AI-generated text |
| `generate_description_with_ai()` | Delegate to `AIService` |

`FormResult` and `StatusResult` typed tuples make return contracts explicit for routes and tests.

### AIService (`services/ai_service.py`)

Facade over the **Google Gemini API**:

- Configuration via constructor or `from_config(app.config)`
- `generate_event_description()` — builds French marketing prompt, calls Gemini
- Error taxonomy: `AIServiceError`, `AIServiceNotConfiguredError`
- Provider error mapping (quota, model not found) to user-friendly French messages

`AIService` has **no Flask imports** in its core logic — only `ai_handlers.py` bridges Flask config to the service.

### Messages (`services/messages.py`)

Centralized French flash message builders:

- `flash_event_created(title)`
- `flash_event_updated(title)`
- `flash_event_deleted(title)`

---

## 6. Factory Layer

The **Factory Pattern** isolates construction of `Event` ORM instances from routes and services.

### EventFactory (`factories/event_factory.py`)

| Method | Purpose |
|--------|---------|
| `from_form(form_data)` | Create new `Event` via `Event.create()` |
| `apply_update(event, form_data)` | Mutate existing event fields |
| `_optional_stripped(value)` | Normalize optional string fields |
| `_apply_status(event, raw_status)` | Set status only if valid |

The factory:

- Parses dates through `utils.dates.parse_event_date()`
- Applies `DEFAULT_STATUS` when status is missing on create
- Does **not** validate — validation is always performed by `EventValidator` first
- Does **not** commit — `EventService` owns the database transaction

### Why a factory?

| Benefit | Explanation |
|---------|-------------|
| **Single construction point** | Form → model mapping lives in one module |
| **Testability** | Factory methods can be unit-tested independently |
| **Separation** | `Event` model stays persistence-focused; mapping rules stay in `factories/` |

---

## 7. Validation Layer

Server-side validation ensures data integrity before any database write.

### EventValidator (`validators/event_validator.py`)

| Method | Purpose |
|--------|---------|
| `validate(data)` | Returns `field → error message` dict |
| `normalize_form_data(data)` | Strip and default values for re-render |
| `_validate_required_fields()` | Title, date, location, category, description |
| `_validate_date_field()` | ISO date parsing via `parse_event_date()` |
| `_validate_status_field()` | Status presence and `is_valid_status()` |

### Constants integration

Field names and French labels come from `constants/event_form.py`:

```python
EVENT_FORM_FIELDS = ("title", "date", "location", "category", "description")
EVENT_FIELD_LABELS = {"title": "Titre", "date": "Date", ...}
```

This prevents label/name drift between templates, validators, and tests.

### Validation flow

```
POST data → EventValidator.normalize_form_data()  # for re-display
         → EventValidator.validate()
         → if errors: return (None, errors, normalized) — no DB write
         → if valid:   EventFactory → db.session.commit()
```

---

## 8. Data Layer

The data layer defines persistence schema and domain-adjacent helpers. It does **not** contain HTTP or business orchestration logic.

### Core models

**`models/event.py` — `Event`**

| Column | Type | Notes |
|--------|------|-------|
| `id` | `Integer` PK | Auto-increment |
| `title` | `String(200)` | Required |
| `date` | `Date` | Indexed |
| `location` | `String(255)` | Optional |
| `category` | `String(100)` | Indexed |
| `description` | `Text` | Optional; may be AI-generated |
| `status` | `String(32)` | Indexed; Kanban column key |

Properties and helpers:

- `status_label` — human-readable label from `STATUS_LABELS`
- `to_dict()` — serialization for tests and APIs
- `Event.create()` — class method for unsaved instances

**`models/event_status.py`**

Single source of truth for Kanban statuses:

```python
EVENT_STATUSES = [
    ("draft", "Draft", "status-draft"),
    ("planned", "Planned", "status-planned"),
    ("confirmed", "Confirmed", "status-confirmed"),
    ("in_progress", "In Progress", "status-in-progress"),
    ("completed", "Completed", "status-completed"),
    ("cancelled", "Cancelled", "status-cancelled"),
]
```

Exports: `STATUS_KEYS`, `STATUS_LABELS`, `DEFAULT_STATUS`, `is_valid_status()`.

### Database extension

`models/__init__.py` exposes the shared `db = SQLAlchemy()` instance, initialized in `create_app()`.

---

## 9. Database Architecture

### Engine and storage

| Setting | Value |
|---------|-------|
| Engine | SQLite |
| Default path | `instance/events.db` |
| ORM | Flask-SQLAlchemy 3 + SQLAlchemy 2 |
| Test database | `sqlite:///:memory:` (`TestingConfig`) |

Connection URI is configured via `SQLALCHEMY_DATABASE_URI` in `config.py`, overridable with `DATABASE_URL`.

### Schema management

`models/db_schema.py` provides `ensure_database_schema()`:

1. Compare expected columns (`Event.__table__.columns`) with actual SQLite columns
2. If table missing → `db.create_all()`
3. If schema drift in development → optionally `drop_all()` + `create_all()` when `RESET_DB_ON_SCHEMA_DRIFT=True`
4. If drift in production → raise `RuntimeError` with remediation instructions

> **Note:** This project does not use Alembic migrations. Schema changes during development trigger a controlled reset rather than incremental migration.

### Entity relationship

Currently a **single-table** design:

```
events
├── id (PK)
├── title
├── date
├── location
├── category
├── description
└── status
```

No foreign keys or related tables yet. Future modules (participants, users) would extend this schema.

### Indexing strategy

Indexes on `date`, `category`, and `status` support:

- Kanban grouping and filtering
- Ordered listing (`ORDER BY date DESC`)
- Status validation lookups

---

## 10. AI Integration Architecture

AI description generation is a cross-cutting feature spanning configuration, services, routes, templates, and client JavaScript.

### Configuration (`config.py`)

| Variable | Purpose |
|----------|---------|
| `GEMINI_API_KEY` | API authentication |
| `GEMINI_MODEL` | Model name (default: `gemini-2.5-flash`) |

`apply_env_to_app()` refreshes config from `.env` on each request in debug mode. `is_gemini_configured()` gates UI availability.

### Service design

```
AIService
├── __init__(api_key, model)
├── from_config(flask_config)
├── is_configured()
├── generate_event_description(title, location, event_date, category)
├── _ensure_ready(title)          # key, package, title checks
├── _build_prompt(...)            # French copywriter instructions
├── _request_description(prompt)  # genai.GenerativeModel call
└── _map_provider_error(exc)      # quota / 404 → AIServiceError
```

### API endpoints

**Form generation (no DB write):**

```
POST /events/ai/generate-description
Body: { "title", "location", "category", "date" }
Response 200: { "success": true, "description": "..." }
Response 400: missing title
Response 502: Gemini error
Response 503: API key not configured
```

**Persist to existing event:**

```
POST /events/<id>/generate-description
→ generates + EventService.save_description()
```

### Client integration

`static/js/ai-generate.js`:

1. Reads form field values (title required)
2. POSTs JSON to `data-generate-url`
3. Inserts returned description into the textarea
4. Shows spinner and status messages

`templates/partials/ai_description_block.html` renders the button, disabled when `ai_configured` is false.

### Dependency

Package: `google-generativeai` (listed in `requirements.txt`).  
A future migration to `google.genai` is planned — the current package is deprecated.

---

## 11. Kanban Workflow

The Kanban board is the primary operational view for event lifecycle management.

### Status lifecycle

```
┌─────────┐   ┌─────────┐   ┌───────────┐   ┌─────────────┐   ┌───────────┐   ┌───────────┐
│  Draft  │ → │ Planned │ → │ Confirmed │ → │ In Progress │ → │ Completed │   │ Cancelled │
└─────────┘   └─────────┘   └───────────┘   └─────────────┘   └───────────┘   └───────────┘
```

Statuses are stored as English snake_case keys (`in_progress`). Display labels and CSS modifiers are defined in `EVENT_STATUSES`.

### Server-side grouping

`EventService.group_by_status()`:

1. Initialize empty lists for each `STATUS_KEYS` entry
2. Assign each event to its status column (fallback: `draft`)
3. Return `Dict[str, List[Event]]` for Jinja iteration

`templates/index.html` renders one column per status, including empty-state messaging when no events exist.

### Drag-and-drop (client)

`static/js/kanban.js` implements native HTML5 drag-and-drop:

```
dragstart → store card + source column
drop      → read data-drop-zone (target status)
          → optimistic DOM move
          → PATCH /events/<id>/status  { "status": "..." }
success   → update badge, show toast
failure   → rollback card to source column, error toast
```

Key behaviors:

- Optimistic UI update before server confirmation
- Rollback on network or validation failure
- Column count badges updated after each move
- Toast feedback (French messages)

### Event cards

`templates/partials/kanban_card.html` displays:

- Title and status badge
- Date, location, category metadata
- Description preview (truncated)
- Edit and delete action buttons

---

## 12. Project Structure

```
EventManagerAI/
│
├── app.py                          # Application factory & entry point
├── config.py                       # Environment & Gemini configuration
├── requirements.txt                # Python dependencies
│
├── constants/
│   ├── __init__.py
│   └── event_form.py               # Form field names, labels, defaults
│
├── factories/
│   ├── __init__.py
│   └── event_factory.py            # Event construction & updates
│
├── models/
│   ├── __init__.py                 # SQLAlchemy db instance
│   ├── db_schema.py                # Schema drift detection & reset
│   ├── event.py                    # Event ORM model
│   └── event_status.py             # Kanban status definitions
│
├── routes/
│   ├── __init__.py
│   ├── event_routes.py             # Event CRUD, Kanban, AI routes
│   ├── ai_handlers.py              # AI JSON response helpers
│   └── landing_routes.py           # Contact form route
│
├── services/
│   ├── __init__.py
│   ├── event_service.py            # Event use cases
│   ├── ai_service.py               # Gemini integration
│   └── messages.py                 # Flash message builders
│
├── validators/
│   ├── __init__.py
│   └── event_validator.py          # Form validation
│
├── utils/
│   ├── __init__.py
│   └── dates.py                    # ISO date parsing
│
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── index.html                  # Kanban board
│   ├── add_event.html
│   ├── edit_event.html
│   ├── layouts/                    # app.html, premium.html
│   ├── partials/                   # form fields, kanban card, AI block
│   └── macros/                     # Jinja form macros
│
├── static/
│   ├── css/                        # premium, app, kanban, style
│   └── js/                         # kanban, ai-generate, landing, main
│
├── tests/
│   ├── conftest.py                 # Shared fixtures & helpers
│   ├── test_app.py
│   ├── test_add_event.py
│   ├── test_edit_event.py
│   ├── test_delete_event.py
│   ├── test_kanban.py
│   ├── test_event_model.py
│   ├── test_ai_service.py
│   └── test_landing.py
│
├── docs/
│   └── ARCHITECTURE.md             # This document
│
└── instance/
    └── events.db                   # SQLite database (gitignored)
```

---

## 13. Testing Strategy

The project uses **pytest** with **34 automated tests** covering routes, services, models, Kanban behavior, AI integration, and the landing page.

### Test configuration

`tests/conftest.py` provides:

| Fixture | Purpose |
|---------|---------|
| `app` | `create_app("testing")` with in-memory SQLite |
| `client` | Flask test client |
| `sample_event` | Single persisted event |
| `sample_events` | Two events in different Kanban columns |
| `valid_event_payload()` | Default valid form data helper |

`TestingConfig` sets `SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"` for isolation and speed.

### Test modules

| Module | Coverage |
|--------|----------|
| `test_app.py` | App factory smoke tests |
| `test_add_event.py` | Create form GET/POST, validation errors |
| `test_edit_event.py` | Edit form GET/POST, persistence |
| `test_delete_event.py` | Delete route and DB removal |
| `test_kanban.py` | Board rendering, PATCH status, invalid status |
| `test_event_model.py` | `Event.create()`, `to_dict()`, `status_label` |
| `test_ai_service.py` | AIService with mocked `genai` |
| `test_landing.py` | Landing page sections and contact form |

### Testing principles

1. **No real Gemini calls** — `unittest.mock.patch` on `services.ai_service.genai`
2. **Database isolation** — each test gets a fresh in-memory schema
3. **HTTP-level tests** — `client.post()`, `client.patch()` for route integration
4. **Shared helpers** — `valid_event_payload()` reduces duplication across CRUD tests

### Running tests

```bash
pytest          # full suite
pytest -v       # verbose
pytest tests/test_kanban.py  # single module
```

---

## 14. Refactoring Improvements

Several refactoring passes improved maintainability, reduced duplication, and addressed SonarLint findings.

### Structural refactoring

| Change | Benefit |
|--------|---------|
| **`constants/event_form.py`** | Single source for field names and French labels |
| **`utils/dates.py`** | Centralized `parse_event_date()` — no duplicated date parsing |
| **`services/messages.py`** | Flash messages extracted from routes |
| **`routes/ai_handlers.py`** | AI JSON logic separated from HTTP routing |
| **`_handle_event_form()`** | DRY create/edit form flow in `event_routes.py` |
| **`templates/partials/event_form_fields.html`** | Shared form fields between add and edit |
| **`tests/conftest.py`** | Shared fixtures and `valid_event_payload()` |
| **`models/db_schema.py`** | Safe schema drift handling in development |

### Service and factory cleanup

- `EventValidator` split into focused private methods (`_validate_required_fields`, `_validate_date_field`, `_validate_status_field`)
- `EventFactory` helpers (`_optional_stripped`, `_apply_status`) reduce inline logic
- `EventService` typed return tuples (`FormResult`, `StatusResult`) clarify contracts
- `AIService` split into `_ensure_ready`, `_build_prompt`, `_request_description`, `_map_provider_error`

### SonarLint improvements

| Area | Improvement |
|------|-------------|
| **Magic numbers** | Named constants for timeouts and scroll offsets in JS |
| **Configuration** | Centralized default Gemini model in `config.py` |
| **Unused imports** | Removed dead imports (e.g. unused typing imports in services) |
| **Duplication** | Eliminated repeated form validation and date parsing logic |
| **Method size** | Large route handlers decomposed into service + handler modules |

These changes keep the codebase aligned with clean-code principles while preserving existing behavior and test coverage.

---

## 15. Future Enhancements

| Priority | Enhancement |
|----------|-------------|
| High | Migrate from `google-generativeai` to `google.genai` |
| High | Add Flask-Migrate (Alembic) for production schema evolution |
| High | CSRF protection on POST/PATCH endpoints |
| Medium | User authentication and role-based access |
| Medium | Participant management module |
| Medium | Persist contact form submissions |
| Medium | REST API with OpenAPI documentation |
| Low | Internationalization (Flask-Babel) for full i18n |
| Low | Docker containerization and CI/CD (GitHub Actions) |
| Low | Real-time Kanban updates via WebSockets |

---

## 16. Conclusion

EventManager AI demonstrates a **pragmatic layered architecture** on Flask:

- **Routes** handle HTTP and rendering only
- **Services** own business use cases
- **Factories** construct domain objects
- **Validators** guard data integrity
- **Models** focus on persistence

The Kanban board and Gemini integration are first-class features with clear separation between server logic (`EventService`, `AIService`) and client behavior (`kanban.js`, `ai-generate.js`). Automated tests and refactoring passes keep the codebase maintainable as new modules are added.

For setup and usage instructions, see the project [README.md](../README.md).

---

1. Enable forms in `add_event.html` / `edit_event.html`
2. Wire POST handlers in `event_routes.py` using `EventFactory` + `db.session`
3. Flash messages and delete confirmation
4. `AIService` uses `google-genai` (`genai.Client`)
5. Add route tests and service unit tests with mocked Gemini
