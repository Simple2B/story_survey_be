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
    stripe_data: Optional[int]

    class Config:
        orm_mode = True
