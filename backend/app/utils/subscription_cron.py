from datetime import datetime
from app.db.database import SessionLocal
from app.models.store import Store

def auto_disable_expired_stores():
    db = SessionLocal()
    now = datetime.utcnow()

    stores = db.query(Store).filter(
        Store.subscription_end != None,
        Store.subscription_end < now,
        Store.is_active == True
    ).all()

    for store in stores:
        store.is_active = False

    db.commit()
    db.close()
