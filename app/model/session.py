from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String

from app.database import Base


class SessionNext(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)

    timestamp_session_start = Column(DateTime(), default=datetime.now)
    timestamp_session_end = Column(DateTime(), nullable=True)
    session = Column(String(256), nullable=False)

    def __repr__(self) -> str:
        return f"<{self.id}: user id {self.session}>"
