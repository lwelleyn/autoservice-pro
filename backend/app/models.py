from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)

    cars = relationship("Car", back_populates="client", cascade="all, delete-orphan")


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    brand = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    vin = Column(String(17), nullable=False, unique=True)

    client = relationship("Client", back_populates="cars")
    work_orders = relationship("WorkOrder", back_populates="car", cascade="all, delete-orphan")


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id", ondelete="CASCADE"), nullable=False)
    description = Column(String(500), nullable=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), default=utcnow)

    car = relationship("Car", back_populates="work_orders")
