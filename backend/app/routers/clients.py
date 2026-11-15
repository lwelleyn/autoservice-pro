from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/clients", tags=["clients"])


def get_client_or_404(db: Session, client_id: int) -> models.Client:
    client = db.get(models.Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.post("", response_model=schemas.ClientResponse)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    db_client = models.Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


@router.get("", response_model=list[schemas.ClientResponse])
def get_clients(db: Session = Depends(get_db)):
    return db.query(models.Client).order_by(models.Client.id).all()


@router.get("/{client_id}", response_model=schemas.ClientDetailResponse)
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = (
        db.query(models.Client)
        .options(selectinload(models.Client.cars).selectinload(models.Car.work_orders))
        .filter(models.Client.id == client_id)
        .first()
    )
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.put("/{client_id}", response_model=schemas.ClientResponse)
def update_client(client_id: int, client: schemas.ClientCreate, db: Session = Depends(get_db)):
    db_client = get_client_or_404(db, client_id)
    db_client.name = client.name
    db_client.phone = client.phone
    db_client.email = client.email
    db.commit()
    db.refresh(db_client)
    return db_client


@router.delete("/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client = get_client_or_404(db, client_id)
    db.delete(client)  # cascades to the client's cars and their work orders
    db.commit()
    return {"message": "Client deleted"}
