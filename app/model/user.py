from uuid import uuid4
from datetime import datetime
import enum
from sqlalchemy import Enum
from sqlalchemy import Column, Integer, String, DateTime, func, or_
from sqlalchemy.orm import relationship

from app.hash_utils import make_hash, hash_verify
from app.database import Base, SessionLocal


def gen_uuid() -> str:
    return str(uuid4())


class User(Base):
    __tablename__ = "users"

    class UserRole(enum.Enum):
        Admin = "Admin"
        Client = "Client"
        Anonymous = "Anonymous"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), default=gen_uuid)
    created_at = Column(DateTime(), default=datetime.now)

    first_name = Column(String(64), nullable=True)
    last_name = Column(String(64), nullable=True)
    username = Column(String(64), nullable=False)

    email = Column(String(128), nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False)

    role = Column(Enum(UserRole), default=UserRole.Anonymous)

    # survey = relationship("Survey", viewonly=True)

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, value: str):
        self.password_hash = make_hash(value)

    @classmethod
    def authenticate(cls, db: SessionLocal, user_id: str, password: str):
        user = (
            db.query(cls)
            .filter(
                or_(
                    func.lower(cls.username) == func.lower(user_id),
                    func.lower(cls.email) == func.lower(user_id),
                )
            )
            .first()
        )
        if user is not None and hash_verify(password, user.password):
            return user

    def __repr__(self):
        return f"<{self.id}: {self.username}>"
