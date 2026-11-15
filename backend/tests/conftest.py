import os

# Must be set before the app is imported: settings are read at import time.
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# One shared in-memory SQLite database (StaticPool keeps a single connection).
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def _enable_foreign_keys(dbapi_connection, _record):
    # SQLite ignores foreign keys unless asked; Postgres always enforces them.
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    """TestClient backed by a fresh, empty database for every test."""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


CLIENT = {"name": "Ivan Petrov", "phone": "+79990001122", "email": "ivan@example.com"}
VIN = "1HGCM82633A004352"
OTHER_VIN = "JH4KA8260MC000001"


@pytest.fixture()
def make_client(client):
    def _make(**overrides):
        response = client.post("/clients", json={**CLIENT, **overrides})
        assert response.status_code == 200, response.text
        return response.json()

    return _make


@pytest.fixture()
def make_car(client, make_client):
    def _make(client_id=None, **overrides):
        if client_id is None:
            client_id = make_client()["id"]
        payload = {
            "client_id": client_id,
            "brand": "Honda",
            "model": "Accord",
            "year": 2003,
            "vin": VIN,
            **overrides,
        }
        response = client.post("/cars", json=payload)
        assert response.status_code == 200, response.text
        return response.json()

    return _make


@pytest.fixture()
def make_work_order(client, make_car):
    def _make(car_id=None, **overrides):
        if car_id is None:
            car_id = make_car()["id"]
        payload = {"car_id": car_id, "description": "Oil change", **overrides}
        response = client.post("/work-orders", json=payload)
        assert response.status_code == 200, response.text
        return response.json()

    return _make
