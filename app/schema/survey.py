from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class SurveyBase(BaseModel):
    class Config:
        orm_mode = True


class SurveyCreate(SurveyBase):
    title: str
    description: Optional[str]
    created_at: Optional[datetime]
    user_id: Optional[int]
    email: Optional[str]
    questions: Optional[List]


class Survey(SurveyBase):
    id: int
    uuid: Optional[str]
    title: str
    description: Optional[str]
    created_at: Optional[str]
    user_id: int
    email: Optional[str]
    questions: Optional[List]


class SurveyDelete(SurveyBase):
    survey_id: int
    email: Optional[str]
