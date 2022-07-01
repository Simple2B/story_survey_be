from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship

from app.database import Base


class SessionNext(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)

    timestamp_session_start = Column(DateTime())
    timestamp_session_end = Column(DateTime(), nullable=True)
    session = Column(String(256), unique=True)

    def __repr__(self) -> str:
        return f"<{self.id}: user id {self.user_id}>"
