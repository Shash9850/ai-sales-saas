from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.conversation import Conversation
from app.utils.dependencies import get_current_user
from app.models.store import Store

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/leads")
def get_leads(db: Session = Depends(get_db),
              current_user = Depends(get_current_user)):

    store = db.query(Store).filter(Store.owner_id == current_user.id).first()

    if not store:
        return []

    leads = db.query(Conversation).filter(
        Conversation.store_id == store.id
    ).order_by(Conversation.created_at.desc()).all()

    return leads
