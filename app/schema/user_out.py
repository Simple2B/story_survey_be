from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserOut(BaseModel):
    id: int
    username: Optional[str]
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True
