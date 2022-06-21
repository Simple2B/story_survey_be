from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: Optional[str]
    email: EmailStr
    image: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    # image_picture: Optional[Image]
    password: Optional[str]
    # provider: Optional[bool]
