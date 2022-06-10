from datetime import datetime
from pydantic import BaseModel


class AnswerBase(BaseModel):
    orm_mode = True


class AnswerCreate(AnswerBase):
    answer: str
    question_id: int


class Answer(AnswerBase):
    id: int
    answer: str
    question_id: int
    created_at: datetime
