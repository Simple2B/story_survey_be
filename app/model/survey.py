from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base
from app.model import question


class Survey(Base):
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True)
    title = Column(String(128), nullable=False)
    created_at = Column(DateTime(), default=datetime.now)
    published = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")

    question = relationship("Question", viewonly=True)

    def __repr__(self) -> str:
        return f"<{self.id}: {self.title} at {self.created_at}>"
