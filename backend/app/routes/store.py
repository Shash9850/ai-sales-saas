from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.store import Store
from app.schemas.store import StoreCreate, StoreResponse
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/store", tags=["Store"])


@router.post("/create", response_model=StoreResponse)
def create_store(
    store: StoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if user already has a store
    existing_store = db.query(Store).filter(Store.owner_id == current_user.id).first()
    if existing_store:
        raise HTTPException(status_code=400, detail="Store already exists for this user")

    new_store = Store(
        name=store.name,
        description=store.description,
        owner_id=current_user.id
    )

    db.add(new_store)
    db.commit()
    db.refresh(new_store)

    return new_store


from app.models.conversation import Conversation
from typing import List


@router.get("/my-conversations")
def get_store_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    store = db.query(Store).filter(Store.owner_id == current_user.id).first()

    if not store:
        raise HTTPException(status_code=400, detail="No store found")

    conversations = db.query(Conversation)\
        .filter(Conversation.store_id == store.id)\
        .order_by(Conversation.created_at.desc())\
        .all()

    return conversations



from sqlalchemy import func
from datetime import datetime, date


@router.get("/analytics")
def get_store_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    store = db.query(Store).filter(Store.owner_id == current_user.id).first()

    if not store:
        raise HTTPException(status_code=400, detail="No store found")

    total_conversations = db.query(Conversation)\
        .filter(Conversation.store_id == store.id)\
        .count()

    today = date.today()

    today_conversations = db.query(Conversation)\
        .filter(
            Conversation.store_id == store.id,
            func.date(Conversation.created_at) == today
        )\
        .count()

    latest_chat = db.query(Conversation)\
        .filter(Conversation.store_id == store.id)\
        .order_by(Conversation.created_at.desc())\
        .first()

    return {
        "store_name": store.name,
        "total_conversations": total_conversations,
        "today_conversations": today_conversations,
        "most_recent_chat_time": latest_chat.created_at if latest_chat else None
    }
