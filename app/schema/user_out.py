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
    stripe_customer: Optional[str]
    stripe_session_id: Optional[str]
    subscription: Optional[enum.Enum]

    class Config:
        orm_mode = True
