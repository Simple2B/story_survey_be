import enum
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserOut(BaseModel):
    id: int
    username: Optional[str]
    email: str
    created_at: datetime
    role: Optional[enum.Enum]
    image: Optional[str]

    class Config:
        orm_mode = True
