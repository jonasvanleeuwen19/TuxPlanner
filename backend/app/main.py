from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import events, todos
from app.routers import ical_feeds
from app.scheduler import start_scheduler, stop_scheduler

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="TuxPlanner API",
    description="Backend API for the TuxPlanner self-hosted calendar app",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, prefix="/api")
app.include_router(todos.router, prefix="/api")
app.include_router(ical_feeds.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "TuxPlanner API is running", "docs": "/docs"}
