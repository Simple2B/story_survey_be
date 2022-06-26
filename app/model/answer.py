from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    answer = Column(String(128), nullable=False)
    created_at = Column(DateTime(), default=datetime.now)

    question_id = Column(Integer, ForeignKey("questions.id"))

    question = relationship("Question")

    def __repr__(self) -> str:
        return f"<{self.id}: {self.answer} at {self.created_at}>"
