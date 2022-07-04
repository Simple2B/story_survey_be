import enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserOut(BaseModel):
    id: int
    username: Optional[str]
    email: str
    created_at: datetime
    role: Optional[enum.Enum]
    image: Optional[str]
    customer_id: Optional[str]
    session_id: Optional[str]
    subscription: Optional[enum.Enum]
    subscription_id: Optional[str]
    product_id: Optional[str]

    class Config:
        orm_mode = True
