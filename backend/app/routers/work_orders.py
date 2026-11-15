from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.routers.cars import get_car_or_404

router = APIRouter(prefix="/work-orders", tags=["work-orders"])


def get_work_order_or_404(db: Session, work_order_id: int) -> models.WorkOrder:
    work_order = db.get(models.WorkOrder, work_order_id)
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    return work_order


@router.post("", response_model=schemas.WorkOrderResponse)
def create_work_order(work_order: schemas.WorkOrderCreate, db: Session = Depends(get_db)):
    get_car_or_404(db, work_order.car_id)
    db_work_order = models.WorkOrder(**work_order.model_dump())
    db.add(db_work_order)
    db.commit()
    db.refresh(db_work_order)
    return db_work_order


@router.get("", response_model=list[schemas.WorkOrderResponse])
def get_work_orders(db: Session = Depends(get_db)):
    return db.query(models.WorkOrder).order_by(models.WorkOrder.id).all()


@router.get("/{work_order_id}", response_model=schemas.WorkOrderResponse)
def get_work_order(work_order_id: int, db: Session = Depends(get_db)):
    return get_work_order_or_404(db, work_order_id)


@router.put("/{work_order_id}", response_model=schemas.WorkOrderResponse)
def update_work_order(
    work_order_id: int, work_order: schemas.WorkOrderCreate, db: Session = Depends(get_db)
):
    db_work_order = get_work_order_or_404(db, work_order_id)
    get_car_or_404(db, work_order.car_id)
    db_work_order.car_id = work_order.car_id
    db_work_order.description = work_order.description
    db_work_order.status = work_order.status
    db.commit()
    db.refresh(db_work_order)
    return db_work_order


@router.delete("/{work_order_id}")
def delete_work_order(work_order_id: int, db: Session = Depends(get_db)):
    work_order = get_work_order_or_404(db, work_order_id)
    db.delete(work_order)
    db.commit()
    return {"message": "Work order deleted"}
