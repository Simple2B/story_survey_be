from typing import List, Optional
from pydantic import BaseModel


class QuestionBase(BaseModel):
    class Config:
        orm_mode = True


class QuestionCreate(QuestionBase):
    question: str
    survey_id: int


class Question(QuestionBase):
    id: int
    question: str
    survey_id: int
    answers: Optional[List]
