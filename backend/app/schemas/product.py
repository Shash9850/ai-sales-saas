from pydantic import BaseModel
from datetime import datetime

class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    stock_quantity: int

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    stock_quantity: int
    is_available: bool
    store_id: int
    created_at: datetime

    class Config:
        from_attributes = True
