from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app import models, schemas
from app.database import get_db
from app.routers.clients import get_client_or_404

router = APIRouter(prefix="/cars", tags=["cars"])


def get_car_or_404(db: Session, car_id: int) -> models.Car:
    car = db.get(models.Car, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


def vin_conflict(vin: str) -> HTTPException:
    return HTTPException(status_code=409, detail=f"Car with VIN {vin} already exists")


def ensure_vin_is_free(db: Session, vin: str, exclude_car_id: int | None = None) -> None:
    query = db.query(models.Car).filter(models.Car.vin == vin)
    if exclude_car_id is not None:
        query = query.filter(models.Car.id != exclude_car_id)
    if query.first():
        raise vin_conflict(vin)


def commit_car(db: Session, vin: str) -> None:
    """Commit, turning a lost race on the unique VIN index into a 409."""
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise vin_conflict(vin) from None


@router.post("", response_model=schemas.CarResponse)
def create_car(car: schemas.CarCreate, db: Session = Depends(get_db)):
    get_client_or_404(db, car.client_id)
    ensure_vin_is_free(db, car.vin)
    db_car = models.Car(**car.model_dump())
    db.add(db_car)
    commit_car(db, car.vin)
    db.refresh(db_car)
    return db_car


@router.get("", response_model=list[schemas.CarResponse])
def get_cars(db: Session = Depends(get_db)):
    return db.query(models.Car).order_by(models.Car.id).all()


@router.get("/{car_id}", response_model=schemas.CarDetailResponse)
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = (
        db.query(models.Car)
        .options(selectinload(models.Car.work_orders))
        .filter(models.Car.id == car_id)
        .first()
    )
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


@router.put("/{car_id}", response_model=schemas.CarResponse)
def update_car(car_id: int, car: schemas.CarCreate, db: Session = Depends(get_db)):
    db_car = get_car_or_404(db, car_id)
    get_client_or_404(db, car.client_id)
    ensure_vin_is_free(db, car.vin, exclude_car_id=car_id)
    db_car.client_id = car.client_id
    db_car.brand = car.brand
    db_car.model = car.model
    db_car.year = car.year
    db_car.vin = car.vin
    commit_car(db, car.vin)
    db.refresh(db_car)
    return db_car


@router.delete("/{car_id}")
def delete_car(car_id: int, db: Session = Depends(get_db)):
    car = get_car_or_404(db, car_id)
    db.delete(car)  # cascades to the car's work orders
    db.commit()
    return {"message": "Car deleted"}
