from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    email: EmailStr
    password: str
