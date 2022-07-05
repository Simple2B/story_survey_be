from typing import Optional, List
from pydantic import BaseModel
from app import schema


class History(BaseModel):
    users: Optional[List[schema.UserOut]]

    class Config:
        orm_mode = True
