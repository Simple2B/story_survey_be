from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AnswerBase(BaseModel):
    orm_mode = True


class AnswerRequest(AnswerBase):
    question: str
    id: int
    survey_id: str


class AnswerCreate(AnswerBase):
    answer: str
    question: AnswerRequest
    email: Optional[str]


class Answer(AnswerBase):
    id: int
    answer: str
    question_id: int
    created_at: datetime
