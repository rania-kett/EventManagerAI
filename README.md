# EventManager AI

**EventManager AI** is an AI-powered event management platform built with Flask and SQLite. It combines a premium marketing experience with a practical back-office: create and manage events, track them on a Kanban board, and generate professional descriptions with Google Gemini.

---

## 1. Project Overview

EventManager AI helps organizers plan events from draft to completion. The application provides:

- A **marketing landing page** to present the product
- A **management platform** for full event CRUD
- A **Kanban board** with drag-and-drop status updates
- **AI-assisted copywriting** for event descriptions (French output via Gemini)

The codebase follows a layered architecture (routes → services → factories/validators → models) with refactoring and code-quality improvements applied throughout the project lifecycle.

| Item | Detail |
|------|--------|
| **Language** | Python 3 |
| **Framework** | Flask 3 |
| **Database** | SQLite (SQLAlchemy ORM) |
| **UI** | Bootstrap 5, custom premium CSS |
| **AI** | Google Gemini API |

---

## 2. Features

### Event management
- Create events (title, date, location, category, description, status)
- Edit existing events
- Delete events with confirmation
- Server-side validation with user-friendly error messages

### Kanban board
- Visual board at `/events/` grouped by status columns
- Drag-and-drop to update event status in real time
- Event cards with metadata preview (date, location, category, description excerpt)
- Six workflow statuses: Draft → Planned → Confirmed → In Progress → Completed → Cancelled

### AI description generation
- One-click **Générer la description** on create/edit forms
- Powered by **Google Gemini** (`google-generativeai`)
- Context-aware prompts (title, location, date, category)
- French marketing-style output

### User experience
- Premium responsive landing page
- Consistent Bootstrap 5 UI across platform pages
- Flash messages for success and error feedback
- Mobile- and tablet-friendly Kanban layout

### Engineering quality
- **Factory Pattern** for building and updating `Event` models
- **Service layer** for business logic (`EventService`, `AIService`)
- **Validators** and shared constants for form fields
- Refactoring for maintainability and **SonarLint**-driven improvements
- Automated tests with **pytest** (34+ tests)

---

## 3. Technologies

| Category | Stack |
|----------|--------|
| Backend | Python, Flask, Flask-SQLAlchemy, SQLAlchemy |
| Database | SQLite |
| Frontend | HTML5, Jinja2, CSS3, JavaScript |
| UI framework | Bootstrap 5, Bootstrap Icons |
| AI | Google Gemini API (`google-generativeai`) |
| Config | `python-dotenv` |
| Testing | pytest |
| Version control | Git & GitHub |

---

## 4. Architecture

```
EventManagerAI/
├── app.py                    # Application factory & entry point
├── config.py                 # Environment configuration
├── constants/                # Shared form field definitions
├── factories/                # EventFactory — build/update ORM instances
├── models/                   # SQLAlchemy models (Event, status)
├── routes/                   # HTTP blueprints (events, landing, AI handlers)
├── services/                 # EventService, AIService, messages
├── templates/                # Jinja2 views (landing, Kanban, forms)
├── static/                   # CSS, JavaScript
├── utils/                    # Date parsing helpers
├── validators/               # Form validation
├── tests/                    # pytest suite
└── docs/ARCHITECTURE.md      # Detailed architecture notes
```

### Layered request flow

```
Browser → routes/event_routes.py
       → services/event_service.py
       → validators/ + factories/
       → models/event.py → SQLite

AI:  routes → routes/ai_handlers.py → services/ai_service.py → Gemini API
```

| Layer | Responsibility |
|-------|----------------|
| **Routes** | HTTP, templates, JSON responses |
| **Services** | Use cases (CRUD, Kanban, AI orchestration) |
| **Factories** | Map form data → `Event` instances |
| **Validators** | Input validation before persistence |
| **Models** | Persistence schema only |

---

## 5. Installation

