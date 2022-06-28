from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    question = Column(String(256), nullable=False)

    survey_id = Column(Integer, ForeignKey("surveys.id"))

    survey = relationship("Survey")

    # answer = relationship("Answer", viewonly=True)

    def __repr__(self) -> str:
        return f"<{self.id}: {self.question}>"
