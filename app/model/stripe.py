import enum
from sqlalchemy import Enum
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Stripe(Base):
    __tablename__ = "stripe_data"

    class SubscriptionType(enum.Enum):
        Basic = "Basic"
        Advance = "Advance"

    id = Column(Integer, primary_key=True)

    stripe_customer_id = Column(String(256), nullable=True)
    stripe_session_id = Column(String(256), nullable=True)
    subscription = Column(Enum(SubscriptionType), nullable=True)

    user = relationship("User", viewonly=True)

    def __repr__(self) -> str:
        return f"<{self.id}: customer id {self.stripe_customer_id}>"
