from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class SurveyBase(BaseModel):
    class Config:
        orm_mode = True


class SurveyCreate(SurveyBase):
    id: Optional[int]
    title: str
    description: Optional[str]
    successful_message: Optional[str]
    created_at: Optional[datetime]
    user_id: Optional[int]
    email: Optional[str]
    published: Optional[bool]
    questions: Optional[List]
    questions_deleted: Optional[List]
    create_question: Optional[List]


class Survey(SurveyBase):
    id: int
    uuid: Optional[str]
    title: str
    description: Optional[str]
    created_at: Optional[str]
    user_id: int
    email: Optional[str]
    questions: Optional[List]
    successful_message: Optional[str]
    published: Optional[bool]

class ServeysDataResult(BaseModel):
    data: list
    data_length: int


class SurveyReport(SurveyBase):
    uuid: int


class SurveyReportData(SurveyBase):
    title: Optional[str]
    description: Optional[str]
    created_at: Optional[str]
    published: Optional[bool]
    questions: Optional[List]
    answers: Optional[List]


class SurveyNextSession(SurveyBase):
    uuid: str
    session: str


class SurveyDelete(SurveyBase):
    survey_id: int
    email: Optional[str]
