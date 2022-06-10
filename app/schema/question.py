from pydantic import BaseModel
from datetime import datetime
from .user_out import UserOut


class QuestionBase(BaseModel):
    orm_mode = True


class QuestionCreate(QuestionBase):
    question: str
    survey_id: int


class Question(QuestionBase):
    id: int
    question: str
    survey_id: int
