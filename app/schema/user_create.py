from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: Optional[str]
    email: str
    image: Optional[str]
    # image_picture: Optional[Image]
    password: Optional[str]
    # provider: Optional[bool]
