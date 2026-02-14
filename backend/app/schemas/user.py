from pydantic import BaseModel, EmailStr
from datetime import datetime

# For user registration
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# For login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Response model
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
