"""FastAPI application entry point.

Wires CORS and health now; routers and DB seeding are added in later tasks.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import init_db
from app.routers import chat, tickets

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="North Star Support Bot", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat.router)
app.include_router(tickets.router)


@app.get("/health")
def health() -> dict[str, str]:
    from app.config import current_mode

    return {"status": "ok", "mode": current_mode()}
