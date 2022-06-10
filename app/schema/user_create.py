from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: Optional[str]
    first_name: str
    last_name: str
    email: EmailStr
    password: str
