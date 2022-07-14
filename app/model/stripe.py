import enum
from sqlalchemy import Enum
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class Stripe(Base):
    __tablename__ = "stripe_data"

    class SubscriptionType(enum.Enum):
        Basic = "Basic"
        Advance = "Advance"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    customer_id = Column(String(628), nullable=True)
    session_id = Column(String(628), nullable=True)
    subscription = Column(Enum(SubscriptionType), nullable=True)
    cancel_at_period_end = Column(Boolean, nullable=True)
    subscription_id = Column(String(628), nullable=True)
    product_id = Column(String(628), nullable=True)

    user = relationship("User")

    def __repr__(self) -> str:
        return f"<{self.id}: customer id {self.customer_id}>"
