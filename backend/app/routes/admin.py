from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.store import Store
from app.models.subscription_plan import SubscriptionPlan
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin"])


# 🔐 Admin role check
def admin_only(user: User):
    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")


# ✅ Activate store manually
@router.post("/activate/{store_id}")
def activate_store(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    admin_only(current_user)

    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    store.is_active = True
    db.commit()

    return {"message": "Store activated"}


# ❌ Deactivate store
@router.post("/deactivate/{store_id}")
def deactivate_store(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    admin_only(current_user)

    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    store.is_active = False
    db.commit()

    return {"message": "Store deactivated"}


# 💼 Activate subscription using plan
@router.post("/activate-plan/{store_id}/{plan_id}")
def activate_plan(
    store_id: int,
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    admin_only(current_user)

    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    now = datetime.utcnow()

    store.subscription_plan_id = plan.id
    store.subscription_start = now
    store.subscription_end = now + timedelta(days=plan.duration_days)
    store.is_active = True

    db.commit()

    return {
        "message": "Plan activated successfully",
        "plan": plan.name,
        "valid_till": store.subscription_end,
    }
