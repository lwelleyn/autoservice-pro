from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.routers import cars, clients, work_orders

# The database schema is managed by Alembic (see backend/alembic/):
# run `alembic upgrade head` before starting the app.

app = FastAPI(title="AutoService Pro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Keep probes and scrapes out of the request metrics.
Instrumentator(excluded_handlers=["/metrics", "/health"]).instrument(app).expose(app)

app.include_router(clients.router)
app.include_router(cars.router)
app.include_router(work_orders.router)


@app.get("/")
def read_root():
    return {"message": "Привет! Бэкенд AutoService Pro успешно работает в WSL и передает данные!"}


@app.get("/health", tags=["service"])
def health(db: Session = Depends(get_db)):
    """Liveness + database connectivity check, used by the Docker healthcheck."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database is unavailable") from None
    return {"status": "ok"}
