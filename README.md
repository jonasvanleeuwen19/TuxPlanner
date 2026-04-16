# TuxPlanner

The ULTIMATE self-hosted planner app — a personal calendar with todos and a daily overview.

![TuxPlanner UI](https://github.com/user-attachments/assets/8f542f8d-786e-4398-8ea7-9f94331801d8)

## Stack

| Layer    | Technology                          |
|----------|-------------------------------------|
| Backend  | Python · FastAPI · SQLAlchemy       |
| Database | PostgreSQL                          |
| Frontend | Vue 3 · Vuetify 3 · FullCalendar 6  |

## Features

- 📅 **FullCalendar** — month / week / day views, drag-and-drop events
- 📋 **Sidebar** — Today panel (date, week number, day-of-year) + Todo list
- ✅ **Todos** — create, complete, delete with optional due date
- 🗓️ **Events** — create, edit, delete, colour-code appointments
- 🌙 **Dark mode** toggle
- 🌍 Dutch locale

## Quick Start (Docker Compose)

```bash
# 1. Clone the repo
git clone https://github.com/jonasvanleeuwen19/TuxPlanner.git
cd TuxPlanner

# 2. Start everything (DB + backend + frontend)
docker compose up --build

# 3. Open the app
#   Frontend: http://localhost:5173
#   API docs:  http://localhost:8000/docs
```

## Local Development

### Backend

```bash
cd backend

# Create virtual env
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and edit env file
cp .env.example .env

# Run the API server (needs a running PostgreSQL)
uvicorn app.main:app --reload
```

API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend

npm install
npm run dev
```

App will be available at `http://localhost:5173`.

## Project Structure

```
TuxPlanner/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app + CORS + router registration
│   │   ├── config.py        # Settings (DATABASE_URL)
│   │   ├── database.py      # SQLAlchemy engine + session
│   │   ├── models.py        # ORM models: Event, Todo
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   └── routers/
│   │       ├── events.py    # CRUD /api/events/
│   │       └── todos.py     # CRUD /api/todos/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue           # Root layout
│   │   ├── main.js
│   │   ├── plugins/
│   │   │   └── vuetify.js    # Vuetify + theme config
│   │   ├── api/
│   │   │   └── index.js      # Axios wrappers for events & todos
│   │   └── components/
│   │       ├── CalendarView.vue  # FullCalendar wrapper
│   │       ├── Sidebar.vue       # Navigation drawer
│   │       ├── TodayPanel.vue    # Today date + stats
│   │       ├── EventDialog.vue   # Add/edit event modal
│   │       └── TodoDialog.vue    # Add todo modal
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
└── docker-compose.yml
```
