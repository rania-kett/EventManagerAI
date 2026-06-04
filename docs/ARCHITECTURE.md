# EventManagerAI — Architecture

## Overview

EventManagerAI is a Flask web application for managing events with optional
AI-generated descriptions via Google Gemini.

This document describes the **skeleton** layout. Feature implementation is
intentionally deferred.

## Layered structure (clean architecture)

```
┌─────────────────────────────────────────────────────────┐
│  Presentation: templates/, static/, routes/             │
├─────────────────────────────────────────────────────────┤
│  Application:  services/ (use cases, Gemini)            │
│                factories/ (object construction)         │
├─────────────────────────────────────────────────────────┤
│  Domain/Data:  models/ (SQLAlchemy ORM)                 │
├─────────────────────────────────────────────────────────┤
│  Infrastructure: config.py, SQLite, Gemini API          │
└─────────────────────────────────────────────────────────┘
```

| Layer | Location | Responsibility |
|-------|----------|----------------|
| Entry | `app.py` | App factory, extension init, blueprint registration |
| Config | `config.py` | Environment settings, DB URI, Gemini keys |
| Routes | `routes/event_routes.py` | HTTP only; delegate to services/factories |
| Services | `services/ai_service.py` | External AI; no Flask imports in core logic |
| Factories | `factories/event_factory.py` | Map forms/dicts → `Event` instances |
| Models | `models/event.py` | Persistence schema |
| UI | `templates/`, `static/` | Bootstrap 5 views |

## Request flow (planned)

1. Browser → `event_routes` blueprint
2. Route validates input → `EventFactory` builds/updates model
3. `db.session` commits for CRUD
4. For AI: route → `AIService.generate_event_description()` → update `Event.description`

## Gemini integration (prepared)

- `config.Config.GEMINI_API_KEY` / `GEMINI_MODEL`
- `services/ai_service.py` — single integration point
- `.env.example` documents required variables
- Uses `google-genai` (Google GenAI SDK)

## Database

- SQLite file: `instance/events.db` (created on first run)
- ORM: Flask-SQLAlchemy
- Table: `events` (see `models/event.py`)

## Next implementation steps

1. Enable forms in `add_event.html` / `edit_event.html`
2. Wire POST handlers in `event_routes.py` using `EventFactory` + `db.session`
3. Flash messages and delete confirmation
4. `AIService` uses `google-genai` (`genai.Client`)
5. Add route tests and service unit tests with mocked Gemini