### Prerequisites
- Python 3.10+ recommended
- `pip`
- Git
- A [Google AI Studio](https://aistudio.google.com/apikey) API key (for AI features)

### Clone the repository

```bash
git clone https://github.com/rania-kett/EventManagerAI.git
cd EventManagerAI
```

### Create a virtual environment (recommended)

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## 6. Environment Variables

Create a `.env` file at the project root (never commit it). Use `.env.example` as a template if available.

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Optional — default: sqlite:///instance/events.db
# DATABASE_URL=sqlite:///instance/events.db

# Google Gemini — required for AI description generation
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash
```

| Variable | Required | Description |
|----------|----------|-------------|
| `FLASK_ENV` | No | `development`, `production`, or `testing` (default: `development`) |
| `SECRET_KEY` | Yes (prod) | Flask session signing key |
| `DATABASE_URL` | No | SQLAlchemy database URI |
| `GEMINI_API_KEY` | For AI | Google Gemini API key |
| `GEMINI_MODEL` | No | Model name (default: `gemini-2.5-flash`) |

> **Security:** Put your real API key only in `.env`. Never commit secrets to `.env.example` or Git.

---

## 7. Run the Project

```bash
# Option A — Flask CLI
flask --app app run --debug

# Option B — Direct Python
python app.py
```

Open in your browser:

| URL | Page |
|-----|------|
| http://127.0.0.1:5000/ | Marketing landing page |
| http://127.0.0.1:5000/events/ | Kanban board |
| http://127.0.0.1:5000/events/add | Create event |

The SQLite database file is created automatically at `instance/events.db` on first run.

---

## 8. Run Tests

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

Run a specific test module:

```bash
pytest tests/test_kanban.py
```

The test suite covers application smoke tests, CRUD routes, Kanban status updates, event model, AI service (mocked), and landing page sections.

---

## 9. AI Integration

### How it works

1. User fills in event fields (at minimum **title**) on the create or edit form.
2. User clicks **Générer la description**.
3. Frontend (`static/js/ai-generate.js`) sends a POST request to `/events/ai/generate-description`.
4. `AIService` builds a French marketing prompt and calls Gemini.
5. The generated text is inserted into the description field; the user can edit before saving.

### Configuration

1. Obtain an API key from [Google AI Studio](https://aistudio.google.com/apikey).
2. Add `GEMINI_API_KEY=...` to `.env`.
3. Restart the Flask server.

If the key is missing, the generate button is disabled and a configuration hint is shown.

### Key files

| File | Role |
|------|------|
| `services/ai_service.py` | Gemini API facade |
| `routes/ai_handlers.py` | JSON response handling |
| `templates/partials/ai_description_block.html` | UI block + button |
| `static/js/ai-generate.js` | Client-side fetch logic |

---

## 10. Kanban Workflow

### Status columns

Internal keys (stored in database) use English snake_case. Display labels are defined in `models/event_status.py`.

| Key | Label (UI) |
|-----|------------|
| `draft` | Draft |
| `planned` | Planned |
| `confirmed` | Confirmed |
| `in_progress` | In Progress |
| `completed` | Completed |
| `cancelled` | Cancelled |

### User flow

1. **Create** an event and choose an initial status (default: Draft).
2. Open the **Kanban board** at `/events/`.
3. **Drag and drop** a card into another column to update its status.
4. JavaScript (`static/js/kanban.js`) sends `PATCH /events/<id>/status` with JSON `{ "status": "..." }`.
5. The board updates optimistically; a toast confirms success or rolls back on error.

### Key files

| File | Role |
|------|------|
| `models/event_status.py` | Status definitions |
| `services/event_service.py` | `group_by_status`, `update_status` |
| `templates/index.html` | Kanban board layout |
| `templates/partials/kanban_card.html` | Event card partial |
| `static/css/kanban.css` | Kanban styles |
| `static/js/kanban.js` | Drag-and-drop logic |

---

## 11. Contributors

This project was developed collaboratively:

| Contributor | Role |
|-------------|------|
| **Rania Kettani** | Project lead & development |
| **Huda Erimi** | Development & features |
| **Sabrine Essadeq** | Development, refactoring & quality |

---

## 12. Future Improvements

- [ ] Migrate from deprecated `google-generativeai` to `google.genai`
- [ ] Add Flask-Migrate (Alembic) for database migrations
- [ ] CSRF protection on all POST/PATCH endpoints
- [ ] User authentication and multi-tenant workspaces
- [ ] Email notifications and contact form persistence
- [ ] Participant management module
- [ ] Event publishing and public event pages
- [ ] API documentation (OpenAPI / REST)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Internationalization (i18n) with Flask-Babel
- [ ] Docker containerization for deployment

---

## Git Workflow

The project uses a **Git Flow**–inspired branching model:

```
main          → production-ready releases
develop       → integration branch
feature/*     → new features (e.g. feature/ux-improvements)
hotfix/*      → urgent fixes
```

Typical flow: `feature/*` → PR to `develop` → merge to `main` when stable.

---

## License

MIT — see repository license file or adjust as needed for your organization.

---

<p align="center">
  <strong>EventManager AI</strong> — Gestion d'événements augmentée par l'intelligence artificielle
</p>
