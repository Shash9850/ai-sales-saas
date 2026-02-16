

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"))
    customer_message = Column(Text)
    ai_response = Column(Text)

    intent = Column(String, nullable=True)
    mentioned_product = Column(String, nullable=True)
    lead_score = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())



