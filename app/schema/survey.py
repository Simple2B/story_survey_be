from pydantic import BaseModel
from datetime import datetime


class SurveyBase(BaseModel):
    class Config:
        orm_mode = True


class SurveyCreate(SurveyBase):
    title: str
    created_at: datetime
    user_id: int


class Survey(SurveyBase):
    id: int
    title: str
    created_at: datetime
    user_id: int
