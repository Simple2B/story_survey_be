import enum
from sqlalchemy import Enum
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Stripe(Base):
    __tablename__ = "stripe_data"

    class SubscriptionType(enum.Enum):
        Basic = "Basic"
        Advance = "Advance"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    customer_id = Column(String(256), nullable=True)
    session_id = Column(String(256), nullable=True)
    subscription = Column(Enum(SubscriptionType), nullable=True)
    subscription_id = Column(String(256), nullable=True)
    product_id = Column(String(256), nullable=True)

    user = relationship("User")

    def __repr__(self) -> str:
        return f"<{self.id}: customer id {self.stripe_customer_id}>"
