from typing import Optional
from pydantic import BaseModel


class AnswerBase(BaseModel):
    class Config:
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
    survey_id: int
    created_at: str
