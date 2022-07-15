import enum
from datetime import datetime
from sqlalchemy import Enum
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    class SubscriptionType(enum.Enum):
        Basic = "Basic"
        Advance = "Advanced"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(), default=datetime.now)
    type = Column(Enum(SubscriptionType), default=SubscriptionType.Basic)
    customer_id = Column(String(512), nullable=True)
    session_id = Column(String(512), nullable=True)
    cancel_at = Column(DateTime(), nullable=True)
    cancel_at_period_end = Column(Boolean, nullable=True)
    subscription_id = Column(String(512), nullable=True)
    product_id = Column(String(512), nullable=True)

    user = relationship("User")

    def __repr__(self) -> str:
        return f"<{self.id}: customer id {self.customer_id}>"
