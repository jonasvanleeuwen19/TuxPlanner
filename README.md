# TuxPlanner

The ULTIMATE self-hosted planner app, a personal calendar with todos and a daily overview.

<img width="1920" height="932" alt="image" src="https://github.com/user-attachments/assets/3feebc4e-0ca4-42f9-9ab1-a4c28c765606" />

## Stack

| Layer    | Technology                          |
|----------|-------------------------------------|
| Backend  | Python · FastAPI · SQLAlchemy       |
| Database | PostgreSQL                          |
| Frontend | Vue 3 · Vuetify 3 · FullCalendar 6  |

## Features

-  **FullCalendar** — month / week / day views, drag-and-drop events
-  **Sidebar** — Today panel (date, week number, day-of-year) + Todo list
-  **Todos** — create, complete, delete with optional due date
-  **Planning** Connect todo's as tasks to your calendar event and plan when you want to work on your task
-  **Events** — create, edit, delete, colour-code appointments
-  **Dark mode** toggle

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
