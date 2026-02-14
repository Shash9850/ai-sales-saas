from pydantic import BaseModel
from datetime import datetime

class StoreCreate(BaseModel):
    name: str
    description: str | None = None

class StoreResponse(BaseModel):
    id: int
    name: str
    description: str | None
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True
