from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.subscription_plan import SubscriptionPlan

router = APIRouter(prefix="/plans", tags=["Subscription Plans"])


@router.post("/create")
def create_plan(name: str, price: float, duration_days: int, db: Session = Depends(get_db)):
    plan = SubscriptionPlan(
        name=name,
        price=price,
        duration_days=duration_days
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)

    return plan


@router.get("/")
def list_plans(db: Session = Depends(get_db)):
    return db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).all()
