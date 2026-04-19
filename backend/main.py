import os
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship, session, declarative_base
from prometheus_fastapi_instrumentator import Instrumentator

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/autoservice")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    cars = relationship("Car", back_populates="client")


class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    brand = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    vin = Column(String(17), nullable=False, unique=True)
    client = relationship("Client", back_populates="cars")
    work_orders = relationship("WorkOrder", back_populates="car")


class WorkOrder(Base):
    __tablename__ = "work_orders"
    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    description = Column(String(500), nullable=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    car = relationship("Car", back_populates="work_orders")


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="AutoService Pro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)


class ClientCreate(BaseModel):
    name: str
    phone: str
    email: EmailStr


class ClientResponse(ClientCreate):
    id: int
    cars: List["CarResponse"] = []

    class Config:
        from_attributes = True


class CarCreate(BaseModel):
    client_id: int
    brand: str
    model: str
    year: int
    vin: str


class CarResponse(CarCreate):
    id: int
    work_orders: List["WorkOrderResponse"] = []

    class Config:
        from_attributes = True


class WorkOrderCreate(BaseModel):
    car_id: int
    description: str
    status: str = "pending"


class WorkOrderResponse(WorkOrderCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


ClientResponse.model_rebuild()
CarResponse.model_rebuild()


@app.get("/")
def read_root():
    return {"message": "Привет! Бэкенд AutoService Pro успешно работает в WSL и передает данные!"}


@app.post("/clients", response_model=ClientResponse)
def create_client(client: ClientCreate, db: session = Depends(get_db)):
    db_client = Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


@app.get("/clients", response_model=List[ClientResponse])
def get_clients(db: session = Depends(get_db)):
    return db.query(Client).all()


@app.get("/clients/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db: session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@app.put("/clients/{client_id}", response_model=ClientResponse)
def update_client(client_id: int, client: ClientCreate, db: session = Depends(get_db)):
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    db_client.name = client.name
    db_client.phone = client.phone
    db_client.email = client.email
    db.commit()
    db.refresh(db_client)
    return db_client


@app.delete("/clients/{client_id}")
def delete_client(client_id: int, db: session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(client)
    db.commit()
    return {"message": "Client deleted"}


@app.post("/cars", response_model=CarResponse)
def create_car(car: CarCreate, db: session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == car.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    db_car = Car(**car.model_dump())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car


@app.get("/cars", response_model=List[CarResponse])
def get_cars(db: session = Depends(get_db)):
    return db.query(Car).all()


@app.get("/cars/{car_id}", response_model=CarResponse)
def get_car(car_id: int, db: session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


@app.put("/cars/{car_id}", response_model=CarResponse)
def update_car(car_id: int, car: CarCreate, db: session = Depends(get_db)):
    db_car = db.query(Car).filter(Car.id == car_id).first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Car not found")
    db_car.client_id = car.client_id
    db_car.brand = car.brand
    db_car.model = car.model
    db_car.year = car.year
    db_car.vin = car.vin
    db.commit()
    db.refresh(db_car)
    return db_car


@app.delete("/cars/{car_id}")
def delete_car(car_id: int, db: session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    db.delete(car)
    db.commit()
    return {"message": "Car deleted"}


@app.post("/work-orders", response_model=WorkOrderResponse)
def create_work_order(work_order: WorkOrderCreate, db: session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == work_order.car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    db_work_order = WorkOrder(**work_order.model_dump())
    db.add(db_work_order)
    db.commit()
    db.refresh(db_work_order)
    return db_work_order


@app.get("/work-orders", response_model=List[WorkOrderResponse])
def get_work_orders(db: session = Depends(get_db)):
    return db.query(WorkOrder).all()


@app.get("/work-orders/{work_order_id}", response_model=WorkOrderResponse)
def get_work_order(work_order_id: int, db: session = Depends(get_db)):
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    return work_order


@app.put("/work-orders/{work_order_id}", response_model=WorkOrderResponse)
def update_work_order(work_order_id: int, work_order: WorkOrderCreate, db: session = Depends(get_db)):
    db_work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not db_work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    db_work_order.car_id = work_order.car_id
    db_work_order.description = work_order.description
    db_work_order.status = work_order.status
    db.commit()
    db.refresh(db_work_order)
    return db_work_order


@app.delete("/work-orders/{work_order_id}")
def delete_work_order(work_order_id: int, db: session = Depends(get_db)):
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    db.delete(work_order)
    db.commit()
    return {"message": "Work order deleted"}