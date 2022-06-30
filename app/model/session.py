from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    timestamp_session_start = Column(DateTime())
    timestamp_session_end = Column(DateTime(), nullable=True)

    user = relationship("User")
    answer = relationship("Answer", viewonly=True)

    def __repr__(self) -> str:
        return f"<{self.id}: user id {self.user_id}>"
