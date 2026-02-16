from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.db.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship



class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 🔗 Relationship
    owner = relationship("User", backref="store")

    # 📧 Contact
    email = Column(String, nullable=True)
    whatsapp_number = Column(String, unique=True, nullable=True)

    # 💰 Subscription System
    is_active = Column(Boolean, default=True)
    subscription_plan = Column(String, nullable=True)
    subscription_start = Column(DateTime, default=datetime.utcnow)
    subscription_end = Column(DateTime, nullable=True)
    subscription_plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=True)
    subscription_plan = relationship("SubscriptionPlan")

