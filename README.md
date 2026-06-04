# EventManagerAI

Professional Flask skeleton for an **Event Management** application with planned **Google Gemini** integration for AI-generated event descriptions.

## Features (planned)

| Feature | Status |
|---------|--------|
| List events | Skeleton route + template |
| Add event | Skeleton |
| Edit event | Skeleton |
| Delete event | Stub (501) |
| Generate description (Gemini) | Stub in `services/ai_service.py` |

## Tech stack

- Python, Flask, SQLite, SQLAlchemy (Flask-SQLAlchemy)
- Bootstrap 5 (CDN)
- Gemini API (prepared, not wired)

## Project structure

```
EventManagerAI/
├── app.py                 # Application factory & entry point
├── config.py              # Environment configuration
├── requirements.txt
├── models/
│   ├── __init__.py        # SQLAlchemy `db` instance
│   └── event.py           # Event ORM model
├── routes/
│   └── event_routes.py    # Event blueprint (HTTP)
├── services/
│   └── ai_service.py      # Gemini integration (future)
├── factories/
│   └── event_factory.py   # Build/update Event from form data
├── templates/             # Jinja2 + Bootstrap 5
├── static/css, static/js
├── tests/
├── docs/ARCHITECTURE.md
└── .env.example
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for layer responsibilities and next steps.

## Quick start

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

copy .env.example .env         # optional; set GEMINI_API_KEY later

flask --app app run --debug
# or: python app.py
```

Open http://127.0.0.1:5000/ — redirects to http://127.0.0.1:5000/events/

## Configuration

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Flask session signing |
| `DATABASE_URL` | SQLAlchemy URI (default: SQLite in `instance/events.db`) |
| `GEMINI_API_KEY` | Google AI API key for descriptions |
| `GEMINI_MODEL` | Model name (default: `gemini-2.0-flash`) |
| `FLASK_ENV` | `development` \| `production` \| `testing` |

## Tests

```bash
pip install pytest
pytest
```

## License

MIT (adjust as needed).
